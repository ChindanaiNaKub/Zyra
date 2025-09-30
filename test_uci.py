#!/usr/bin/env python3
"""
UCI Conformance Testing Script for Zyra Chess Engine

This script tests the UCI protocol implementation by sending commands
and validating responses. It can be used as an alternative to GUI testing
when Cute Chess or Arena are not available.
"""

import os
import signal
import subprocess
import sys
import time
from typing import List, Optional, Tuple


class UCITester:
    """Test UCI protocol conformance."""

    def __init__(self, engine_path: str = None):
        """Initialize tester with engine path."""
        if engine_path is None:
            # Try to find the engine
            if os.path.exists("interfaces/uci.py"):
                self.engine_path = [sys.executable, "-m", "interfaces.uci"]
            elif os.path.exists("zyra/interfaces/uci.py"):
                self.engine_path = [sys.executable, "-m", "zyra.interfaces.uci"]
            else:
                self.engine_path = ["zyra-uci"]  # Assume installed
        else:
            self.engine_path = engine_path.split()

        self.process = None
        self.test_results = []

    def start_engine(self) -> bool:
        """Start the UCI engine process."""
        try:
            print(f"Starting engine: {' '.join(self.engine_path)}")
            self.process = subprocess.Popen(
                self.engine_path,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            time.sleep(0.1)  # Give engine time to start
            return True
        except Exception as e:
            print(f"Failed to start engine: {e}")
            return False

    def send_command(self, command: str, timeout: float = 5.0) -> Tuple[bool, str]:
        """Send a command to the engine and get response."""
        if not self.process:
            return False, "Engine not started"

        try:
            print(f"Sending: {command}")
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()

            # Read response with timeout
            start_time = time.time()
            response_lines = []

            while time.time() - start_time < timeout:
                try:
                    # Use select to check if data is available
                    import select

                    if select.select([self.process.stdout], [], [], 0.1)[0]:
                        line = self.process.stdout.readline()
                        if line:
                            response_lines.append(line.strip())
                            print(f"Received: {line.strip()}")

                            # Check if this looks like a complete response
                            if any(
                                keyword in line.lower()
                                for keyword in ["uciok", "readyok", "bestmove", "info"]
                            ):
                                break
                        else:
                            break
                    else:
                        time.sleep(0.01)
                except:
                    time.sleep(0.01)

            response = "\n".join(response_lines)
            return True, response

        except Exception as e:
            return False, f"Error sending command: {e}"

    def test_basic_commands(self) -> bool:
        """Test basic UCI commands."""
        print("\n=== Testing Basic UCI Commands ===")

        tests = [
            ("uci", "uciok"),
            ("isready", "readyok"),
            ("ucinewgame", None),  # No specific response expected
            ("position startpos", None),
            ("go movetime 1000", "bestmove"),
            ("quit", None),
        ]

        all_passed = True

        for command, expected in tests:
            print(f"\nTesting: {command}")
            success, response = self.send_command(command)

            if not success:
                print(f"❌ FAILED: {response}")
                all_passed = False
                continue

            if expected is None:
                print(f"✅ PASSED: {command} (no specific response expected)")
            elif expected in response.lower():
                print(f"✅ PASSED: {command} - found '{expected}' in response")
            else:
                print(f"❌ FAILED: {command} - expected '{expected}', got: {response}")
                all_passed = False

        return all_passed

    def test_position_commands(self) -> bool:
        """Test position setup commands."""
        print("\n=== Testing Position Commands ===")

        # Reset engine
        self.send_command("ucinewgame")

        tests = [
            ("position startpos", None),
            ("position startpos moves e2e4", None),
            ("position fen rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", None),
            ("go movetime 500", "bestmove"),
        ]

        all_passed = True

        for command, expected in tests:
            print(f"\nTesting: {command}")
            success, response = self.send_command(command)

            if not success:
                print(f"❌ FAILED: {response}")
                all_passed = False
                continue

            if expected is None:
                print(f"✅ PASSED: {command}")
            elif expected in response.lower():
                print(f"✅ PASSED: {command} - found '{expected}' in response")
            else:
                print(f"❌ FAILED: {command} - expected '{expected}', got: {response}")
                all_passed = False

        return all_passed

    def test_search_commands(self) -> bool:
        """Test search and go commands."""
        print("\n=== Testing Search Commands ===")

        # Reset engine
        self.send_command("ucinewgame")
        self.send_command("position startpos")

        tests = [
            ("go movetime 100", "bestmove"),
            ("go nodes 100", "bestmove"),
            ("go depth 3", "bestmove"),  # Should work but log warning
        ]

        all_passed = True

        for command, expected in tests:
            print(f"\nTesting: {command}")
            success, response = self.send_command(command, timeout=10.0)

            if not success:
                print(f"❌ FAILED: {response}")
                all_passed = False
                continue

            if expected in response.lower():
                print(f"✅ PASSED: {command} - found '{expected}' in response")
            else:
                print(f"❌ FAILED: {command} - expected '{expected}', got: {response}")
                all_passed = False

        return all_passed

    def test_stability(self, num_games: int = 3) -> bool:
        """Test engine stability with multiple games."""
        print(f"\n=== Testing Stability ({num_games} games) ===")

        all_passed = True

        for game_num in range(1, num_games + 1):
            print(f"\nGame {game_num}:")

            # Reset for new game
            self.send_command("ucinewgame")
            self.send_command("position startpos")

            # Play a few moves
            for move_num in range(1, 6):  # 5 moves per side = 10 half-moves
                print(f"  Move {move_num}:")
                success, response = self.send_command("go movetime 200", timeout=5.0)

                if not success or "bestmove" not in response.lower():
                    print(f"❌ FAILED: Game {game_num}, Move {move_num} - {response}")
                    all_passed = False
                    break

                # Extract move and apply it
                if "bestmove" in response.lower():
                    move_line = [
                        line for line in response.split("\n") if "bestmove" in line.lower()
                    ]
                    if move_line:
                        move = move_line[0].split()[-1]
                        print(f"    Engine played: {move}")
                        self.send_command(f"position startpos moves {move}")
                    else:
                        print(f"❌ FAILED: Could not extract move from: {response}")
                        all_passed = False
                        break
                else:
                    print(f"❌ FAILED: No bestmove in response: {response}")
                    all_passed = False
                    break
            else:
                print(f"✅ PASSED: Game {game_num} completed successfully")

        return all_passed

    def cleanup(self):
        """Clean up the engine process."""
        if self.process:
            try:
                self.process.stdin.write("quit\n")
                self.process.stdin.flush()
                self.process.wait(timeout=2)
            except:
                self.process.terminate()
            finally:
                self.process = None

    def run_all_tests(self) -> bool:
        """Run all UCI conformance tests."""
        print("Starting UCI Conformance Testing for Zyra Chess Engine")
        print("=" * 60)

        if not self.start_engine():
            return False

        try:
            # Run test suites
            basic_ok = self.test_basic_commands()
            position_ok = self.test_position_commands()
            search_ok = self.test_search_commands()
            stability_ok = self.test_stability(3)

            # Summary
            print("\n" + "=" * 60)
            print("TEST SUMMARY:")
            print(f"Basic Commands: {'✅ PASSED' if basic_ok else '❌ FAILED'}")
            print(f"Position Commands: {'✅ PASSED' if position_ok else '❌ FAILED'}")
            print(f"Search Commands: {'✅ PASSED' if search_ok else '❌ FAILED'}")
            print(f"Stability Tests: {'✅ PASSED' if stability_ok else '❌ FAILED'}")

            all_passed = basic_ok and position_ok and search_ok and stability_ok
            print(
                f"\nOverall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}"
            )

            return all_passed

        finally:
            self.cleanup()


def main():
    """Main testing function."""
    import argparse

    parser = argparse.ArgumentParser(description="Test UCI conformance for Zyra chess engine")
    parser.add_argument("--engine", help="Path to engine executable")
    parser.add_argument("--games", type=int, default=3, help="Number of stability test games")
    args = parser.parse_args()

    tester = UCITester(args.engine)

    # Override stability test if games specified
    if args.games != 3:
        original_stability = tester.test_stability
        tester.test_stability = lambda: original_stability(args.games)

    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
