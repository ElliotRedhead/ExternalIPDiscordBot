set -e
docker build -t externalipdiscordbot .
mkdir -p alerts # created here so Docker doesn't make it root-owned
docker rm -f externalipdiscordbot 2>/dev/null || true
docker run -d --restart unless-stopped --name "externalipdiscordbot" -v "$(pwd)/.env:/app/.env:ro" -v "$(pwd)/commands.json:/app/commands.json:ro" -v "$(pwd)/alerts:/app/alerts:ro" externalipdiscordbot
