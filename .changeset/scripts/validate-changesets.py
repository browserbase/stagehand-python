#!/usr/bin/env python3
"""
Validate changeset files format.
"""

import re
import sys
from pathlib import Path

import click


def validate_changeset_file(filepath: Path) -> bool:
    """Validate a changeset file format."""
    try:
        with open(filepath) as f:
            content = f.read()
        
        lines = content.strip().split("\n")
        
        # Check frontmatter
        if len(lines) < 3 or lines[0] != "---":
            click.echo(f"❌ {filepath}: Missing or invalid frontmatter start")
            return False
        
        # Find end of frontmatter
        end_idx = None
        for i, line in enumerate(lines[1:], 1):
            if line == "---":
                end_idx = i
                break
        
        if end_idx is None:
            click.echo(f"❌ {filepath}: Missing frontmatter end")
            return False
        
        # Validate package and change type
        found_valid_entry = False
        for line in lines[1:end_idx]:
            if line.strip():
                match = re.match(r'^"([^"]+)":\s*(major|minor|patch)$', line.strip())
                if match:
                    found_valid_entry = True
                    break
        
        if not found_valid_entry:
            click.echo(f"❌ {filepath}: Invalid package/change type format")
            return False
        
        # Check for description
        description = "\n".join(lines[end_idx + 1:]).strip()
        if not description:
            click.echo(f"❌ {filepath}: Missing change description")
            return False
        
        click.echo(f"✅ {filepath}: Valid changeset")
        return True
        
    except Exception as e:
        click.echo(f"❌ {filepath}: Error reading file: {e}")
        return False


@click.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True))
def main(files):
    """Validate changeset files."""
    if not files:
        sys.exit(0)
    
    all_valid = True
    for filepath in files:
        path = Path(filepath)
        if path.name != "README.md" and path.suffix == ".md":
            if not validate_changeset_file(path):
                all_valid = False
    
    if not all_valid:
        sys.exit(1)


if __name__ == "__main__":
    main()