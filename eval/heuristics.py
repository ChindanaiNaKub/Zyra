"""Position evaluation heuristics.

This module contains explainable evaluation functions for material,
positional factors, and style-based weights.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple

# -------------------- Utility Data --------------------
PIECE_VALUES: Dict[str, int] = {
    "p": 100,
    "n": 320,
    "b": 330,
    "r": 500,
    "q": 900,
    # Kings are not scored directly as material; handled in king safety
}

CENTER_SQUARES_0X88: List[int] = []  # Filled lazily to avoid import loops


def _lazy_init_center() -> None:
    global CENTER_SQUARES_0X88
    if CENTER_SQUARES_0X88:
        return
    # Late import to avoid circular import at module load
    from core.board import square_to_index

    CENTER_SQUARES_0X88 = [
        square_to_index("d4"),
        square_to_index("e4"),
        square_to_index("d5"),
        square_to_index("e5"),
    ]


def _is_offboard(index: int) -> bool:
    return (index & 0x88) != 0


def _is_white(piece: str) -> bool:
    return piece.isupper()


def _file_of(index: int) -> int:
    return index & 0x7


def _rank_of(index: int) -> int:
    return (index >> 4) & 0x7


class EvaluationResult:
    """Container for evaluation totals and explainable breakdown."""

    def __init__(self, total: float, breakdown: Dict[str, float], style_applied: Dict[str, float]):
        self.total = total
        self.breakdown = breakdown
        self.style_applied = style_applied


class Evaluation:
    """Chess position evaluator with explainable heuristics."""

    def __init__(
        self,
        style_weights: Optional[Dict[str, float]] = None,
        logger: Optional[Callable[[str], None]] = None,
    ) -> None:
        """Initialize evaluator with optional style weights.

        Scores are centipawns from White's perspective (positive favors White).
        """
        self.style_weights = style_weights or {}
        self._logger: Optional[Callable[[str], None]] = logger
        self._log_buffer: List[str] = []

    def _log(self, msg: str) -> None:
        if self._logger is not None:
            try:
                self._logger(msg)
            except Exception:
                pass
        self._log_buffer.append(msg)
        if len(self._log_buffer) > 100:
            self._log_buffer.pop(0)

    # -------------------- Public API --------------------
    def evaluate(self, position: Any) -> float:
        """Evaluate a chess position and return score in centipawns.

        Positive scores favor White. Negative scores favor Black.
        """
        result = self._evaluate_internal(position)
        return result.total

    def explain_evaluation(self, position: Any) -> Dict[str, Any]:
        """Return breakdown of evaluation components and applied weights."""
        result = self._evaluate_internal(position)
        return {
            "total": result.total,
            "terms": result.breakdown,
            "style_weights": result.style_applied,
            "log": list(self._log_buffer),
        }

    # -------------------- Internal Implementation --------------------
    def _evaluate_internal(self, position: Any) -> EvaluationResult:
        _lazy_init_center()

        material_cp = self._score_material(position)
        attacking_cp = self._score_attacking_motifs(position)
        center_cp = self._score_center_control(position)
        rook_files_cp = self._score_rook_files(position)
        mobility_cp = self._score_mobility(position)
        king_safety_cp = self._score_king_safety(position)
        initiative_cp = int(0.5 * mobility_cp)

        breakdown: Dict[str, float] = {
            "material": float(material_cp),
            "attacking_motifs": float(attacking_cp),
            "center_control": float(center_cp),
            "rook_files": float(rook_files_cp),
            "mobility": float(mobility_cp),
            "king_safety": float(king_safety_cp),
            "initiative": float(initiative_cp),
        }

        # Apply style weights
        style_weights = self.style_weights or {}
        total = 0.0
        for term, value in breakdown.items():
            weight = style_weights.get(term, 1.0)
            total += value * weight

        # logging
        self._log_buffer.clear()
        self._log(f"Evaluation terms: {breakdown}")
        self._log(f"Applied style weights: {style_weights}")
        self._log(f"Total score (cp): {total}")

        return EvaluationResult(total=total, breakdown=breakdown, style_applied=style_weights)

    # -------------------- Term Scorers --------------------
    def _score_material(self, position: Any) -> int:
        score = 0
        for idx in range(128):
            if _is_offboard(idx):
                continue
            piece = position.squares[idx]
            if piece == "\u0000":
                continue
            lower = piece.lower()
            if lower in PIECE_VALUES:
                val = PIECE_VALUES[lower]
                score += val if _is_white(piece) else -val
        return score

    def _score_attacking_motifs(self, position: Any) -> int:
        """Simple attacking/sacrificial motif bonuses.

        Bonuses when a piece attacks an enemy piece square. The bonus scales
        with the target piece value. If the attacker is en prise by a lower
        or equal valued enemy (crude sacrifice indicator), add a small extra.
        """
        from core.moves import _square_attacked_by  # type: ignore

        bonus = 0
        for idx in range(128):
            if _is_offboard(idx):
                continue
            piece = position.squares[idx]
            if piece == "\u0000" or piece.lower() == "k":
                continue
            is_white = _is_white(piece)

            # Scan target squares to detect direct attacks on enemy pieces by stepping rays/offsets
            lower = piece.lower()
            targets: List[int] = []
            if lower == "n":
                for off in [31, 33, 14, 18, -31, -33, -14, -18]:
                    t = idx + off
                    if not _is_offboard(t):
                        targets.append(t)
            elif lower in ("b", "r", "q"):
                directions = []
                if lower in ("b", "q"):
                    directions += [15, 17, -15, -17]
                if lower in ("r", "q"):
                    directions += [16, -16, 1, -1]
                for d in directions:
                    t = idx + d
                    while not _is_offboard(t):
                        targets.append(t)
                        if position.squares[t] != "\u0000":
                            break
                        t += d
            elif lower == "k":
                continue
            else:  # pawn
                for diag in (-15, -17) if is_white else (15, 17):
                    t = idx + diag
                    if not _is_offboard(t):
                        targets.append(t)

            for t in targets:
                tp = position.squares[t]
                if tp == "\u0000" or _is_white(tp) == is_white:
                    continue
                target_val = PIECE_VALUES.get(tp.lower(), 0)
                if target_val == 0:
                    continue
                base = max(5, target_val // 20)  # e.g., queen 45, rook 25, minor 16
                if is_white:
                    bonus += base
                else:
                    bonus -= base

                # crude sacrificial motif: attacker is attacked by opponent and target more valuable
                attacker_val = PIECE_VALUES.get(lower, 0)
                if target_val > attacker_val:
                    attacked = _square_attacked_by(position, idx, by_white=not is_white)
                    if attacked:
                        extra = max(3, (target_val - attacker_val) // 50)
                        if is_white:
                            bonus += extra
                        else:
                            bonus -= extra
        return bonus

    def _score_center_control(self, position: Any) -> int:
        # Count occupancy of the four central squares
        score = 0
        for sq in CENTER_SQUARES_0X88:
            piece = position.squares[sq]
            if piece == "\u0000":
                continue
            score += 10 if _is_white(piece) else -10
        return score

    def _score_rook_files(self, position: Any) -> int:
        # Bonus for rooks on open/semi-open files (no friendly/all pawns on file)
        score = 0
        for idx in range(128):
            if _is_offboard(idx):
                continue
            piece = position.squares[idx]
            if piece.lower() != "r":
                continue
            file_idx = _file_of(idx)
            has_white_pawn = False
            has_black_pawn = False
            # Scan the file
            for r in range(8):
                sq = (r << 4) | file_idx
                p = position.squares[sq]
                if p.lower() == "p":
                    if p.isupper():
                        has_white_pawn = True
                    else:
                        has_black_pawn = True
            bonus = 0
            if not has_white_pawn and not has_black_pawn:
                bonus = 15  # open file
            elif (not has_white_pawn and _is_white(piece)) or (
                not has_black_pawn and not _is_white(piece)
            ):
                bonus = 8  # semi-open for that side
            if _is_white(piece):
                score += bonus
            else:
                score -= bonus
        return score

    def _score_mobility(self, position: Any) -> int:
        # Simple mobility: number of legal moves difference
        from core.moves import generate_moves

        # Count white mobility
        original_side = position.side_to_move
        position.side_to_move = "w"
        white_moves = len(generate_moves(position))
        position.side_to_move = "b"
        black_moves = len(generate_moves(position))
        position.side_to_move = original_side
        return white_moves - black_moves

    def _score_king_safety(self, position: Any) -> int:
        # Basic king safety: pawn shield in front of king gets small bonus
        from core.moves import _locate_king  # type: ignore

        score = 0
        white_king = _locate_king(position, white=True)
        black_king = _locate_king(position, white=False)
        if white_king is not None:
            wr = _rank_of(white_king)
            wf = _file_of(white_king)
            # Check squares one rank in front of the king (towards rank 8 for White is -1 in our from_top metric)
            shield = 0
            for df in (-1, 0, 1):
                f = wf + df
                r = wr - 1
                if 0 <= f < 8 and 0 <= r < 8:
                    sq = (r << 4) | f
                    if position.squares[sq] == "P":
                        shield += 1
            score += shield * 8
        if black_king is not None:
            br = _rank_of(black_king)
            bf = _file_of(black_king)
            shield = 0
            for df in (-1, 0, 1):
                f = bf + df
                r = br + 1
                if 0 <= f < 8 and 0 <= r < 8:
                    sq = (r << 4) | f
                    if position.squares[sq] == "p":
                        shield += 1
            score -= shield * 8
        return score


def get_style_profile(profile_name: str) -> Dict[str, float]:
    """Get predefined style profile weights.

    Weights apply multiplicatively to evaluation terms.
    Known terms: material, attacking_motifs, center_control, rook_files, mobility, king_safety, initiative
    """
    profiles: Dict[str, Dict[str, float]] = {
        "aggressive": {
            "material": 1.0,
            "attacking_motifs": 1.3,
            "center_control": 1.1,
            "rook_files": 1.05,
            "mobility": 1.0,
            "king_safety": 1.0,
            "initiative": 1.0,
        },
        "defensive": {
            "material": 1.05,
            "center_control": 1.0,
            "rook_files": 1.0,
            "mobility": 0.95,
            "king_safety": 1.3,
            "attacking_motifs": 0.9,
            "initiative": 0.9,
        },
        "experimental": {
            "material": 0.95,
            "center_control": 1.05,
            "rook_files": 1.05,
            "mobility": 1.25,
            "king_safety": 0.9,
            "attacking_motifs": 1.2,
            "initiative": 1.1,
        },
    }
    return profiles.get(profile_name, {})


def parse_style_config(config: Optional[Dict[str, float] or str]) -> Dict[str, float]:
    """Parse style config which may be a profile name or a weights dict."""
    if config is None:
        return {}
    if isinstance(config, str):
        return get_style_profile(config)
    if isinstance(config, dict):
        return validate_style_weights(config)
    return {}


def validate_style_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """Validate and sanitize style weights dictionary.

    - Keeps only known terms
    - Coerces values to float when possible
    - Ignores invalid entries
    """
    known_terms = {
        "material",
        "attacking_motifs",
        "center_control",
        "rook_files",
        "mobility",
        "king_safety",
        "initiative",
    }
    sanitized: Dict[str, float] = {}
    for k, v in weights.items():
        if k not in known_terms:
            continue
        try:
            sanitized[k] = float(v)
        except (TypeError, ValueError):
            continue
    return sanitized


def set_style_profile(evaluator: Evaluation, style: Optional[Dict[str, float] or str]) -> None:
    """Update evaluator style at runtime."""
    evaluator.style_weights = parse_style_config(style)
    evaluator._log("Style profile updated")


def _noop(_: str) -> None:
    return None


def create_evaluator(
    style: Optional[Dict[str, float] or str] = None, logger: Optional[Callable[[str], None]] = None
) -> Evaluation:
    """Factory to create an Evaluation with parsed style and optional logger."""
    lw = parse_style_config(style)
    return Evaluation(style_weights=lw, logger=logger or _noop)


def _log_to_stdout(msg: str) -> None:
    print(msg)


def _log_debug_disabled(_: str) -> None:
    pass


def _should_log() -> bool:
    return False


def _safe_str(obj: Any) -> str:
    try:
        return str(obj)
    except Exception:
        return "<unprintable>"


def _discard_excess_logs(logs: List[str], max_entries: int = 100) -> List[str]:
    if len(logs) <= max_entries:
        return logs
    return logs[-max_entries:]


def _merge_logs(base: List[str], extra: List[str], max_entries: int = 100) -> List[str]:
    merged = base + extra
    return _discard_excess_logs(merged, max_entries)


def _format_term(name: str, value: float, weight: float) -> str:
    return f"{name}={value:.2f} x {weight:.2f}"


def _weighted_sum(terms: Dict[str, float], weights: Dict[str, float]) -> float:
    total = 0.0
    for t, v in terms.items():
        total += v * weights.get(t, 1.0)
    return total


def _clamp(value: float, min_v: float, max_v: float) -> float:
    return max(min_v, min(max_v, value))


def _sign(value: float) -> int:
    return (value > 0) - (value < 0)


def _abs(value: float) -> float:
    return -value if value < 0 else value


def _avg(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _median(values: List[float]) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return float(s[mid])
    return float((s[mid - 1] + s[mid]) / 2.0)


def _stddev(values: List[float]) -> float:
    if not values:
        return 0.0
    mean = _avg(values)
    var = _avg([(v - mean) ** 2 for v in values])
    return var**0.5


def _percent_diff(a: float, b: float) -> float:
    if a == 0:
        return 0.0
    return (b - a) / abs(a)


def _weighted_terms_str(terms: Dict[str, float], weights: Dict[str, float]) -> str:
    parts = [_format_term(k, terms[k], weights.get(k, 1.0)) for k in terms]
    return ", ".join(parts)


def _merge_dicts(a: Dict[str, float], b: Dict[str, float]) -> Dict[str, float]:
    c = dict(a)
    c.update(b)
    return c


def _minmax(values: List[float]) -> Tuple[float, float]:
    if not values:
        return 0.0, 0.0
    return min(values), max(values)


def _normalize_probs(values: List[float]) -> List[float]:
    s = sum(values)
    if s == 0:
        return [0.0 for _ in values]
    return [v / s for v in values]


def _softmax(values: List[float], temperature: float = 1.0) -> List[float]:
    if temperature <= 0:
        temperature = 1.0
    import math

    exps = [math.exp(v / temperature) for v in values]
    s = sum(exps)
    if s == 0:
        return [0.0 for _ in values]
    return [v / s for v in exps]


def _linmap(x: float, in_min: float, in_max: float, out_min: float, out_max: float) -> float:
    if in_max == in_min:
        return out_min
    return out_min + (x - in_min) * (out_max - out_min) / (in_max - in_min)


def _cummean(values: List[float]) -> List[float]:
    total = 0.0
    out: List[float] = []
    for i, v in enumerate(values, 1):
        total += v
        out.append(total / i)
    return out


def _percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = int(_clamp(p, 0.0, 1.0) * (len(s) - 1))
    return float(s[k])


def _quantize(value: float, step: float) -> float:
    if step <= 0:
        return value
    import math

    return math.floor(value / step + 0.5) * step


def _round2(value: float) -> float:
    return float(f"{value:.2f}")


def _as_cp(value: float) -> int:
    return int(round(value))


def _clip_cp(value: int, min_cp: int = -5000, max_cp: int = 5000) -> int:
    return max(min_cp, min(max_cp, value))


def _scale_cp(value: int, scale: float) -> int:
    return int(round(value * scale))


def _max_abs(values: List[float]) -> float:
    if not values:
        return 0.0
    return max(values, key=lambda x: _abs(x))


def _min_abs(values: List[float]) -> float:
    if not values:
        return 0.0
    return min(values, key=lambda x: _abs(x))


def _log_terms(terms: Dict[str, float], weights: Dict[str, float]) -> str:
    return _weighted_terms_str(terms, weights)


def _sum_dict_values(d: Dict[str, float]) -> float:
    return sum(d.values())


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _merge_breakdowns(a: Dict[str, float], b: Dict[str, float]) -> Dict[str, float]:
    c = dict(a)
    for k, v in b.items():
        c[k] = c.get(k, 0.0) + v
    return c


def _safe_get(d: Dict[str, float], key: str, default: float = 1.0) -> float:
    return float(d.get(key, default))


def _nonzero(value: float, eps: float = 1e-9) -> bool:
    return abs(value) > eps


def _bounded(value: float, low: float, high: float) -> bool:
    return low <= value <= high


def _mean_abs(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(abs(v) for v in values) / len(values)


def _log(self, msg: str) -> None:
    if self._logger is not None:
        try:
            self._logger(msg)
        except Exception:
            pass
    self._log_buffer.append(msg)
    if len(self._log_buffer) > 100:
        self._log_buffer.pop(0)


# ============================================================================
# PERFORMANCE OPTIMIZATION: Use optimized versions when available
# ============================================================================
try:
    from eval.heuristics_optimized import OptimizedEvaluation, quick_evaluate

    # Store standard version as backup
    _Evaluation_standard = Evaluation

    # Use optimized evaluation as default
    Evaluation = OptimizedEvaluation  # type: ignore

    __all__ = [
        "Evaluation",
        "OptimizedEvaluation",
        "quick_evaluate",
        "parse_style_config",
        "create_evaluator",
        "get_style_profile",
    ]

except ImportError:
    # Optimized version not available, use standard implementation
    __all__ = ["Evaluation", "parse_style_config", "create_evaluator", "get_style_profile"]
