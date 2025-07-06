#!/usr/bin/env python3
"""
Quick test to validate CI setup is working locally.
"""
import subprocess
import sys


def run_command(cmd, description):
    """Run a command and check if it succeeds."""
    print(f"🔍 Testing {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description}: PASSED")
            return True
        else:
            print(f"❌ {description}: FAILED")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description}: TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description}: EXCEPTION - {e}")
        return False


def main():
    """Test CI setup components."""
    print("🚀 Testing CI/CD Setup")
    print("=" * 40)
    
    tests = [
        ("uv --version", "uv installation"),
        ("uv run python --version", "Python via uv"),
        ("uv run python -c 'import app; print(\"✓ App imports\")'", "App import"),
        ("uv run python -c 'import models; print(\"✓ Models import\")'", "Models import"),
        ("uv run python -c 'import pytest; print(\"✓ Pytest available\")'", "Pytest availability"),
        ("uv run ruff --version", "Ruff linter"),
        ("uv run black --version", "Black formatter"),
        ("uv run isort --version", "isort import sorter"),
        ("uv run bandit --version", "Bandit security scanner"),
        ("uv run safety --version", "Safety dependency scanner"),
    ]
    
    passed = 0
    total = len(tests)
    
    for cmd, desc in tests:
        if run_command(cmd, desc):
            passed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 CI setup is ready!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())