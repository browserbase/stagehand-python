#!/usr/bin/env python3
"""
Stagehand Migration Validation Script

This script validates that your migration from Browserbase to local setup is working correctly.
Run this after completing your migration to ensure everything is configured properly.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

try:
    from stagehand import Stagehand, StagehandConfig
except ImportError:
    print("❌ Stagehand not installed. Please install with: pip install stagehand")
    sys.exit(1)


class MigrationValidator:
    """Validates Stagehand migration setup."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
    
    def check(self, condition: bool, success_msg: str, error_msg: str, warning: bool = False):
        """Check a condition and record the result."""
        self.total_checks += 1
        if condition:
            print(f"✅ {success_msg}")
            self.success_count += 1
        else:
            if warning:
                print(f"⚠️  {error_msg}")
                self.warnings.append(error_msg)
            else:
                print(f"❌ {error_msg}")
                self.errors.append(error_msg)
    
    def validate_environment(self):
        """Validate environment setup."""
        print("\n🔍 Validating Environment Setup...")
        
        # Check for API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        together_key = os.getenv("TOGETHER_API_KEY")
        
        has_any_key = any([openai_key, anthropic_key, together_key])
        self.check(
            has_any_key,
            "LLM API key found in environment",
            "No LLM API keys found. Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or TOGETHER_API_KEY"
        )
        
        # Check for old Browserbase keys (should be warnings)
        browserbase_key = os.getenv("BROWSERBASE_API_KEY")
        browserbase_project = os.getenv("BROWSERBASE_PROJECT_ID")
        
        self.check(
            not browserbase_key,
            "No old Browserbase API key found",
            "Old BROWSERBASE_API_KEY still set - you can remove this",
            warning=True
        )
        
        self.check(
            not browserbase_project,
            "No old Browserbase project ID found",
            "Old BROWSERBASE_PROJECT_ID still set - you can remove this",
            warning=True
        )
    
    def validate_configuration(self):
        """Validate configuration creation."""
        print("\n🔍 Validating Configuration...")
        
        try:
            # Test basic configuration
            config = StagehandConfig(
                model_name="gpt-4o-mini",
                model_client_options={
                    "api_key": os.getenv("OPENAI_API_KEY") or "test-key"
                }
            )
            self.check(True, "Basic configuration created successfully", "")
            
            # Test with browser options
            config_with_browser = StagehandConfig(
                model_name="gpt-4o-mini",
                model_client_options={
                    "api_key": os.getenv("OPENAI_API_KEY") or "test-key"
                },
                local_browser_launch_options={
                    "headless": True,
                    "viewport": {"width": 1280, "height": 720}
                }
            )
            self.check(True, "Configuration with browser options created successfully", "")
            
        except Exception as e:
            self.check(False, "", f"Configuration creation failed: {e}")
    
    async def validate_runtime(self):
        """Validate runtime functionality."""
        print("\n🔍 Validating Runtime Functionality...")
        
        # Check if we have a real API key for testing
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️  Skipping runtime tests - no OPENAI_API_KEY set")
            return
        
        config = StagehandConfig(
            model_name="gpt-4o-mini",
            model_client_options={"api_key": api_key},
            local_browser_launch_options={"headless": True}
        )
        
        stagehand = None
        try:
            # Test initialization
            stagehand = Stagehand(config)
            await stagehand.init()
            self.check(True, "Stagehand initialized successfully", "")
            
            # Test browser navigation
            page = stagehand.page
            await page.goto("https://example.com")
            self.check(True, "Browser navigation works", "")
            
            # Test basic extraction
            try:
                title = await page.extract("the page title")
                self.check(
                    title is not None and len(str(title).strip()) > 0,
                    f"Extraction works: '{title}'",
                    "Extraction returned empty result"
                )
            except Exception as e:
                self.check(False, "", f"Extraction failed: {e}")
            
        except Exception as e:
            self.check(False, "", f"Runtime validation failed: {e}")
        
        finally:
            if stagehand:
                try:
                    await stagehand.close()
                    self.check(True, "Cleanup successful", "")
                except Exception as e:
                    self.check(False, "", f"Cleanup failed: {e}")
    
    def validate_file_cleanup(self):
        """Check for leftover Browserbase files."""
        print("\n🔍 Checking for Leftover Files...")
        
        # Check common locations for browserbase imports
        python_files = list(Path(".").rglob("*.py"))
        browserbase_files = []
        
        for file_path in python_files:
            if any(skip in str(file_path) for skip in ['.git', '__pycache__', '.pytest_cache']):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'browserbase' in content.lower() and 'import' in content:
                        browserbase_files.append(str(file_path))
            except:
                continue
        
        self.check(
            len(browserbase_files) == 0,
            "No browserbase imports found in Python files",
            f"Found browserbase imports in: {', '.join(browserbase_files)}",
            warning=True
        )
        
        # Check requirements.txt
        req_files = ["requirements.txt", "pyproject.toml", "setup.py"]
        for req_file in req_files:
            if Path(req_file).exists():
                try:
                    with open(req_file, 'r') as f:
                        content = f.read()
                        has_browserbase = 'browserbase' in content.lower()
                        self.check(
                            not has_browserbase,
                            f"No browserbase dependency in {req_file}",
                            f"Found browserbase dependency in {req_file}",
                            warning=True
                        )
                except:
                    pass
    
    def print_summary(self):
        """Print validation summary."""
        print("\n" + "="*60)
        print("MIGRATION VALIDATION SUMMARY")
        print("="*60)
        
        print(f"✅ Successful checks: {self.success_count}/{self.total_checks}")
        
        if self.warnings:
            print(f"⚠️  Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if self.errors:
            print(f"❌ Errors: {len(self.errors)}")
            for error in self.errors:
                print(f"   • {error}")
        
        print("\n" + "="*60)
        
        if not self.errors:
            if self.warnings:
                print("🎉 Migration validation passed with warnings!")
                print("   Your setup should work, but consider addressing the warnings above.")
            else:
                print("🎉 Migration validation passed completely!")
                print("   Your Stagehand setup is ready to use.")
        else:
            print("❌ Migration validation failed!")
            print("   Please address the errors above before using Stagehand.")
        
        print("="*60)
        
        return len(self.errors) == 0


async def main():
    """Run migration validation."""
    print("🚀 Stagehand Migration Validation")
    print("This script validates your migration from Browserbase to local setup.")
    print("="*60)
    
    validator = MigrationValidator()
    
    # Run validation steps
    validator.validate_environment()
    validator.validate_configuration()
    await validator.validate_runtime()
    validator.validate_file_cleanup()
    
    # Print summary and exit
    success = validator.print_summary()
    
    if success:
        print("\n📚 Next steps:")
        print("1. Run your existing automation scripts to test them")
        print("2. Update any remaining test configurations")
        print("3. Check the examples/ directory for reference implementations")
        print("4. Review docs/migration_guide.md for additional tips")
    else:
        print("\n🔧 Troubleshooting:")
        print("1. Check docs/troubleshooting.md for common issues")
        print("2. Run the migration utility: python docs/migration_utility.py")
        print("3. Enable verbose logging in your configuration")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())