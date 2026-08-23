set -e
docker build -t externalipdiscordbot .
docker rm -f externalipdiscordbot 2>/dev/null || true
docker run -d --restart unless-stopped --name "externalipdiscordbot" -v "$(pwd)/.env:/app/.env:ro" -v "$(pwd)/commands.json:/app/commands.json:ro" externalipdiscordbot
