docker build -t externalipdiscordbot . && docker run -it --rm --name "externalipdiscordbot" -v "$(pwd)/.env:/app/.env:ro" -v "$(pwd)/commands.json:/app/commands.json:ro" externalipdiscordbot
