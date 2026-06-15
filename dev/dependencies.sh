#!/usr/bin/env bash
set -euo pipefail

curl -fsSL https://dl.yarnpkg.com/debian/pubkey.gpg | sudo gpg --yes --dearmor -o /usr/share/keyrings/yarnkey.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/yarnkey.gpg] https://dl.yarnpkg.com/debian stable main" | sudo tee /etc/apt/sources.list.d/yarn.list > /dev/null
sudo apt update

# Use `uv` to sync dependencies from pyproject.toml into the project's virtualenv
if ! command -v uv >/dev/null 2>&1; then
	echo "uv not found in PATH. Install uv (e.g. 'pip install uv') or make it available before running this script."
	exit 1
fi

echo "Running 'uv sync' to install project dependencies from pyproject.toml..."
uv sync

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
