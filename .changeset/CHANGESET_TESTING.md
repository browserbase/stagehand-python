# Testing the Changeset System

This document explains how to test the changeset system implementation.

## Quick Test

Run the automated test suite:
```bash
./test_changesets.py
# or
python3 test_changesets.py
```

This will:
1. Backup your current files
2. Test all components of the changeset system
3. Restore your files to their original state
4. Show a summary of test results

## Manual Testing

### 1. Create a Changeset

```bash
# Interactive mode
./changeset

# Or with parameters
python3 .changeset/scripts/changeset.py --type patch --message "Fixed a bug"
```

### 2. Test Version Bumping

```bash
# Dry run to see what would happen
python3 .changeset/scripts/version.py --dry-run

# Actually bump the version
python3 .changeset/scripts/version.py
```

### 3. Test Changelog Generation

```bash
# Dry run to preview changelog
python3 .changeset/scripts/changelog.py --dry-run

# Generate changelog
python3 .changeset/scripts/changelog.py
```

### 4. Test Pre-commit Hooks

```bash
# Validate changeset files
python3 .changeset/scripts/validate-changesets.py .changeset/*.md

# Check if changeset exists (will fail on main branch)
python3 .changeset/scripts/check-changeset.py
```

## GitHub Actions Testing

The GitHub Actions will trigger when:
1. **Push to main**: Creates/updates a "Version Packages" PR
2. **Merge version PR**: Publishes to PyPI and creates GitHub release

To test locally:
1. Create a feature branch
2. Make some changes
3. Create a changeset: `./changeset`
4. Commit and push
5. Open PR to main
6. When merged, the actions will run

## Expected Behavior

### Changeset Creation
- Creates a markdown file in `.changeset/` with a random name
- File contains package name, change type, and description
- Shows changed files compared to main branch

### Version Bumping
- Reads all changesets
- Determines version bump (major > minor > patch)
- Updates version in `pyproject.toml` and `__init__.py`
- Archives processed changesets
- Creates data file for changelog generation

### Changelog Generation
- Reads changeset data from version script
- Generates formatted changelog entry
- Updates CHANGELOG.md with new version section
- Groups changes by type (major/minor/patch)

### GitHub Actions
- `changesets.yml`: Runs on push to main
- `changeset-publish.yml`: Runs when version PR is merged
- Creates PR with version bumps and changelog updates
- Publishes to PyPI when PR is merged

## Troubleshooting

### "No changeset found" error
- Make sure you're not on main/master branch
- Create a changeset with `./changeset`
- Check `.changeset/` directory for `.md` files

### Version not bumping correctly
- Check `.changeset/config.json` is valid JSON
- Ensure changesets have correct format
- Look for error messages in script output

### Changelog not generating
- Make sure version script ran first
- Check for `.changeset/.changeset-data.json`
- Verify CHANGELOG.md exists or will be created

### Pre-commit hooks not working
- Install pre-commit: `pip install pre-commit`
- Set up hooks: `pre-commit install`
- Run manually: `pre-commit run --all-files`