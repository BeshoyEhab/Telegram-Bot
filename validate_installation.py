# =============================================================================
# FILE: validate_installation.py
# DESCRIPTION: Installation validation script - checks Phase 0 setup
# LOCATION: Project root directory
# PURPOSE: Automatically validates all Phase 0 components
# USAGE: python validate_installation.py
# =============================================================================

#!/usr/bin/env python3
"""
Installation Validation Script for Telegram School Bot
Run this script to verify Phase 0 setup is complete.

Usage: python validate_installation.py
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text: str):
    """Print section header."""
    print(f"\n{BOLD}{BLUE}{'=' * 60}{RESET}")
    print(f"{BOLD}{BLUE}{text:^60}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 60}{RESET}\n")

def print_test(name: str, passed: bool, details: str = ""):
    """Print test result."""
    status = f"{GREEN}✓ PASS{RESET}" if passed else f"{RED}✗ FAIL{RESET}"
    print(f"{status} | {name}")
    if details:
        print(f"        {details}")

def check_python_version() -> Tuple[bool, str]:
    """Check Python version >= 3.9."""
    version = sys.version_info
    required = (3, 9)
    passed = version >= required
    details = f"Found Python {version.major}.{version.minor}.{version.micro}"
    if not passed:
        details += f" (Required: {required[0]}.{required[1]}+)"
    return passed, details

def check_file_exists(filepath: str) -> Tuple[bool, str]:
    """Check if file exists."""
    path = Path(filepath)
    if path.exists():
        size = path.stat().st_size
        return True, f"Size: {size} bytes"
    return False, "File not found"

def check_directory_exists(dirpath: str) -> Tuple[bool, str]:
    """Check if directory exists."""
    path = Path(dirpath)
    if path.exists() and path.is_dir():
        files = len(list(path.iterdir()))
        return True, f"Contains {files} items"
    return False, "Directory not found"

def check_import(module_name: str) -> Tuple[bool, str]:
    """Check if module can be imported."""
    try:
        __import__(module_name)
        return True, "Import successful"
    except ImportError as e:
        return False, f"ImportError: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_config() -> Tuple[bool, str]:
    """Check configuration."""
    try:
        import config
        if not config.BOT_API:
            return False, "BOT_API not set"
        if len(config.AUTHORIZED_USERS) == 0:
            return False, "No authorized users configured"
        return True, f"Token: {config.BOT_API[:10]}..., Users: {len(config.AUTHORIZED_USERS)}"
    except Exception as e:
        return False, str(e)

def check_database() -> Tuple[bool, str]:
    """Check database connection."""
    try:
        from database import check_connection, get_table_counts
        if not check_connection():
            return False, "Connection failed"
        counts = get_table_counts()
        total = sum(counts.values())
        return True, f"9 tables created, {total} total rows"
    except Exception as e:
        return False, str(e)

def check_migrations() -> Tuple[bool, str]:
    """Check Alembic migrations."""
    try:
        import subprocess
        result = subprocess.run(
            ['alembic', 'current'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            if '(head)' in output:
                return True, "Migrations up to date"
            return False, "Migrations not at head"
        return False, "Alembic command failed"
    except FileNotFoundError:
        return False, "Alembic not installed"
    except Exception as e:
        return False, str(e)

def run_validation():
    """Run all validation checks."""
    
    print_header("PHASE 0 INSTALLATION VALIDATION")
    
    tests_passed = 0
    tests_failed = 0
    
    # Python Environment
    print_header("1. Python Environment")
    
    passed, details = check_python_version()
    print_test("Python Version", passed, details)
    tests_passed += passed
    tests_failed += not passed
    
    # Core Files
    print_header("2. Core Files")
    
    core_files = [
        "config.py",
        "main.py",
        "requirements.txt",
        ".env",
        "alembic.ini",
        "pytest.ini",
    ]
    
    for file in core_files:
        passed, details = check_file_exists(file)
        print_test(file, passed, details)
        tests_passed += passed
        tests_failed += not passed
    
    # Directories
    print_header("3. Directory Structure")
    
    directories = [
        "database",
        "utils",
        "tests",
        "handlers",
        "services",
        "middleware",
        "logs",
        "backups",
        "exports",
        "templates",
    ]
    
    for directory in directories:
        passed, details = check_directory_exists(directory)
        print_test(directory, passed, details)
        tests_passed += passed
        tests_failed += not passed
    
    # Python Imports
    print_header("4. Python Modules")
    
    modules = [
        "config",
        "database",
        "database.models",
        "database.connection",
        "utils.logging_config",
        "telegram",
        "sqlalchemy",
        "alembic",
        "pytest",
    ]
    
    for module in modules:
        passed, details = check_import(module)
        print_test(module, passed, details)
        tests_passed += passed
        tests_failed += not passed
    
    # Configuration
    print_header("5. Configuration")
    
    passed, details = check_config()
    print_test("Config Loading", passed, details)
    tests_passed += passed
    tests_failed += not passed
    
    # Database
    print_header("6. Database")
    
    passed, details = check_file_exists("school_bot.db")
    print_test("Database File", passed, details)
    tests_passed += passed
    tests_failed += not passed
    
    passed, details = check_database()
    print_test("Database Connection", passed, details)
    tests_passed += passed
    tests_failed += not passed
    
    passed, details = check_migrations()
    print_test("Migrations Status", passed, details)
    tests_passed += passed
    tests_failed += not passed
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    total_tests = tests_passed + tests_failed
    percentage = (tests_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {GREEN}{tests_passed}{RESET}")
    print(f"Failed: {RED}{tests_failed}{RESET}")
    print(f"Success Rate: {percentage:.1f}%")
    print()
    
    if tests_failed == 0:
        print(f"{GREEN}{BOLD}✓ ALL TESTS PASSED!{RESET}")
        print(f"{GREEN}Phase 0 installation is complete and ready.{RESET}")
        print(f"{YELLOW}You can now proceed to test the bot in Telegram.{RESET}")
        print()
        print("Next steps:")
        print("1. Run: python main.py")
        print("2. Send /start to your bot in Telegram")
        print("3. Run: python -m pytest tests/ -v")
        print("4. Report completion to proceed to Phase 1")
        return 0
    else:
        print(f"{RED}{BOLD}✗ SOME TESTS FAILED{RESET}")
        print(f"{RED}Please fix the issues above before proceeding.{RESET}")
        print()
        print("Common fixes:")
        print("1. Make sure virtual environment is activated")
        print("2. Run: pip install -r requirements.txt")
        print("3. Create .env file from .env.example")
        print("4. Run: alembic upgrade head")
        return 1

if __name__ == '__main__':
    try:
        exit_code = run_validation()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Validation interrupted by user{RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{RED}Unexpected error: {e}{RESET}")
        sys.exit(1)
