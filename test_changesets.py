#!/usr/bin/env python3
"""
Test script for the changeset system.
Run this to validate all components work correctly.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(message):
    """Print a formatted header."""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}{message}{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")


def print_success(message):
    """Print success message."""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    """Print error message."""
    print(f"{RED}✗ {message}{RESET}")


def print_info(message):
    """Print info message."""
    print(f"{YELLOW}ℹ {message}{RESET}")


def run_command(cmd, capture_output=True):
    """Run a shell command and return result."""
    print(f"  Running: {cmd}")
    if capture_output:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  Error: {result.stderr}")
        return result
    else:
        return subprocess.run(cmd, shell=True)


def backup_files():
    """Backup important files before testing."""
    files_to_backup = [
        "pyproject.toml",
        "stagehand/__init__.py",
        "CHANGELOG.md",
        ".changeset/config.json"
    ]
    
    backup_dir = Path(".changeset-test-backup")
    backup_dir.mkdir(exist_ok=True)
    
    for file in files_to_backup:
        if Path(file).exists():
            dest = backup_dir / file.replace("/", "_")
            shutil.copy2(file, dest)
            print_info(f"Backed up {file}")
    
    return backup_dir


def restore_files(backup_dir):
    """Restore backed up files."""
    files_to_restore = [
        ("pyproject.toml", "pyproject.toml"),
        ("stagehand___init__.py", "stagehand/__init__.py"),
        ("CHANGELOG.md", "CHANGELOG.md"),
        (".changeset_config.json", ".changeset/config.json")
    ]
    
    for backup_name, original_path in files_to_restore:
        backup_file = backup_dir / backup_name
        if backup_file.exists():
            shutil.copy2(backup_file, original_path)
            print_info(f"Restored {original_path}")
    
    # Clean up backup directory
    shutil.rmtree(backup_dir)


def test_changeset_creation():
    """Test creating changesets."""
    print_header("Testing Changeset Creation")
    
    # Test 1: Create patch changeset
    print("\nTest 1: Creating patch changeset...")
    result = run_command(
        'python3 .changeset/scripts/changeset.py --type patch --message "Test patch change"'
    )
    if result.returncode == 0:
        print_success("Patch changeset created successfully")
    else:
        print_error("Failed to create patch changeset")
        return False
    
    # Test 2: Create minor changeset
    print("\nTest 2: Creating minor changeset...")
    result = run_command(
        'python3 .changeset/scripts/changeset.py --type minor --message "Test minor feature"'
    )
    if result.returncode == 0:
        print_success("Minor changeset created successfully")
    else:
        print_error("Failed to create minor changeset")
        return False
    
    # Test 3: Create major changeset
    print("\nTest 3: Creating major changeset...")
    result = run_command(
        'python3 .changeset/scripts/changeset.py --type major --message "Test breaking change"'
    )
    if result.returncode == 0:
        print_success("Major changeset created successfully")
    else:
        print_error("Failed to create major changeset")
        return False
    
    # Check changesets were created
    changesets = list(Path(".changeset").glob("*.md"))
    changesets = [cs for cs in changesets if cs.name != "README.md"]
    
    if len(changesets) >= 3:
        print_success(f"Found {len(changesets)} changesets")
        for cs in changesets:
            print(f"  - {cs.name}")
    else:
        print_error(f"Expected at least 3 changesets, found {len(changesets)}")
        return False
    
    return True


def test_version_bumping():
    """Test version bumping logic."""
    print_header("Testing Version Bumping")
    
    # Get current version
    with open("pyproject.toml") as f:
        content = f.read()
        import re
        match = re.search(r'version = "([^"]+)"', content)
        current_version = match.group(1) if match else "0.0.0"
    
    print(f"Current version: {current_version}")
    
    # Run version script (dry run first)
    print("\nTest 1: Dry run version bump...")
    result = run_command("python3 .changeset/scripts/version.py --dry-run")
    if result.returncode == 0:
        print_success("Dry run completed successfully")
        # Check output for expected version bump
        if "→" in result.stdout:
            print(f"  {result.stdout.split('→')[0].split('Version bump:')[1].strip()} → {result.stdout.split('→')[1].split()[0]}")
    else:
        print_error("Dry run failed")
        return False
    
    # Run actual version bump
    print("\nTest 2: Actual version bump...")
    result = run_command("python3 .changeset/scripts/version.py")
    if result.returncode == 0:
        print_success("Version bump completed successfully")
        
        # Verify files were updated
        with open("pyproject.toml") as f:
            content = f.read()
            match = re.search(r'version = "([^"]+)"', content)
            new_version = match.group(1) if match else "0.0.0"
        
        print(f"  New version in pyproject.toml: {new_version}")
        
        # Check __init__.py
        with open("stagehand/__init__.py") as f:
            content = f.read()
            if f'__version__ = "{new_version}"' in content:
                print_success("Version updated in __init__.py")
            else:
                print_error("Version not updated correctly in __init__.py")
                return False
        
        # Check if changesets were archived
        archive_dir = Path(".changeset/archive") / new_version
        if archive_dir.exists():
            archived = list(archive_dir.glob("*.md"))
            print_success(f"Changesets archived ({len(archived)} files)")
        else:
            print_error("Changesets not archived")
            return False
            
    else:
        print_error("Version bump failed")
        return False
    
    return True


def test_changelog_generation():
    """Test changelog generation."""
    print_header("Testing Changelog Generation")
    
    # Check if changeset data exists
    data_file = Path(".changeset/.changeset-data.json")
    if not data_file.exists():
        print_error("No changeset data file found")
        return False
    
    # Test dry run
    print("\nTest 1: Dry run changelog generation...")
    result = run_command("python3 .changeset/scripts/changelog.py --dry-run")
    if result.returncode == 0:
        print_success("Dry run completed successfully")
        # Show preview
        if "Generated changelog entry:" in result.stdout:
            print("\nChangelog preview:")
            lines = result.stdout.split("\n")
            in_preview = False
            for line in lines:
                if "Generated changelog entry:" in line:
                    in_preview = True
                elif "-" * 60 in line:
                    if in_preview:
                        break
                elif in_preview:
                    print(f"  {line}")
    else:
        print_error("Dry run failed")
        return False
    
    # Test actual changelog generation
    print("\nTest 2: Actual changelog generation...")
    result = run_command("python3 .changeset/scripts/changelog.py")
    if result.returncode == 0:
        print_success("Changelog generation completed successfully")
        
        # Verify CHANGELOG.md was updated
        if Path("CHANGELOG.md").exists():
            with open("CHANGELOG.md") as f:
                content = f.read()
                if "## [" in content:
                    print_success("CHANGELOG.md updated with new version")
                    # Show first few lines of new entry
                    lines = content.split("\n")
                    print("\nNew changelog entry:")
                    for i, line in enumerate(lines):
                        if line.startswith("## ["):
                            for j in range(min(10, len(lines) - i)):
                                print(f"  {lines[i + j]}")
                            break
                else:
                    print_error("CHANGELOG.md not updated correctly")
                    return False
        else:
            print_error("CHANGELOG.md not found")
            return False
    else:
        print_error("Changelog generation failed")
        return False
    
    return True


def test_pre_commit_hooks():
    """Test pre-commit hook scripts."""
    print_header("Testing Pre-commit Hooks")
    
    # Test changeset validation
    print("\nTest 1: Validating changeset files...")
    
    # Create a valid changeset for testing
    valid_changeset = Path(".changeset/test-valid.md")
    valid_changeset.write_text("""---
