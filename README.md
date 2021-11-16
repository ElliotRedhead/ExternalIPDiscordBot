# ExternalIPDiscordBot

Automatically update Discord bot status to display external IP of a server, useful for non-static IPs.  
Commands to display connection instructions for each service.

## Getting Started

1. Follow the [discord documentation](https://discordpy.readthedocs.io/en/stable/discord.html)
2. `git clone` this repository
3. Create a new .env file within the downloaded repository based on the .env.default format.
4. Create a new commands.json file within the downloaded repository based on the commands.json.default format.

### Running in Docker (Simplified)

5. In a terminal navigate to the repo and run `source startdocker.sh` (Linux) or `bash startdocker.sh` (Windows).

### Running without Docker

5. Install dependencies with pip `pip install -r requirements.txt`
6. Run `python externalipdiscordbot.py`

## Supporting Resources

[RealPython.com](https://realpython.com/how-to-make-a-discord-bot-python/)

## Future Iteration Points

- docstrings
- custom response message read from json
