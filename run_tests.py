#!/usr/bin/env python3
"""
TaskFlow Backend Test Runner

This script provides an easy way to run the test suite with different options.
"""
import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and print the description."""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0


def main():
    """Main test runner function."""
    print("🚀 TaskFlow Backend Test Suite")
    print("Using pytest - The most popular Python testing framework")
    
    # Change to the backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if virtual environment is activated
    if not os.environ.get('VIRTUAL_ENV'):
        print("\n⚠️  Warning: Virtual environment not detected.")
        print("Please activate the virtual environment first:")
        print("  source venv/bin/activate")
        return False
    
    # Run different test scenarios
    test_scenarios = [
        {
            'cmd': 'python -m pytest tests/unit/test_auth_routes.py -v',
            'desc': 'Authentication Tests'
        },
        {
            'cmd': 'python -m pytest tests/unit/test_project_routes.py -v --tb=short',
            'desc': 'Project Management Tests'
        },
        {
            'cmd': 'python -m pytest tests/unit/test_tag_routes.py -v --tb=short',
            'desc': 'Tag Management Tests'
        },
        {
            'cmd': 'python -m pytest tests/unit/test_models.py -v --tb=short',
            'desc': 'Database Model Tests'
        }
    ]
    
    success_count = 0
    total_count = len(test_scenarios)
    
    for scenario in test_scenarios:
        if run_command(scenario['cmd'], scenario['desc']):
            success_count += 1
        else:
            print(f"❌ {scenario['desc']} failed")
    
    # Run coverage report
    print(f"\n{'='*60}")
    print("📊 Generating Coverage Report")
    print(f"{'='*60}")
    
    coverage_cmd = 'python -m pytest tests/unit/test_auth_routes.py tests/unit/test_project_routes.py tests/unit/test_tag_routes.py --cov=src --cov-report=term-missing --cov-report=html --tb=no -q'
    subprocess.run(coverage_cmd, shell=True)
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 Test Summary")
    print(f"{'='*60}")
    print(f"✅ Successful test suites: {success_count}/{total_count}")
    print(f"📈 Coverage report generated in htmlcov/index.html")
    print(f"🎯 Framework: pytest (most popular Python testing framework)")
    
    if success_count == total_count:
        print("🎉 All test suites passed!")
        return True
    else:
        print("⚠️  Some test suites had issues - check output above")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

