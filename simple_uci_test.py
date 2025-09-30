#!/usr/bin/env python3
"""
Simple UCI Testing Script for Zyra Chess Engine

This script tests UCI protocol by sending commands and checking responses.
"""

import subprocess
import sys
import time


def test_uci_command(engine_cmd, test_input, expected_output=None):
    """Test a single UCI command."""
    print(f"Testing: {test_input}")

    try:
        # Start the engine
        process = subprocess.Popen(
            engine_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Send command
        stdout, stderr = process.communicate(input=test_input, timeout=10)

        print(f"Output: {stdout.strip()}")
        if stderr.strip():
            print(f"Stderr: {stderr.strip()}")

        # Check if expected output is found
        if expected_output:
            if expected_output.lower() in stdout.lower():
                print("✅ PASSED")
                return True
            else:
                print(f"❌ FAILED - Expected '{expected_output}', got: {stdout.strip()}")
                return False
        else:
            print("✅ PASSED (no specific output expected)")
            return True

    except subprocess.TimeoutExpired:
        print("❌ FAILED - Timeout")
        process.kill()
        return False
    except Exception as e:
        print(f"❌ FAILED - Error: {e}")
        return False


def main():
    """Run UCI conformance tests."""
    print("UCI Conformance Testing for Zyra Chess Engine")
    print("=" * 50)

    # Determine engine command
    engine_cmd = [sys.executable, "-m", "interfaces.uci"]

    # Test cases
    tests = [
        ("uci\n", "uciok"),
        ("isready\n", "readyok"),
        ("ucinewgame\n", None),
        ("position startpos\n", None),
        ("go movetime 1000\n", "bestmove"),
        ("quit\n", None),
    ]

    passed = 0
    total = len(tests)

    for test_input, expected in tests:
        if test_uci_command(engine_cmd, test_input, expected):
            passed += 1
        print()

    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All UCI tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
