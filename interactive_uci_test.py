#!/usr/bin/env python3
"""
Interactive UCI Test Interface

This script provides an interactive way to test your UCI engine
with a user-friendly interface that simulates what a chess GUI would do.
"""

import os
import subprocess
import sys
import time
from typing import List, Tuple

# Add current directory to path
sys.path.insert(0, ".")

from interfaces.uci import UCIEngine


class InteractiveUCITester:
    """Interactive UCI testing interface."""

    def __init__(self):
        self.engine = UCIEngine()
        self.test_results = []

    def print_header(self, title: str):
        """Print a formatted header."""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")

    def print_command(self, command: str):
        """Print a command in a formatted way."""
        print(f"\n📤 Sending: {command}")

    def print_response(self, response: str, expected: str = None):
        """Print a response in a formatted way."""
        if response:
            print(f"📥 Response: {response}")
        else:
            print("📥 Response: (no output)")

        if expected:
            if expected.lower() in str(response).lower():
                print("✅ PASSED")
                return True
            else:
                print(f"❌ FAILED - Expected '{expected}'")
                return False
        else:
            print("✅ PASSED (no specific response expected)")
            return True

    def test_basic_commands(self):
        """Test basic UCI commands interactively."""
        self.print_header("Basic UCI Commands Test")

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
            self.print_command(command)
            response = self.engine.handle_command(command)
            if self.print_response(response, expected):
                passed += 1
            time.sleep(0.5)  # Small delay for readability

        print(f"\n📊 Basic Commands: {passed}/{total} passed")
        return passed == total

    def test_position_variations(self):
        """Test different position setups."""
        self.print_header("Position Setup Test")

        # Reset engine
        self.engine.handle_command("ucinewgame")

        tests = [
            ("position startpos", None),
            ("position startpos moves e2e4", None),
            ("position fen rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", None),
        ]

        passed = 0
        total = len(tests)

        for command, expected in tests:
            self.print_command(command)
            response = self.engine.handle_command(command)
            if self.print_response(response, expected):
                passed += 1
            time.sleep(0.5)

        print(f"\n📊 Position Commands: {passed}/{total} passed")
        return passed == total

    def test_search_parameters(self):
        """Test different search parameters."""
        self.print_header("Search Parameters Test")

        # Reset and set position
        self.engine.handle_command("ucinewgame")
        self.engine.handle_command("position startpos")

        tests = [
            ("go movetime 500", "bestmove"),
            ("go nodes 100", "bestmove"),
            ("go depth 2", "bestmove"),  # Should work but may log warning
        ]

        passed = 0
        total = len(tests)

        for command, expected in tests:
            self.print_command(command)
            response = self.engine.handle_command(command)
            if self.print_response(response, expected):
                passed += 1
            time.sleep(0.5)

        print(f"\n📊 Search Commands: {passed}/{total} passed")
        return passed == total

    def test_stability(self):
        """Test engine stability with multiple moves."""
        self.print_header("Stability Test")

        # Reset engine
        self.engine.handle_command("ucinewgame")
        self.engine.handle_command("position startpos")

        # Play a sequence of moves
        moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4"]

        print(f"🎮 Playing {len(moves)} moves to test stability...")

        passed_moves = 0

        for i, move in enumerate(moves):
            print(f"\n🔄 Move {i+1}: {move}")

            # Get engine response
            self.print_command("go movetime 200")
            response = self.engine.handle_command("go movetime 200")

            if "bestmove" in str(response).lower():
                print(f"📥 Engine response: {response}")
                print("✅ Engine responded with bestmove")
                passed_moves += 1

                # Apply the move for next iteration
                if i < len(moves) - 1:  # Don't apply the last move
                    current_moves = " ".join(moves[: i + 1])
                    self.engine.handle_command(f"position startpos moves {current_moves}")
            else:
                print(f"❌ No bestmove in response: {response}")

            time.sleep(0.5)

        print(f"\n📊 Stability: {passed_moves}/{len(moves)} moves completed")
        return passed_moves == len(moves)

    def test_manual_commands(self):
        """Allow manual command testing."""
        self.print_header("Manual Command Testing")

        print("Enter UCI commands manually (type 'quit' to exit):")
        print("Available commands: uci, isready, ucinewgame, position, go, quit")

        while True:
            try:
                command = input("\n🔧 Enter command: ").strip()

                if command.lower() == "quit":
                    break

                if not command:
                    continue

                self.print_command(command)
                response = self.engine.handle_command(command)
                self.print_response(response)

            except KeyboardInterrupt:
                print("\n\n👋 Exiting manual testing...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    def run_all_tests(self):
        """Run all automated tests."""
        print("🚀 Zyra UCI Engine - Interactive Testing")
        print("=" * 60)

        # Run test suites
        basic_ok = self.test_basic_commands()
        position_ok = self.test_position_variations()
        search_ok = self.test_search_parameters()
        stability_ok = self.test_stability()

        # Summary
        self.print_header("Test Results Summary")

        results = [
            ("Basic UCI Commands", basic_ok),
            ("Position Commands", position_ok),
            ("Search Commands", search_ok),
            ("Stability Testing", stability_ok),
        ]

        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name}: {status}")

        all_passed = all(result for _, result in results)

        if all_passed:
            print("\n🎉 ALL TESTS PASSED!")
            print("Your Zyra engine is UCI compliant and ready for GUI integration!")
        else:
            print("\n❌ Some tests failed. Check the output above for details.")

        return all_passed

    def show_menu(self):
        """Show the main menu."""
        while True:
            print("\n" + "=" * 60)
            print("🧪 Zyra UCI Engine Tester")
            print("=" * 60)
            print("1. Run all automated tests")
            print("2. Test basic UCI commands")
            print("3. Test position variations")
            print("4. Test search parameters")
            print("5. Test stability")
            print("6. Manual command testing")
            print("7. Show GUI integration info")
            print("8. Exit")

            choice = input("\n🔧 Select an option (1-8): ").strip()

            if choice == "1":
                self.run_all_tests()
            elif choice == "2":
                self.test_basic_commands()
            elif choice == "3":
                self.test_position_variations()
            elif choice == "4":
                self.test_search_parameters()
            elif choice == "5":
                self.test_stability()
            elif choice == "6":
                self.test_manual_commands()
            elif choice == "7":
                self.show_gui_info()
            elif choice == "8":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please select 1-8.")

    def show_gui_info(self):
        """Show GUI integration information."""
        self.print_header("GUI Integration Information")

        print("🎮 To use your engine with chess GUIs:")
        print(f"   Engine Path: python -m interfaces.uci")
        print(f"   Working Directory: {os.getcwd()}")
        print(f"   Engine Name: Zyra Chess Engine")

        print("\n📋 Recommended GUIs for Linux:")
        print("   1. PyChess: pip install pychess")
        print("   2. Lucas Chess: pip install lucas-chess")
        print("   3. Cute Chess: Build from source")
        print("   4. Arena: Use with Wine")

        print("\n🔧 Quick PyChess Setup:")
        print("   1. Install: pip install pychess")
        print("   2. Run: pychess")
        print("   3. Add engine: python -m interfaces.uci")
        print("   4. Start playing!")


def main():
    """Main function."""
    tester = InteractiveUCITester()
    tester.show_menu()


if __name__ == "__main__":
    main()
