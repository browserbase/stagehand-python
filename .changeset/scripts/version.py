#!/usr/bin/env python3
"""
Version management script - Processes changesets and bumps version.
"""

import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import click

# No TOML dependency needed - we'll use regex parsing


CHANGESET_DIR = Path(".changeset")
CONFIG_FILE = CHANGESET_DIR / "config.json"


def load_config() -> Dict:
    """Load changeset configuration."""
    if not CONFIG_FILE.exists():
        click.echo(click.style("❌ No changeset config found.", fg="red"))
        sys.exit(1)
    
    with open(CONFIG_FILE) as f:
        return json.load(f)


def parse_changeset(filepath: Path) -> Tuple[str, str, str]:
    """Parse a changeset file and return (package, change_type, description)."""
    with open(filepath) as f:
        content = f.read()
    
    # Parse frontmatter
    lines = content.strip().split("\n")
    
    if lines[0] != "---":
        raise ValueError(f"Invalid changeset format in {filepath}")
    
    # Find end of frontmatter
    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line == "---":
            end_idx = i
            break
    
    if end_idx is None:
        raise ValueError(f"Invalid changeset format in {filepath}")
    
    # Parse package and change type
    for line in lines[1:end_idx]:
        if line.strip():
            match = re.match(r'"(.+)":\s*(\w+)', line.strip())
            if match:
                package = match.group(1)
                change_type = match.group(2)
                break
    else:
        raise ValueError(f"Could not parse package and change type from {filepath}")
    
    # Get description (everything after frontmatter)
    description = "\n".join(lines[end_idx + 1:]).strip()
    
    return package, change_type, description


def get_changesets() -> List[Tuple[Path, str, str, str]]:
    """Get all changeset files and parse them."""
    changesets = []
    
    for filepath in CHANGESET_DIR.glob("*.md"):
        if filepath.name == "README.md":
            continue
        
        try:
            package, change_type, description = parse_changeset(filepath)
            changesets.append((filepath, package, change_type, description))
        except Exception as e:
            click.echo(click.style(f"⚠️  Error parsing {filepath}: {e}", fg="yellow"))
    
    return changesets


def determine_version_bump(changesets: List[Tuple[Path, str, str, str]]) -> str:
    """Determine the version bump type based on changesets."""
    has_major = any(ct == "major" for _, _, ct, _ in changesets)
    has_minor = any(ct == "minor" for _, _, ct, _ in changesets)
    
    if has_major:
        return "major"
    elif has_minor:
        return "minor"
    else:
        return "patch"


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """Parse semantic version string."""
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", version_str)
    if not match:
        raise ValueError(f"Invalid version format: {version_str}")
    
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def bump_version(current_version: str, bump_type: str) -> str:
    """Bump version based on type."""
    major, minor, patch = parse_version(current_version)
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    else:  # patch
        return f"{major}.{minor}.{patch + 1}"




def update_pyproject_version(filepath: Path, new_version: str):
    """Update version in pyproject.toml."""
    # Read the file as text to preserve formatting
    with open(filepath) as f:
        content = f.read()
    
    # Update version using regex
    content = re.sub(
        r'(version\s*=\s*")[^"]+(")',
        f'\\g<1>{new_version}\\g<2>',
        content
    )
    
    # Write back
    with open(filepath, "w") as f:
        f.write(content)


def get_current_version(config: Dict) -> str:
    """Get current version from pyproject.toml."""
    pyproject_path = Path(config["package"]["pyprojectPath"])
    
    with open(pyproject_path) as f:
        content = f.read()
    
    # Extract version using regex
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if match:
        return match.group(1)
    else:
        raise ValueError("Could not find version in pyproject.toml")


@click.command()
@click.option("--dry-run", is_flag=True, help="Show what would be done without making changes")
@click.option("--skip-changelog", is_flag=True, help="Skip changelog generation")
def main(dry_run: bool, skip_changelog: bool):
    """Process changesets and bump version."""
    
    click.echo(click.style("📦 Processing changesets...\n", fg="cyan", bold=True))
    
    config = load_config()
    changesets = get_changesets()
    
    if not changesets:
        click.echo(click.style("No changesets found. Nothing to do!", fg="yellow"))
        return
    
    # Show changesets
    click.echo(click.style(f"Found {len(changesets)} changeset(s):", fg="green"))
    for filepath, package, change_type, desc in changesets:
        emoji = config["changeTypes"].get(change_type, {}).get("emoji", "")
        desc_line = desc.split('\n')[0][:60]
        click.echo(f"  {emoji} {change_type}: {desc_line}...")
    
    # Determine version bump
    bump_type = determine_version_bump(changesets)
    current_version = get_current_version(config)
    new_version = bump_version(current_version, bump_type)
    
    click.echo(f"\n📊 Version bump: {current_version} → {new_version} ({bump_type})")
    
    if dry_run:
        click.echo(click.style("\n🔍 Dry run - no changes made", fg="yellow"))
        return
    
    # Update version in files
    click.echo(click.style("\n📝 Updating version files...", fg="cyan"))
    
    # Update __init__.py
    version_file = Path(config["package"]["versionPath"])
    
    with open(version_file) as f:
        content = f.read()
    
    # Simple regex replacement for __version__ = "x.y.z"
    content = re.sub(
        r'(__version__\s*=\s*")[^"]+(")',
        f'\\g<1>{new_version}\\g<2>',
        content
    )
    
    with open(version_file, "w") as f:
        f.write(content)
    click.echo(f"  ✓ Updated {version_file}")
    
    # Update pyproject.toml
    pyproject_path = Path(config["package"]["pyprojectPath"])
    update_pyproject_version(pyproject_path, new_version)
    click.echo(f"  ✓ Updated {pyproject_path}")
    
    # Generate changelog entries
    if not skip_changelog:
        click.echo(click.style("\n📜 Generating changelog entries...", fg="cyan"))
        
        changelog_entries = []
        for filepath, package, change_type, desc in changesets:
            changelog_entries.append({
                "type": change_type,
                "description": desc,
                "changeset": filepath.name
            })
        
        # Save changelog data for the changelog script
        changelog_data = {
            "version": new_version,
            "previous_version": current_version,
            "date": None,  # Will be set by changelog script
            "entries": changelog_entries
        }
        
        with open(CHANGESET_DIR / ".changeset-data.json", "w") as f:
            json.dump(changelog_data, f, indent=2)
    
    # Archive processed changesets
    click.echo(click.style("\n🗂️  Archiving changesets...", fg="cyan"))
    
    archive_dir = CHANGESET_DIR / "archive" / new_version
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    for filepath, _, _, _ in changesets:
        shutil.move(str(filepath), str(archive_dir / filepath.name))
        click.echo(f"  ✓ Archived {filepath.name}")
    
    click.echo(click.style(f"\n✅ Version bumped to {new_version}!", fg="green", bold=True))
    click.echo(click.style("📝 Don't forget to run the changelog script next!", fg="yellow"))


if __name__ == "__main__":
    main()