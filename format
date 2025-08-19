#!/bin/bash

# Define source directories (adjust as needed)
SOURCE_DIRS="stagehand"

# Apply Black formatting first
echo "Applying Black formatting..."
black $SOURCE_DIRS

# Apply Ruff with autofix for all issues (including import sorting)
echo "Applying Ruff autofixes (including import sorting)..."
ruff check --fix $SOURCE_DIRS

echo "Checking for remaining issues..."
ruff check $SOURCE_DIRS

echo "Done! Code has been formatted and linted." 