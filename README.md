# ExternalIPDiscordBot

Automatically update Discord bot status to display external IP of a server, useful for non-static IPs.  
Commands to display connection instructions for each service.

## Getting Started

1. Follow the [discord documentation](https://discordpy.readthedocs.io/en/stable/discord.html)
2. `git clone` this repository
3. Create a new .env file within the downloaded repository based on the .env default format.

### Running in Docker (Simplified)

4. In a terminal navigate to the repo and run `source startdocker.sh` (Linux) or `bash startdocker.sh` (Windows).

### Running without Docker

4. Run `python externalipdiscordbot.py`

## Supporting Resources

[RealPython.com](https://realpython.com/how-to-make-a-discord-bot-python/)

## Future Iteration Points

- docstrings
- read from json
