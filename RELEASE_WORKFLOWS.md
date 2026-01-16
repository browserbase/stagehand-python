# Release + publish workflow

This repo publishes the `stagehand` Python package to PyPI when a **GitHub Release** is published. The release is currently initiated manually via the `release-please` CLI.

## Chronological flow (step-by-step)

1. Run `pnpx release-please release-pr` (local machine).
   - Opens/updates a Release PR to `main` with version + `CHANGELOG.md` updates.
2. Merge the Release PR into `main`.
3. Run `pnpx release-please github-release` (local machine).
   - Publishes the GitHub Release + git tag.
4. Wait for GitHub Actions to publish to PyPI (automatic).
   - Trigger: GitHub Release `published` event runs `.github/workflows/publish-pypi.yml`.
   - Builds platform wheels that embed the Stagehand server binary (downloaded from the latest `stagehand-server/v*` GitHub Release in `browserbase/stagehand`), then publishes to PyPI.

## Important implementation notes

- **Server binary bundling into wheels**
  - `.github/workflows/publish-pypi.yml` downloads the prebuilt Stagehand server SEA binary from the latest `stagehand-server/v*` GitHub Release in `browserbase/stagehand`, then places it into `src/stagehand/_sea/*` before running `uv build --wheel`.
- **Stagehand server version selection (current behavior)**
  - `publish-pypi.yml` resolves the latest GitHub Release tag matching `stagehand-server/v*` from `browserbase/stagehand` and downloads the matching `stagehand-server-<platform>` release asset for each wheel build.
- **Secrets**
  - PyPI publish uses `secrets.STAGEHAND_PYPI_TOKEN || secrets.PYPI_TOKEN`.
  - `.github/workflows/release-doctor.yml` runs `bin/check-release-environment` on qualifying PRs and fails if `PYPI_TOKEN` is missing.
