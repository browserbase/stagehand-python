#!/usr/bin/env python3
"""
Changelog generation script - Generates changelog from processed changesets.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import click


CHANGESET_DIR = Path(".changeset")
CONFIG_FILE = CHANGESET_DIR / "config.json"
CHANGELOG_FILE = Path("CHANGELOG.md")


def load_config() -> Dict:
    """Load changeset configuration."""
    if not CONFIG_FILE.exists():
        click.echo(click.style("❌ No changeset config found.", fg="red"))
        sys.exit(1)
    
    with open(CONFIG_FILE) as f:
        return json.load(f)


def load_changeset_data() -> Optional[Dict]:
    """Load processed changeset data."""
    data_file = CHANGESET_DIR / ".changeset-data.json"
    
    if not data_file.exists():
        return None
    
    with open(data_file) as f:
        data = json.load(f)
    
    # Set current date if not set
    if data.get("date") is None:
        data["date"] = datetime.now().strftime("%Y-%m-%d")
    
    return data


def get_pr_info() -> Optional[Dict[str, str]]:
    """Get PR information if available."""
    try:
        # Try to get PR info from GitHub context (in Actions)
        pr_number = os.environ.get("GITHUB_PR_NUMBER")
        if pr_number:
            return {
                "number": pr_number,
                "url": f"https://github.com/{os.environ.get('GITHUB_REPOSITORY')}/pull/{pr_number}"
            }
        
        # Try to get from git branch name (if it contains PR number)
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            branch = result.stdout.strip()
            # Look for patterns like "pr-123" or "pull/123"
            match = re.search(r'(?:pr|pull)[/-](\d+)', branch, re.IGNORECASE)
            if match:
                pr_number = match.group(1)
                # Try to get repo info
                repo_result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    capture_output=True,
                    text=True
                )
                if repo_result.returncode == 0:
                    repo_url = repo_result.stdout.strip()
                    # Extract owner/repo from URL
                    match = re.search(r'github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$', repo_url)
                    if match:
                        repo = match.group(1)
                        return {
                            "number": pr_number,
                            "url": f"https://github.com/{repo}/pull/{pr_number}"
                        }
    except Exception:
        pass
    
    return None


def format_changelog_entry(entry: Dict, config: Dict) -> str:
    """Format a single changelog entry."""
    change_type = entry["type"]
    description = entry["description"]
    
    # Get emoji if configured
    emoji = config["changeTypes"].get(change_type, {}).get("emoji", "")
    
    # Format entry
    if emoji:
        line = f"- {emoji} **{change_type}**: {description}"
    else:
        line = f"- **{change_type}**: {description}"
    
    return line


def generate_version_section(data: Dict, config: Dict) -> str:
    """Generate changelog section for a version."""
    version = data["version"]
    date = data["date"]
    entries = data["entries"]
    
    # Start with version header
    section = f"## [{version}] - {date}\n\n"
    
    # Get PR info if available
    pr_info = get_pr_info()
    if pr_info:
        section += f"[View Pull Request]({pr_info['url']})\n\n"
    
    # Group entries by type
    grouped = {}
    for entry in entries:
        change_type = entry["type"]
        if change_type not in grouped:
            grouped[change_type] = []
        grouped[change_type].append(entry)
    
    # Add entries by type (in order: major, minor, patch)
    type_order = ["major", "minor", "patch"]
    
    for change_type in type_order:
        if change_type in grouped:
            type_info = config["changeTypes"].get(change_type, {})
            type_name = type_info.get("description", change_type.capitalize())
            
            section += f"### {type_name}\n\n"
            
            for entry in grouped[change_type]:
                section += format_changelog_entry(entry, config) + "\n"
            
            section += "\n"
    
    return section.strip() + "\n"


def update_changelog(new_section: str, version: str):
    """Update the changelog file with new section."""
    if CHANGELOG_FILE.exists():
        with open(CHANGELOG_FILE) as f:
            current_content = f.read()
    else:
        # Create new changelog with header
        current_content = """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

"""
    
    # Check if version already exists
    if f"## [{version}]" in current_content:
        click.echo(click.style(f"⚠️  Version {version} already exists in changelog", fg="yellow"))
        return False
    
    # Find where to insert (after the header, before first version)
    lines = current_content.split("\n")
    insert_index = None
    
    # Look for first version entry or end of header
    for i, line in enumerate(lines):
        if line.startswith("## ["):
            insert_index = i
            break
    
    if insert_index is None:
        # No versions yet, add at the end
        new_content = current_content.rstrip() + "\n\n" + new_section + "\n"
    else:
        # Insert before first version
        lines.insert(insert_index, new_section)
        lines.insert(insert_index + 1, "")  # Add blank line
        new_content = "\n".join(lines)
    
    # Write updated changelog
    with open(CHANGELOG_FILE, "w") as f:
        f.write(new_content)
    
    return True


@click.command()
@click.option("--dry-run", is_flag=True, help="Show what would be added without making changes")
@click.option("--date", help="Override the date (YYYY-MM-DD format)")
def main(dry_run: bool, date: Optional[str]):
    """Generate changelog from processed changesets."""
    
    click.echo(click.style("📜 Generating changelog...\n", fg="cyan", bold=True))
    
    config = load_config()
    data = load_changeset_data()
    
    if not data:
        click.echo(click.style("No changeset data found. Run version script first!", fg="red"))
        return
    
    # Override date if provided
    if date:
        data["date"] = date
    
    # Generate changelog section
    new_section = generate_version_section(data, config)
    
    click.echo(click.style("Generated changelog entry:", fg="green"))
    click.echo("-" * 60)
    click.echo(new_section)
    click.echo("-" * 60)
    
    if dry_run:
        click.echo(click.style("\n🔍 Dry run - no changes made", fg="yellow"))
        return
    
    # Update changelog file
    if update_changelog(new_section, data["version"]):
        click.echo(click.style(f"\n✅ Updated {CHANGELOG_FILE}", fg="green", bold=True))
        
        # Clean up data file
        data_file = CHANGESET_DIR / ".changeset-data.json"
        if data_file.exists():
            os.remove(data_file)
    else:
        click.echo(click.style("\n❌ Failed to update changelog", fg="red"))
        return
    
    # Show next steps
    click.echo(click.style("\n📝 Next steps:", fg="yellow"))
    click.echo("  1. Review the updated CHANGELOG.md")
    click.echo("  2. Commit the version and changelog changes")
    click.echo("  3. Create a pull request for the release")


if __name__ == "__main__":
    main()