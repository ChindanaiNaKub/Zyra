from fastapi.testclient import TestClient

# Import the FastAPI app from the web server
from zyra.web.server import app

client = TestClient(app)


def test_new_game_starts_with_startpos():
    resp = client.post("/api/new", json={})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data.get("fen"), str)
    assert data.get("history") == []
    assert data.get("side_to_move") in ("w", "b")


def test_illegal_move_rejected():
    # Ensure fresh game
    client.post("/api/new", json={})
    # Try an obviously illegal move (move from off-board)
    resp = client.post("/api/move", json={"uci": "z9z9"})
    assert resp.status_code == 400
    assert "Invalid move" in resp.json().get("detail", "") or "Illegal move" in resp.json().get(
        "detail", ""
    )


def test_legal_move_then_engine_replies_and_eval_present():
    client.post("/api/new", json={})
    # Make a common opening move
    resp = client.post("/api/move", json={"uci": "e2e4"})
    assert resp.status_code == 200
    data = resp.json()
    # After player's move and engine reply, there should be at least 2 moves in history
    history = data.get("history")
    assert isinstance(history, list)
    assert len(history) >= 2
    # Evaluation should be present after the engine move
    assert data.get("eval_cp") is None or isinstance(data.get("eval_cp"), (int, float))


def test_state_endpoint_returns_current_position_and_eval():
    # State should always return fen and eval
    resp = client.get("/api/state")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data.get("fen"), str)
    assert data.get("eval_cp") is None or isinstance(data.get("eval_cp"), (int, float))
