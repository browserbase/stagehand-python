#!/usr/bin/env python3
"""
Check if changeset exists for feature branches.
"""

import os
import sys
from pathlib import Path

import click
import git


CHANGESET_DIR = Path(".changeset")
SKIP_BRANCHES = ["main", "master", "develop", "release/*", "hotfix/*"]
SKIP_PREFIXES = ["chore/", "docs/", "test/", "ci/", "build/"]


def should_skip_branch(branch_name: str) -> bool:
    """Check if branch should skip changeset requirement."""
    # Check exact matches
    if branch_name in SKIP_BRANCHES:
        return True
    
    # Check prefixes
    for prefix in SKIP_PREFIXES:
        if branch_name.startswith(prefix):
            return True
    
    # Check patterns
    for pattern in SKIP_BRANCHES:
        if "*" in pattern:
            import fnmatch
            if fnmatch.fnmatch(branch_name, pattern):
                return True
    
    return False


@click.command()
@click.option("--skip-ci", is_flag=True, help="Skip check in CI environment")
def main(skip_ci):
    """Check if changeset exists for the current branch."""
    
    # Skip in CI if requested
    if skip_ci and os.environ.get("CI"):
        click.echo("Skipping changeset check in CI")
        sys.exit(0)
    
    try:
        repo = git.Repo(".")
        
        # Get current branch
        try:
            current_branch = repo.active_branch.name
        except TypeError:
            # Detached HEAD state (common in CI)
            click.echo("Skipping changeset check in detached HEAD state")
            sys.exit(0)
        
        # Check if we should skip this branch
        if should_skip_branch(current_branch):
            click.echo(f"Skipping changeset check for branch: {current_branch}")
            sys.exit(0)
        
        # Get uncommitted changeset files
        uncommitted_changesets = []
        for item in repo.index.entries:
            filepath = item[0]
            if filepath.startswith(".changeset/") and filepath.endswith(".md") and "README" not in filepath:
                uncommitted_changesets.append(filepath)
        
        # Get staged changeset files
        staged_changesets = []
        diff = repo.index.diff("HEAD")
        for item in diff:
            if item.a_path and item.a_path.startswith(".changeset/") and item.a_path.endswith(".md") and "README" not in item.a_path:
                staged_changesets.append(item.a_path)
        
        # Check if any changesets exist
        if uncommitted_changesets or staged_changesets:
            click.echo(f"✅ Found changeset(s) for branch: {current_branch}")
            if uncommitted_changesets:
                click.echo(f"   Uncommitted: {', '.join(uncommitted_changesets)}")
            if staged_changesets:
                click.echo(f"   Staged: {', '.join(staged_changesets)}")
            sys.exit(0)
        else:
            click.echo(f"❌ No changeset found for feature branch: {current_branch}")
            click.echo("💡 Create a changeset by running: python .changeset/scripts/changeset.py")
            click.echo("   Or use: ./changeset")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Warning: Could not check for changesets: {e}")
        # Don't fail on errors
        sys.exit(0)


if __name__ == "__main__":
    main()