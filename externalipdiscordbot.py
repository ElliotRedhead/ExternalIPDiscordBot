import os
import logging
import socket

from discord.ext import commands
from dotenv import load_dotenv
import urllib.request

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PING_PORT = os.getenv("PING_PORT")
CONNECTION_PORT = os.getenv("CONNECTION_PORT")

bot = commands.Bot(command_prefix="!")
logging.basicConfig(
    filename="externalipdiscordbot.log",
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)


async def portIsOpen(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except Exception as exception:
        print(f"Could not connect through specified port. {exception}")
        return False


@bot.event
async def on_ready():
    logging.info("Discord bot startup complete, ready to accept requests.")
    for guild in bot.guilds:
        print(
            f"{bot.user} is connected to the following guild:\n"
            f"{guild.name}(id: {guild.id})\n"
        )


@bot.command(
    name="rust",
    help="Check if Rust game server is up and write out the command needed to connect.",
)
async def rust(context):
    logging.info(f"{context.author.name} - {context.invoked_with}")
    try:
        external_ip = urllib.request.urlopen("https://ident.me").read().decode("utf8")
    except urllib.error.URLError as error:
        logging.error(error)
        print(f"Could not connect to the specified URL, reason: {error.reason}")
    try:
        if await portIsOpen(external_ip, PING_PORT):
            logging.info("Connection successfully made to server.")
            await context.send(
                f"The server is running, connect with: `client.connect {external_ip}:{CONNECTION_PORT}`"
            )
        else:
            logging.info("Connection could not be made to server.")
            await context.send(
                f"The server may not be running, to attempt connection regardless: `client.connect {external_ip}:{CONNECTION_PORT}`"
            )
    except Exception:
        await context.send(
            "This service encountered an unexpected error, please try again later."
        )


bot.run(TOKEN)
