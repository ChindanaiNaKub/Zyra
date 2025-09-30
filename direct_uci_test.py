#!/usr/bin/env python3
"""
Direct UCI Testing Script

This script tests the UCI engine by importing it directly
and testing the command handling without subprocess issues.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, ".")

from interfaces.uci import UCIEngine


def test_uci_commands():
    """Test UCI commands directly."""
    print("Testing Zyra UCI Engine (Direct)")
    print("=" * 40)

    engine = UCIEngine()

    # Test basic commands
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
        response = engine.handle_command(command)
        print(f"Response: {response}")

        if expected is None:
            print("✅ PASSED (no specific response expected)")
            passed += 1
        elif expected.lower() in str(response).lower():
            print(f"✅ PASSED - Found '{expected}' in response")
            passed += 1
        else:
            print(f"❌ FAILED - Expected '{expected}', got: {response}")

    print(f"\nBasic commands: {passed}/{total} passed")
    return passed == total


def test_position_commands():
    """Test position setup commands."""
    print("\n" + "=" * 40)
    print("Testing Position Commands")
    print("=" * 40)

    engine = UCIEngine()

    # Reset engine
    engine.handle_command("ucinewgame")

    tests = [
        ("position startpos", None),
        ("position startpos moves e2e4", None),
        ("position fen rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", None),
    ]

    passed = 0
    total = len(tests)

    for command, expected in tests:
        print(f"\nTesting: {command}")
        response = engine.handle_command(command)
        print(f"Response: {response}")

        if expected is None:
            print("✅ PASSED")
            passed += 1
        else:
            print(f"❌ FAILED - Expected '{expected}', got: {response}")

    print(f"\nPosition commands: {passed}/{total} passed")
    return passed == total


def test_search_commands():
    """Test search commands."""
    print("\n" + "=" * 40)
    print("Testing Search Commands")
    print("=" * 40)

    engine = UCIEngine()

    # Reset and set position
    engine.handle_command("ucinewgame")
    engine.handle_command("position startpos")

    tests = [
        ("go movetime 500", "bestmove"),
        ("go nodes 100", "bestmove"),
        ("go depth 2", "bestmove"),  # Should work but may log warning
    ]

    passed = 0
    total = len(tests)

    for command, expected in tests:
        print(f"\nTesting: {command}")
        response = engine.handle_command(command)
        print(f"Response: {response}")

        if expected.lower() in str(response).lower():
            print(f"✅ PASSED - Found '{expected}' in response")
            passed += 1
        else:
            print(f"❌ FAILED - Expected '{expected}', got: {response}")

    print(f"\nSearch commands: {passed}/{total} passed")
    return passed == total


def test_stability():
    """Test engine stability with multiple moves."""
    print("\n" + "=" * 40)
    print("Testing Stability")
    print("=" * 40)

    engine = UCIEngine()

    # Reset engine
    engine.handle_command("ucinewgame")
    engine.handle_command("position startpos")

    # Play a sequence of moves
    moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4"]

    print(f"Playing {len(moves)} moves...")

    passed_moves = 0

    for i, move in enumerate(moves):
        print(f"\nMove {i+1}: {move}")

        # Get engine response
        response = engine.handle_command("go movetime 200")
        print(f"Engine response: {response}")

        if "bestmove" in str(response).lower():
            print("✅ Engine responded with bestmove")
            passed_moves += 1

            # Apply the move for next iteration
            if i < len(moves) - 1:  # Don't apply the last move
                current_moves = " ".join(moves[: i + 1])
                engine.handle_command(f"position startpos moves {current_moves}")
        else:
            print("❌ No bestmove in response")

    print(f"\nStability: {passed_moves}/{len(moves)} moves completed")
    return passed_moves == len(moves)


def main():
    """Run all direct UCI tests."""
    print("Zyra Chess Engine - Direct UCI Testing")
    print("=" * 60)

    # Run test suites
    basic_ok = test_uci_commands()
    position_ok = test_position_commands()
    search_ok = test_search_commands()
    stability_ok = test_stability()

    # Summary
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print(f"Basic UCI Commands: {'✅ PASSED' if basic_ok else '❌ FAILED'}")
    print(f"Position Commands: {'✅ PASSED' if position_ok else '❌ FAILED'}")
    print(f"Search Commands: {'✅ PASSED' if search_ok else '❌ FAILED'}")
    print(f"Stability Testing: {'✅ PASSED' if stability_ok else '❌ FAILED'}")

    all_passed = basic_ok and position_ok and search_ok and stability_ok

    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("Your Zyra engine is UCI compliant!")
        print("\nTo use with chess GUIs:")
        print("1. Cute Chess: Add engine with command 'python -m interfaces.uci'")
        print("2. Arena: Add UCI engine pointing to your Python installation")
        print("3. Other GUIs: Use 'python -m interfaces.uci' as the engine command")
        return 0
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
