#!/usr/bin/env python3
"""
Stagehand Browserbase Migration Utility

This script helps users migrate from Browserbase-based configurations to the new local-only setup.
It analyzes existing code and provides migration suggestions.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse


class BrowserbaseMigrationAnalyzer:
    """Analyzes code for Browserbase usage and suggests migrations."""
    
    def __init__(self):
        self.browserbase_patterns = [
            r'env\s*=\s*["\']BROWSERBASE["\']',
            r'BROWSERBASE',
            r'browserbase_session_id',
            r'browserbase_session_create_params',
            r'api_key\s*=.*browserbase',
            r'project_id\s*=',
            r'api_url\s*=.*browserbase',
            r'use_api\s*=\s*True',
            r'connect_browserbase_browser',
            r'from browserbase import',
            r'import browserbase',
        ]
        
        self.migration_suggestions = {
            'env="BROWSERBASE"': 'Remove env parameter (defaults to local mode)',
            'api_key=': 'Move to model_client_options["api_key"] for LLM API key',
            'project_id=': 'Remove project_id (not needed for local mode)',
            'api_url=': 'Remove api_url (not needed for local mode)',
            'browserbase_session_id=': 'Remove browserbase_session_id',
            'browserbase_session_create_params=': 'Remove browserbase_session_create_params',
            'use_api=True': 'Remove use_api parameter',
            'connect_browserbase_browser': 'Use connect_browser instead',
            'from browserbase import': 'Remove browserbase imports',
            'import browserbase': 'Remove browserbase imports',
        }

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file for Browserbase usage."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {'error': f'Could not read file: {e}'}
        
        issues = []
        for pattern in self.browserbase_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                matched_text = match.group()
                suggestion = self._get_suggestion(matched_text)
                issues.append({
                    'line': line_num,
                    'text': matched_text,
                    'suggestion': suggestion,
                    'pattern': pattern
                })
        
        return {
            'file': str(file_path),
            'issues': issues,
            'needs_migration': len(issues) > 0
        }

    def _get_suggestion(self, matched_text: str) -> str:
        """Get migration suggestion for matched text."""
        for key, suggestion in self.migration_suggestions.items():
            if key.lower() in matched_text.lower():
                return suggestion
        return 'Review and update according to migration guide'

    def analyze_directory(self, directory: Path, extensions: List[str] = None) -> List[Dict[str, Any]]:
        """Analyze all files in a directory."""
        if extensions is None:
            extensions = ['.py', '.ipynb', '.md', '.txt']
        
        results = []
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                # Skip certain directories
                if any(skip in str(file_path) for skip in ['.git', '__pycache__', '.pytest_cache', 'node_modules']):
                    continue
                
                result = self.analyze_file(file_path)
                if result.get('needs_migration', False):
                    results.append(result)
        
        return results


def generate_migration_config(old_config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate new configuration from old Browserbase configuration."""
    new_config = {}
    
    # Copy non-Browserbase fields
    keep_fields = [
        'model_name', 'verbose', 'logger', 'use_rich_logging',
        'dom_settle_timeout_ms', 'enable_caching', 'self_heal',
        'wait_for_captcha_solves', 'system_prompt', 'experimental'
    ]
    
    for field in keep_fields:
        if field in old_config:
            new_config[field] = old_config[field]
    
    # Handle model API configuration
    model_client_options = {}
    
    # Move API key to model_client_options if it was for LLM
    if 'model_api_key' in old_config:
        model_client_options['api_key'] = old_config['model_api_key']
    
    # Add custom API base if needed
    if 'custom_api_base' in old_config:
        model_client_options['api_base'] = old_config['custom_api_base']
    
    if model_client_options:
        new_config['model_client_options'] = model_client_options
    
    # Handle browser launch options
    browser_options = {}
    if 'headless' in old_config:
        browser_options['headless'] = old_config['headless']
    if 'viewport' in old_config:
        browser_options['viewport'] = old_config['viewport']
    
    if browser_options:
        new_config['local_browser_launch_options'] = browser_options
    
    return new_config


def print_migration_report(results: List[Dict[str, Any]]):
    """Print a detailed migration report."""
    print("=" * 60)
    print("STAGEHAND BROWSERBASE MIGRATION REPORT")
    print("=" * 60)
    
    if not results:
        print("✅ No Browserbase usage detected. Your code appears to be already migrated!")
        return
    
    print(f"Found {len(results)} files that need migration:\n")
    
    for result in results:
        print(f"📁 File: {result['file']}")
        print(f"   Issues found: {len(result['issues'])}")
        
        for issue in result['issues']:
            print(f"   Line {issue['line']}: {issue['text']}")
            print(f"   → {issue['suggestion']}")
        print()
    
    print("=" * 60)
    print("NEXT STEPS:")
    print("1. Review the migration guide: docs/migration_guide.md")
    print("2. Update your configuration according to the suggestions above")
    print("3. Test your updated code with the new local-only setup")
    print("4. Remove browserbase from your requirements.txt")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Migrate from Browserbase to local Stagehand setup')
    parser.add_argument('path', nargs='?', default='.', help='Path to analyze (default: current directory)')
    parser.add_argument('--extensions', nargs='+', default=['.py', '.ipynb', '.md'], 
                       help='File extensions to analyze')
    parser.add_argument('--config-example', action='store_true',
                       help='Show configuration migration example')
    
    args = parser.parse_args()
    
    if args.config_example:
        print("Configuration Migration Example:")
        print("=" * 40)
        print("OLD (Browserbase):")
        print("""
from stagehand import StagehandConfig

config = StagehandConfig(
    env="BROWSERBASE",
    api_key="bb_your_browserbase_key",
    project_id="your_project_id",
    model_name="gpt-4o",
    model_api_key="your_openai_key"
)
        """)
        
        print("NEW (Local):")
        print("""
from stagehand import StagehandConfig

config = StagehandConfig(
    model_name="gpt-4o",
    model_client_options={
        "api_key": "your_openai_key"
    },
    local_browser_launch_options={
        "headless": False
    }
)
        """)
        return
    
    analyzer = BrowserbaseMigrationAnalyzer()
    path = Path(args.path)
    
    if not path.exists():
        print(f"Error: Path '{path}' does not exist")
        sys.exit(1)
    
    print(f"Analyzing {path} for Browserbase usage...")
    
    if path.is_file():
        results = [analyzer.analyze_file(path)]
        results = [r for r in results if r.get('needs_migration', False)]
    else:
        results = analyzer.analyze_directory(path, args.extensions)
    
    print_migration_report(results)


if __name__ == '__main__':
    main()