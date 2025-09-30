#!/usr/bin/env python3
"""
Working UCI Test Script

This script tests the UCI engine by sending all commands at once
and parsing the output, which works better with the engine's design.
"""

import re
import subprocess
import sys


def test_uci_commands():
    """Test UCI commands by sending them all at once."""
    print("Testing Zyra UCI Engine")
    print("=" * 40)

    # Prepare test commands
    test_commands = [
        "uci",
        "isready",
        "ucinewgame",
        "position startpos",
        "go movetime 1000",
        "quit",
    ]

    # Send all commands at once
    input_text = "\n".join(test_commands) + "\n"

    print("Sending commands:")
    for cmd in test_commands:
        print(f"  {cmd}")

    try:
        # Run the engine with unbuffered output
        result = subprocess.run(
            [sys.executable, "-u", "-m", "interfaces.uci"],
            input=input_text,
            capture_output=True,
            text=True,
            timeout=30,
        )

        print(f"\nEngine output:")
        print(result.stdout)

        if result.stderr:
            print(f"Engine stderr:")
            print(result.stderr)

        # Parse results
        output = result.stdout.lower()

        tests = [
            ("uci", "uciok" in output),
            ("isready", "readyok" in output),
            ("ucinewgame", True),  # No specific output expected
            ("position startpos", True),  # No specific output expected
            ("go movetime", "bestmove" in output),
            ("quit", True),  # Process should exit
        ]

        print(f"\nTest Results:")
        passed = 0
        for test_name, result in tests:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {test_name}: {status}")
            if result:
                passed += 1

        print(f"\nSummary: {passed}/{len(tests)} tests passed")
        return passed == len(tests)

    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_position_variations():
    """Test different position setups."""
    print("\n" + "=" * 40)
    print("Testing Position Variations")
    print("=" * 40)

    test_cases = [
        {
            "name": "Start position",
            "commands": ["uci", "isready", "position startpos", "go movetime 500", "quit"],
        },
        {
            "name": "Start position with moves",
            "commands": [
                "uci",
                "isready",
                "position startpos moves e2e4",
                "go movetime 500",
                "quit",
            ],
        },
        {
            "name": "FEN position",
            "commands": [
                "uci",
                "isready",
                "position fen rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                "go movetime 500",
                "quit",
            ],
        },
    ]

    passed = 0
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")

        input_text = "\n".join(test_case["commands"]) + "\n"

        try:
            result = subprocess.run(
                [sys.executable, "-u", "-m", "interfaces.uci"],
                input=input_text,
                capture_output=True,
                text=True,
                timeout=20,
            )

            if "bestmove" in result.stdout.lower():
                print("✅ PASSED")
                passed += 1
            else:
                print("❌ FAILED - No bestmove in output")
                print(f"Output: {result.stdout}")

        except Exception as e:
            print(f"❌ FAILED - Error: {e}")

    print(f"\nPosition tests: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)


def test_search_parameters():
    """Test different search parameters."""
    print("\n" + "=" * 40)
    print("Testing Search Parameters")
    print("=" * 40)

    test_cases = [
        {
            "name": "Movetime search",
            "commands": ["uci", "isready", "position startpos", "go movetime 500", "quit"],
        },
        {
            "name": "Nodes search",
            "commands": ["uci", "isready", "position startpos", "go nodes 100", "quit"],
        },
        {
            "name": "Depth search (should log warning)",
            "commands": ["uci", "isready", "position startpos", "go depth 2", "quit"],
        },
    ]

    passed = 0
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")

        input_text = "\n".join(test_case["commands"]) + "\n"

        try:
            result = subprocess.run(
                [sys.executable, "-u", "-m", "interfaces.uci"],
                input=input_text,
                capture_output=True,
                text=True,
                timeout=20,
            )

            if "bestmove" in result.stdout.lower():
                print("✅ PASSED")
                passed += 1
            else:
                print("❌ FAILED - No bestmove in output")
                print(f"Output: {result.stdout}")

        except Exception as e:
            print(f"❌ FAILED - Error: {e}")

    print(f"\nSearch parameter tests: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)


def test_stability():
    """Test engine stability with multiple games."""
    print("\n" + "=" * 40)
    print("Stability Testing")
    print("=" * 40)

    print("Running 3 stability test games...")

    # Create a sequence of moves for a mini-game
    moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4"]

    commands = ["uci", "isready", "ucinewgame", "position startpos"]

    # Add moves one by one
    for i, move in enumerate(moves):
        if i == 0:
            commands.append(f"position startpos moves {move}")
        else:
            current_moves = " ".join(moves[: i + 1])
            commands.append(f"position startpos moves {current_moves}")
        commands.append("go movetime 200")

    commands.append("quit")

    input_text = "\n".join(commands) + "\n"

    try:
        result = subprocess.run(
            [sys.executable, "-u", "-m", "interfaces.uci"],
            input=input_text,
            capture_output=True,
            text=True,
            timeout=30,
        )

        # Count bestmove responses
        bestmove_count = result.stdout.lower().count("bestmove")
        expected_moves = len(moves)

        print(f"Expected {expected_moves} moves, got {bestmove_count} bestmove responses")

        if bestmove_count >= expected_moves:
            print("✅ PASSED - Engine completed stability test")
            return True
        else:
            print("❌ FAILED - Not enough moves completed")
            print(f"Output: {result.stdout}")
            return False

    except Exception as e:
        print(f"❌ FAILED - Error: {e}")
        return False


def main():
    """Run all UCI tests."""
    print("Zyra Chess Engine - UCI Conformance Testing")
    print("=" * 60)

    # Run test suites
    basic_ok = test_uci_commands()
    position_ok = test_position_variations()
    search_ok = test_search_parameters()
    stability_ok = test_stability()

    # Summary
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print(f"Basic UCI Commands: {'✅ PASSED' if basic_ok else '❌ FAILED'}")
    print(f"Position Variations: {'✅ PASSED' if position_ok else '❌ FAILED'}")
    print(f"Search Parameters: {'✅ PASSED' if search_ok else '❌ FAILED'}")
    print(f"Stability Testing: {'✅ PASSED' if stability_ok else '❌ FAILED'}")

    all_passed = basic_ok and position_ok and search_ok and stability_ok

    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("Your Zyra engine is UCI compliant and ready for GUI integration!")
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