"stagehand": patch
---

Test changeset for validation
""")
    
    result = run_command(f"python3 .changeset/scripts/validate-changesets.py {valid_changeset}")
    if result.returncode == 0:
        print_success("Valid changeset passed validation")
    else:
        print_error("Valid changeset failed validation")
        valid_changeset.unlink()
        return False
    
    # Create an invalid changeset
    invalid_changeset = Path(".changeset/test-invalid.md")
    invalid_changeset.write_text("""---
invalid format
---
""")
    
    result = run_command(f"python3 .changeset/scripts/validate-changesets.py {invalid_changeset}")
    if result.returncode != 0:
        print_success("Invalid changeset correctly rejected")
    else:
        print_error("Invalid changeset was not rejected")
        valid_changeset.unlink()
        invalid_changeset.unlink()
        return False
    
    # Clean up test files
    valid_changeset.unlink()
    invalid_changeset.unlink()
    
    # Test changeset check (will fail on main branch, which is expected)
    print("\nTest 2: Testing changeset check...")
    result = run_command("python3 .changeset/scripts/check-changeset.py")
    print_info("Changeset check completed (may fail on main branch - that's expected)")
    
    return True


def main():
    """Run all tests."""
    print_header("Changeset System Test Suite")
    print_info("This will test the changeset system components")
    print_info("Original files will be backed up and restored")
    
    # Check we're in the right directory
    if not Path(".changeset/config.json").exists():
        print_error("Not in project root directory (no .changeset/config.json found)")
        sys.exit(1)
    
    # Backup files
    print("\nBacking up files...")
    backup_dir = backup_files()
    
    try:
        # Run tests
        tests = [
            ("Changeset Creation", test_changeset_creation),
            ("Version Bumping", test_version_bumping),
            ("Changelog Generation", test_changelog_generation),
            ("Pre-commit Hooks", test_pre_commit_hooks),
        ]
        
        results = []
        for name, test_func in tests:
            try:
                result = test_func()
                results.append((name, result))
            except Exception as e:
                print_error(f"Exception in {name}: {e}")
                results.append((name, False))
        
        # Summary
        print_header("Test Summary")
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for name, result in results:
            if result:
                print_success(f"{name}: PASSED")
            else:
                print_error(f"{name}: FAILED")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print_success("\nAll tests passed! 🎉")
        else:
            print_error(f"\n{total - passed} tests failed")
        
    finally:
        # Restore files
        print("\nRestoring original files...")
        restore_files(backup_dir)
        
        # Clean up any remaining test changesets
        for cs in Path(".changeset").glob("*.md"):
            if cs.name not in ["README.md", "wild-rivers-sing.md"]:  # Keep the original one
                cs.unlink()
        
        # Clean up archive directory if it exists
        archive_dir = Path(".changeset/archive")
        if archive_dir.exists():
            shutil.rmtree(archive_dir)
        
        # Clean up changeset data file
        data_file = Path(".changeset/.changeset-data.json")
        if data_file.exists():
            data_file.unlink()
        
        print_success("Cleanup completed")


if __name__ == "__main__":
    main()