#!/usr/bin/env python3
"""Debug UCI to see what Lucas Chess sends"""
import sys

print("id name Zyra Debug", flush=True)
print("id author Zyra", flush=True)
print("uciok", flush=True)

while True:
    try:
        line = input().strip()
        # Log to stderr so we can see it
        print(f"DEBUG: Received: {line}", file=sys.stderr, flush=True)

        if line == "quit":
            break
        elif line == "uci":
            print("id name Zyra Debug", flush=True)
            print("id author Zyra", flush=True)
            print("uciok", flush=True)
        elif line == "isready":
            print("readyok", flush=True)
        elif line.startswith("position"):
            print(f"DEBUG: Position command: {line}", file=sys.stderr, flush=True)
            pass  # Accept position
        elif line.startswith("go"):
            print(f"DEBUG: Go command received: {line}", file=sys.stderr, flush=True)
            print("bestmove e2e4", flush=True)
        elif line == "ucinewgame":
            pass
    except EOFError:
        break
