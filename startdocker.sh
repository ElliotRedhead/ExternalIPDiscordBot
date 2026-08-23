docker build -t externalipdiscordbot . && docker run -it --rm --name "externalipdiscordbot" -v "$(pwd)/.env:/.env:ro" -v "$(pwd)/commands.json:/commands.json:ro" externalipdiscordbot
