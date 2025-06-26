# Changesets

This directory contains changeset files that track changes to the codebase. The changeset system is inspired by the JavaScript changesets tool but adapted for Python projects.

## How it works

1. **Creating a changeset**: When you make changes that should be included in the changelog, run:
   ```bash
   python .changeset/scripts/changeset.py
   # or use the wrapper script:
   ./changeset
   ```
   
   This will prompt you to:
   - Select the type of change (major, minor, or patch)
   - Provide a description of the change
   
   A markdown file will be created in this directory with a random name like `warm-chefs-sell.md`.

2. **Version bumping**: The GitHub Action will automatically:
   - Detect changesets in PRs to main
   - Create or update a "Version Packages" PR
   - Bump the version based on the changesets
   - Update the CHANGELOG.md

3. **Publishing**: When the "Version Packages" PR is merged:
   - The package is automatically published to PyPI
   - A GitHub release is created
   - The changesets are archived

## Changeset format

Each changeset file looks like:
```markdown
---
"stagehand": patch
---

Fixed a bug in the browser automation logic
```

## Configuration

The changeset behavior is configured in `.changeset/config.json`:
- `baseBranch`: The branch to compare against (usually "main")
- `changeTypes`: Definitions for major, minor, and patch changes
- `package`: Package-specific configuration

## Best practices

1. Create a changeset for every user-facing change
2. Use clear, concise descriptions
3. Choose the appropriate change type:
   - `patch`: Bug fixes and small improvements
   - `minor`: New features that are backwards compatible
   - `major`: Breaking changes

## Workflow

1. Make your code changes
2. Run `./changeset` to create a changeset
3. Commit both your code changes and the changeset file
4. Open a PR
5. The changeset will be processed when the PR is merged to main