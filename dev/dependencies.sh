curl -fsSL https://dl.yarnpkg.com/debian/pubkey.gpg | sudo gpg --yes --dearmor -o /usr/share/keyrings/yarnkey.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/yarnkey.gpg] https://dl.yarnpkg.com/debian stable main" | sudo tee /etc/apt/sources.list.d/yarn.list > /dev/null
sudo apt update
uv sync
source /workspaces/isis_report/.venv/bin/activate
playwright install chromium --with-deps --only-shell
