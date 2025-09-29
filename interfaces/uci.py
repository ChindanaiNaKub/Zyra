"""UCI protocol implementation.

This module provides UCI protocol support for communication with
chess GUIs like Cute Chess and Arena.
"""

import sys
from typing import List, Optional


class UCIEngine:
    """UCI protocol engine interface."""

    def __init__(self) -> None:
        """Initialize UCI engine."""
        self.position = None
        self.search_engine = None

    def handle_command(self, command: str) -> Optional[str]:
        """Handle UCI protocol commands."""
        parts = command.strip().split()

        if not parts:
            return None

        cmd = parts[0].lower()

        if cmd == "uci":
            return "uciok"
        elif cmd == "isready":
            return "readyok"
        elif cmd == "quit":
            sys.exit(0)

        return None

    def run_uci_loop(self) -> None:
        """Main UCI protocol loop."""
        while True:
            try:
                command = input().strip()
                response = self.handle_command(command)
                if response:
                    print(response)
            except EOFError:
                break
