#!/usr/bin/env python3
"""
Changeset CLI - Interactive tool for creating changeset files.
Similar to JavaScript changesets but for Python projects.
"""

import json
import os
import random
import string
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import click
import git


CHANGESET_DIR = Path(".changeset")
CONFIG_FILE = CHANGESET_DIR / "config.json"


def load_config() -> Dict:
    """Load changeset configuration."""
    if not CONFIG_FILE.exists():
        click.echo(click.style("❌ No changeset config found. Please run from project root.", fg="red"))
        sys.exit(1)
    
    with open(CONFIG_FILE) as f:
        return json.load(f)


def get_changed_files() -> List[str]:
    """Get list of changed files compared to base branch."""
    config = load_config()
    base_branch = config.get("baseBranch", "main")
    
    try:
        repo = git.Repo(".")
        
        # Get current branch
        current_branch = repo.active_branch.name
        
        # Get diff between current branch and base
        diff_output = repo.git.diff(f"{base_branch}...HEAD", "--name-only")
        
        if not diff_output:
            return []
            
        return diff_output.strip().split("\n")
    except Exception as e:
        click.echo(click.style(f"Error getting changed files: {e}", fg="yellow"))
        return []


def generate_changeset_name() -> str:
    """Generate a random changeset filename like 'warm-chefs-sell'."""
    adjectives = [
        "warm", "cool", "fast", "slow", "bright", "dark", "soft", "hard",
        "sweet", "sour", "fresh", "stale", "new", "old", "big", "small",
        "happy", "sad", "brave", "shy", "clever", "silly", "calm", "wild"
    ]
    
    nouns = [
        "dogs", "cats", "birds", "fish", "lions", "bears", "rabbits", "foxes",
        "chefs", "artists", "writers", "singers", "dancers", "actors", "poets", "musicians",
        "stars", "moons", "suns", "clouds", "rivers", "mountains", "oceans", "forests"
    ]
    
    verbs = [
        "run", "jump", "sing", "dance", "write", "paint", "cook", "bake",
        "sell", "buy", "trade", "share", "give", "take", "make", "break",
        "fly", "swim", "walk", "talk", "think", "dream", "play", "work"
    ]
    
    return f"{random.choice(adjectives)}-{random.choice(nouns)}-{random.choice(verbs)}"


def create_changeset(change_type: str, description: str) -> str:
    """Create a changeset file and return its path."""
    config = load_config()
    package_name = config["package"]["name"]
    
    # Generate filename
    filename = f"{generate_changeset_name()}.md"
    filepath = CHANGESET_DIR / filename
    
    # Create changeset content
    content = f"""---
"{package_name}": {change_type}
---

{description}
"""
    
    with open(filepath, "w") as f:
        f.write(content)
    
    return str(filepath)


@click.command()
@click.option("--type", type=click.Choice(["major", "minor", "patch"]), help="Change type (if not provided, will prompt)")
@click.option("--message", "-m", help="Change description (if not provided, will prompt)")
def main(type: Optional[str], message: Optional[str]):
    """Create a new changeset for tracking changes."""
    
    click.echo(click.style("🦋 Creating a new changeset...\n", fg="cyan", bold=True))
    
    # Check for changed files
    changed_files = get_changed_files()
    
    if changed_files:
        click.echo(click.style("📝 Changed files detected:", fg="green"))
        for file in changed_files[:10]:  # Show first 10 files
            click.echo(f"   • {file}")
        if len(changed_files) > 10:
            click.echo(f"   ... and {len(changed_files) - 10} more files")
        click.echo()
    
    # Load config for change types
    config = load_config()
    change_types = config.get("changeTypes", {})
    
    # Prompt for change type if not provided
    if not type:
        click.echo(click.style("What kind of change is this?", fg="yellow", bold=True))
        
        choices = []
        for ct, info in change_types.items():
            emoji = info.get("emoji", "")
            desc = info.get("description", ct)
            choices.append(f"{emoji} {ct} - {desc}")
        
        for i, choice in enumerate(choices, 1):
            click.echo(f"  {i}) {choice}")
        
        choice_num = click.prompt("\nSelect change type", type=int)
        
        if 1 <= choice_num <= len(change_types):
            type = list(change_types.keys())[choice_num - 1]
        else:
            click.echo(click.style("Invalid choice!", fg="red"))
            sys.exit(1)
    
    # Prompt for description if not provided
    if not message:
        click.echo(click.style("\n📝 Please describe the change:", fg="yellow", bold=True))
        click.echo(click.style("(This will be used in the changelog)", fg="bright_black"))
        
        message = click.prompt("Description", type=str)
        
        if not message.strip():
            click.echo(click.style("Description cannot be empty!", fg="red"))
            sys.exit(1)
    
    # Create the changeset
    changeset_path = create_changeset(type, message.strip())
    
    click.echo(click.style(f"\n✅ Changeset created: {changeset_path}", fg="green", bold=True))
    
    # Show preview
    click.echo(click.style("\nPreview:", fg="cyan"))
    with open(changeset_path) as f:
        content = f.read()
        for line in content.split("\n"):
            if line.strip():
                click.echo(f"  {line}")
    
    click.echo(click.style("\n💡 Tip: Commit this changeset with your changes!", fg="bright_black"))


if __name__ == "__main__":
    main()