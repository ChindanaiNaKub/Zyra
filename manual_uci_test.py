#!/usr/bin/env python3
"""
Manual UCI Testing Script

This script tests the UCI engine by running it in a subprocess and
communicating through stdin/stdout properly.
"""

import os
import subprocess
import sys
import time


def test_uci_engine():
    """Test the UCI engine with proper subprocess handling."""
    print("Testing Zyra UCI Engine")
    print("=" * 40)

    # Start the engine
    print("Starting engine...")
    process = subprocess.Popen(
        [sys.executable, "-m", "interfaces.uci"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    def send_and_wait(command, expected=None, timeout=5):
        """Send command and wait for response."""
        print(f"\nSending: {command}")

        # Send command
        process.stdin.write(command + "\n")
        process.stdin.flush()

        # Read response
        start_time = time.time()
        response_lines = []

        while time.time() - start_time < timeout:
            try:
                line = process.stdout.readline()
                if line:
                    response_lines.append(line.strip())
                    print(f"Received: {line.strip()}")

                    # Check if we got the expected response
                    if expected and expected.lower() in line.lower():
                        break
                else:
                    time.sleep(0.01)
            except:
                break

        response = "\n".join(response_lines)

        if expected:
            if expected.lower() in response.lower():
                print(f"✅ PASSED - Found '{expected}'")
                return True
            else:
                print(f"❌ FAILED - Expected '{expected}', got: {response}")
                return False
        else:
            print("✅ PASSED (no specific response expected)")
            return True

    try:
        # Test basic commands
        print("\n=== Basic UCI Commands ===")
        tests = [
            ("uci", "uciok"),
            ("isready", "readyok"),
            ("ucinewgame", None),
            ("position startpos", None),
        ]

        passed = 0
        for command, expected in tests:
            if send_and_wait(command, expected):
                passed += 1

        print(f"\nBasic commands: {passed}/{len(tests)} passed")

        # Test search
        print("\n=== Search Commands ===")
        search_tests = [
            ("go movetime 1000", "bestmove"),
            ("go nodes 100", "bestmove"),
        ]

        search_passed = 0
        for command, expected in search_tests:
            if send_and_wait(command, expected, timeout=10):
                search_passed += 1

        print(f"Search commands: {search_passed}/{len(search_tests)} passed")

        # Test quit
        print("\n=== Cleanup ===")
        send_and_wait("quit", None)

        # Wait for process to exit
        process.wait(timeout=2)

        total_passed = passed + search_passed
        total_tests = len(tests) + len(search_tests)

        print(f"\n=== SUMMARY ===")
        print(f"Total: {total_passed}/{total_tests} tests passed")

        if total_passed == total_tests:
            print("🎉 All UCI tests passed!")
            return True
        else:
            print("❌ Some tests failed")
            return False

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    finally:
        # Clean up
        try:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=1)
        except:
            pass


def test_stability():
    """Test engine stability with multiple games."""
    print("\n" + "=" * 40)
    print("STABILITY TESTING")
    print("=" * 40)

    # This is a simplified stability test
    # In a real scenario, you'd want to run longer games
    print("Running basic stability test...")

    # Test that the engine can handle multiple commands
    process = subprocess.Popen(
        [sys.executable, "-m", "interfaces.uci"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    try:
        # Send a sequence of commands
        commands = ["uci", "isready", "ucinewgame", "position startpos", "go movetime 500", "quit"]

        for cmd in commands:
            print(f"Sending: {cmd}")
            process.stdin.write(cmd + "\n")
            process.stdin.flush()
            time.sleep(0.1)

        # Wait for process to finish
        process.wait(timeout=5)
        print("✅ Stability test completed without crashes")
        return True

    except Exception as e:
        print(f"❌ Stability test failed: {e}")
        return False
    finally:
        try:
            if process.poll() is None:
                process.terminate()
        except:
            pass


def main():
    """Run all tests."""
    print("Zyra Chess Engine - UCI Conformance Testing")
    print("=" * 50)

    # Test basic UCI functionality
    uci_success = test_uci_engine()

    # Test stability
    stability_success = test_stability()

    print("\n" + "=" * 50)
    print("FINAL RESULTS:")
    print(f"UCI Conformance: {'✅ PASSED' if uci_success else '❌ FAILED'}")
    print(f"Stability: {'✅ PASSED' if stability_success else '❌ FAILED'}")

    if uci_success and stability_success:
        print("\n🎉 All tests passed! Engine is ready for GUI integration.")
        return 0
    else:
        print("\n❌ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
