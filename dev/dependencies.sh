#!/usr/bin/env bash
set -euo pipefail

# Use `uv` to sync dependencies from pyproject.toml into the project's virtualenv
if ! command -v uv >/dev/null 2>&1; then
	echo "uv not found in PATH. Install uv (e.g. 'pip install uv') or make it available before running this script."
	exit 1
fi

echo "Running 'uv sync' to install project dependencies from pyproject.toml..."
uv sync --upgrade

echo "Running 'uv lock --upgrade' to update the lock file..."
uv lock --upgrade

# Activate the virtual environment created/managed by uv (commonly .venv)
if [ -f ".venv/bin/activate" ]; then
	# shellcheck disable=SC1091
	source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
	# shellcheck disable=SC1091
	source venv/bin/activate
else
	echo "No virtualenv activation script found (.venv or venv). Proceeding without activation."
fi

# Install Playwright browsers using the active Python interpreter
echo "Installing Playwright Chromium (headless)"
python -m playwright install chromium --with-deps --only-shell

# Install OpenCode CLI tool
echo "Installing OpenCode CLI tool"
curl -fsSL https://opencode.ai/install | bash
