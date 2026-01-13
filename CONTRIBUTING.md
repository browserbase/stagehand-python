## Setting up the environment

### With `uv`

We use [uv](https://docs.astral.sh/uv/) to manage dependencies because it will automatically provision a Python environment with the expected Python version. To set it up, run:

```sh
$ ./scripts/bootstrap
```

Or [install uv manually](https://docs.astral.sh/uv/getting-started/installation/) and run:

```sh
$ uv sync --all-extras
```

You can then run scripts using `uv run python script.py`:

```sh
uv run python script.py
```

## Modifying/Adding code

Most of the SDK is generated code. Modifications to code will be persisted between generations, but may
result in merge conflicts between manual patches and changes from the generator. The generator will never
modify the contents of the `src/stagehand/lib/` and `examples/` directories.

## Setting up the local server binary (for development)

The SDK supports running a local Stagehand server for development and testing. To use this feature, you need to download the appropriate binary for your platform.

### Quick setup

Run the download script to automatically download the correct binary:

```sh
$ uv run python scripts/download-binary.py
```

This will:
- Detect your platform (macOS, Linux, Windows) and architecture (x64, arm64)
- Download the latest stagehand-server binary from GitHub releases
- Place it in `bin/sea/` where the SDK expects to find it

### Manual download (alternative)

You can also manually download from [GitHub releases](https://github.com/browserbase/stagehand/releases):

1. Find the latest `stagehand/server vX.X.X` release
2. Download the binary for your platform:
   - macOS ARM: `stagehand-server-darwin-arm64`
   - macOS Intel: `stagehand-server-darwin-x64`
   - Linux: `stagehand-server-linux-x64` or `stagehand-server-linux-arm64`
   - Windows: `stagehand-server-win32-x64.exe` or `stagehand-server-win32-arm64.exe`
3. Rename it to match the expected format (remove `-server` from the name):
   - `stagehand-darwin-arm64`, `stagehand-linux-x64`, `stagehand-win32-x64.exe`, etc.
4. Place it in `bin/sea/` directory
5. Make it executable (Unix only): `chmod +x bin/sea/stagehand-*`

### Using an environment variable (optional)

Instead of placing the binary in `bin/sea/`, you can point to any binary location:

```sh
$ export STAGEHAND_SEA_BINARY=/path/to/your/stagehand-binary
$ uv run python test_local_mode.py
```

## Adding and running examples

All files in the `examples/` directory are not modified by the generator and can be freely edited or added to.

```py
# add an example to examples/<your-example>.py

#!/usr/bin/env -S uv run python
…
```

```sh
$ chmod +x examples/<your-example>.py
# run the example against your api
$ ./examples/<your-example>.py
```

## Using the repository from source

If you’d like to use the repository from source, you can either install from git or link to a cloned repository:

To install via git:

```sh
uv run pip install git+ssh://git@github.com/browserbase/stagehand-python#stainless.git
```

Alternatively, you can build from source and install the wheel file:

Building this package will create two files in the `dist/` directory, a `.tar.gz` containing the source files and a `.whl` that can be used to install the package efficiently.

To create a distributable version of the library, all you have to do is run this command:

```sh
$ uv build
# or
$ uv run python -m build
```

Then to install:

```sh
uv run pip install ./path-to-wheel-file.whl
```

## Running tests

Most tests require you to [set up a mock server](https://github.com/stoplightio/prism) against the OpenAPI spec to run the tests.

```sh
# you will need npm installed
$ npx prism mock path/to/your/openapi.yml
```

```sh
$ uv run -- ./scripts/test
```

## Linting and formatting

This repository uses [ruff](https://github.com/astral-sh/ruff) and
[black](https://github.com/psf/black) to format the code in the repository.

To lint:

```sh
$ uv run -- ./scripts/lint
```

To format and fix all ruff issues automatically:

```sh
$ uv run -- ./scripts/format
```

## Publishing and releases

Changes made to this repository via the automated release PR pipeline should publish to PyPI automatically. If
the changes aren't made through the automated pipeline, you may want to make releases manually.

### Publish with a GitHub workflow

You can release to package managers by using [the `Publish PyPI` GitHub action](https://www.github.com/browserbase/stagehand-python/actions/workflows/publish-pypi.yml). This requires a setup organization or repository secret to be set up.

### Publish manually

If you need to manually release a package, you can run the `bin/publish-pypi` script with a `PYPI_TOKEN` set on
the environment.
