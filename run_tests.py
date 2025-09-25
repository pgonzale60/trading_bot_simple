#!/usr/bin/env python3
"""
Test runner for the trading bot system.

This script runs all unit tests and provides a comprehensive test report.
"""

import unittest
import sys
import os
import time
from io import StringIO


def discover_and_run_tests():
    """Discover and run all tests in the tests directory."""
    # Add current directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    # Discover tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(current_dir, 'tests')

    # Change to the project directory to ensure proper imports
    original_cwd = os.getcwd()
    try:
        os.chdir(current_dir)
        suite = loader.discover('tests', pattern='test_*.py')
    finally:
        os.chdir(original_cwd)

    # Create test runner with detailed output
    stream = StringIO()
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=2,
        failfast=False,
        buffer=True
    )

    print("🧪 TRADING BOT UNIT TESTS")
    print("=" * 50)

    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()

    # Print results
    output = stream.getvalue()
    print(output)

    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"Duration: {end_time - start_time:.2f} seconds")

    # Detailed failure/error report
    if result.failures:
        print(f"\n❌ FAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}")

    if result.errors:
        print(f"\n💥 ERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}")

    # Overall result
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
        return True
    else:
        print("\n❌ SOME TESTS FAILED!")
        return False


def run_specific_test_module(module_name):
    """Run tests from a specific module."""
    try:
        # Add current directory to path for imports
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)

        # Import the specific test module
        test_module = __import__(f'tests.{module_name}', fromlist=[module_name])

        # Create test suite from the module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)

        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        return result.wasSuccessful()
    except ImportError as e:
        print(f"❌ Could not import test module '{module_name}': {e}")
        return False


def main():
    """Main test runner."""
    import argparse

    parser = argparse.ArgumentParser(description='Trading Bot Test Runner')
    parser.add_argument(
        '--module',
        help='Run tests from specific module (e.g., test_risk_management)',
        choices=['test_multi_asset_tester', 'test_optimizer', 'test_risk_management']
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available test modules'
    )

    args = parser.parse_args()

    if args.list:
        print("Available test modules:")
        print("  - test_risk_management     # Core risk management tests (ESSENTIAL)")
        print("  - test_multi_asset_tester # Multi-asset testing functionality")
        print("  - test_optimizer          # Strategy parameter optimization")
        return

    if args.module:
        print(f"Running tests from module: {args.module}")
        success = run_specific_test_module(args.module)
    else:
        print("Running all tests...")
        success = discover_and_run_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()