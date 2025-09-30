#!/usr/bin/env python3
"""
Interactive UCI Testing Script

This script tests the UCI engine by running it interactively and sending
commands one by one, which is closer to how a real GUI would interact.
"""

import queue
import subprocess
import sys
import threading
import time


class UCITester:
    def __init__(self):
        self.process = None
        self.output_queue = queue.Queue()
        self.output_thread = None

    def start_engine(self):
        """Start the UCI engine."""
        print("Starting UCI engine...")
        self.process = subprocess.Popen(
            [sys.executable, "-m", "interfaces.uci"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,  # Unbuffered
        )

        # Start output reader thread
        self.output_thread = threading.Thread(target=self._read_output)
        self.output_thread.daemon = True
        self.output_thread.start()

        time.sleep(0.5)  # Give engine time to start
        return True

    def _read_output(self):
        """Read output from engine in background thread."""
        while self.process and self.process.poll() is None:
            try:
                line = self.process.stdout.readline()
                if line:
                    self.output_queue.put(line.strip())
            except:
                break

    def send_command(self, command, timeout=5):
        """Send command and wait for response."""
        print(f"Sending: {command}")

        # Clear any existing output
        while not self.output_queue.empty():
            self.output_queue.get()

        # Send command
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()

        # Collect responses
        responses = []
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                response = self.output_queue.get(timeout=0.1)
                responses.append(response)
                print(f"Received: {response}")

                # Check if we got a complete response
                if any(keyword in response.lower() for keyword in ["uciok", "readyok", "bestmove"]):
                    break
            except queue.Empty:
                continue

        return "\n".join(responses)

    def test_basic_commands(self):
        """Test basic UCI commands."""
        print("\n=== Testing Basic UCI Commands ===")

        tests = [
            ("uci", "uciok"),
            ("isready", "readyok"),
            ("ucinewgame", None),
            ("position startpos", None),
            ("go movetime 1000", "bestmove"),
        ]

        passed = 0
        total = len(tests)

        for command, expected in tests:
            print(f"\nTesting: {command}")
            response = self.send_command(command)

            if expected is None:
                print("✅ PASSED (no specific response expected)")
                passed += 1
            elif expected.lower() in response.lower():
                print(f"✅ PASSED - Found '{expected}' in response")
                passed += 1
            else:
                print(f"❌ FAILED - Expected '{expected}', got: {response}")

        return passed, total

    def test_position_variations(self):
        """Test different position setups."""
        print("\n=== Testing Position Commands ===")

        # Reset
        self.send_command("ucinewgame")

        tests = [
            ("position startpos", None),
            ("position startpos moves e2e4", None),
            ("position fen rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", None),
        ]

        passed = 0
        total = len(tests)

        for command, expected in tests:
            print(f"\nTesting: {command}")
            response = self.send_command(command)

            if expected is None:
                print("✅ PASSED")
                passed += 1
            else:
                print(f"❌ FAILED - Expected '{expected}', got: {response}")

        return passed, total

    def test_search_parameters(self):
        """Test different search parameters."""
        print("\n=== Testing Search Parameters ===")

        # Reset
        self.send_command("ucinewgame")
        self.send_command("position startpos")

        tests = [
            ("go movetime 500", "bestmove"),
            ("go nodes 50", "bestmove"),
            ("go depth 2", "bestmove"),  # Should work but may log warning
        ]

        passed = 0
        total = len(tests)

        for command, expected in tests:
            print(f"\nTesting: {command}")
            response = self.send_command(command, timeout=10)

            if expected.lower() in response.lower():
                print(f"✅ PASSED - Found '{expected}' in response")
                passed += 1
            else:
                print(f"❌ FAILED - Expected '{expected}', got: {response}")

        return passed, total

    def test_stability(self, num_games=2):
        """Test engine stability with multiple games."""
        print(f"\n=== Testing Stability ({num_games} games) ===")

        passed = 0

        for game_num in range(1, num_games + 1):
            print(f"\nGame {game_num}:")

            # Reset
            self.send_command("ucinewgame")
            self.send_command("position startpos")

            # Play a few moves
            game_passed = True
            for move_num in range(1, 4):  # 3 moves per side
                print(f"  Move {move_num}:")
                response = self.send_command("go movetime 300", timeout=8)

                if "bestmove" not in response.lower():
                    print(f"❌ FAILED: No bestmove in response: {response}")
                    game_passed = False
                    break

                # Extract and apply move
                move_line = [line for line in response.split("\n") if "bestmove" in line.lower()]
                if move_line:
                    move = move_line[0].split()[-1]
                    print(f"    Engine played: {move}")
                    self.send_command(f"position startpos moves {move}")
                else:
                    print(f"❌ FAILED: Could not extract move")
                    game_passed = False
                    break

            if game_passed:
                print(f"✅ Game {game_num} completed successfully")
                passed += 1
            else:
                print(f"❌ Game {game_num} failed")

        return passed, num_games

    def cleanup(self):
        """Clean up the engine process."""
        if self.process:
            try:
                self.send_command("quit")
                time.sleep(0.5)
                if self.process.poll() is None:
                    self.process.terminate()
            except:
                pass
            finally:
                self.process = None

    def run_all_tests(self):
        """Run all tests."""
        print("UCI Conformance Testing for Zyra Chess Engine")
        print("=" * 60)

        if not self.start_engine():
            print("❌ Failed to start engine")
            return False

        try:
            # Run test suites
            basic_passed, basic_total = self.test_basic_commands()
            position_passed, position_total = self.test_position_variations()
            search_passed, search_total = self.test_search_parameters()
            stability_passed, stability_total = self.test_stability(2)

            # Summary
            total_passed = basic_passed + position_passed + search_passed + stability_passed
            total_tests = basic_total + position_total + search_total + stability_total

            print("\n" + "=" * 60)
            print("TEST SUMMARY:")
            print(f"Basic Commands: {basic_passed}/{basic_total}")
            print(f"Position Commands: {position_passed}/{position_total}")
            print(f"Search Commands: {search_passed}/{search_total}")
            print(f"Stability Tests: {stability_passed}/{stability_total}")
            print(f"Overall: {total_passed}/{total_tests}")

            if total_passed == total_tests:
                print("🎉 All tests passed!")
                return True
            else:
                print("❌ Some tests failed")
                return False

        finally:
            self.cleanup()


def main():
    tester = UCITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
