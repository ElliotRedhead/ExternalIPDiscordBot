import os
import logging
import socket
import discord

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


async def port_is_open(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except Exception as exception:
        print(f"Could not connect through specified port. {exception}")
        return False


def get_external_ip():
    try:
        return (
            urllib.request.urlopen("https://checkip.amazonaws.com")
            .read()
            .decode("utf8")
        )
    except urllib.error.URLError as error:
        logging.error(error)
        print(f"Could not connect to the specified URL, reason: {error.reason}")


@bot.event
async def on_ready():
    logging.info("Discord bot startup complete, ready to accept requests.")
    status = discord.Game(get_external_ip())
    await bot.change_presence(
        status=discord.Status.online,
        activity=status,
    ),
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
    external_ip = get_external_ip()
    try:
        if await port_is_open(external_ip, PING_PORT):
            logging.info("Connection successfully made to server.")
            await context.send(
                f"The server is running, connect with: `client.connect {external_ip}:{CONNECTION_PORT}`"
            )
        else:
            logging.info("Connection could not be made to server.")
            await context.send(
                f"The server may not be running, to attempt connection regardless: `client.connect {external_ip}:{CONNECTION_PORT}`"
            )
    except Exception as exception:
        logging.warn(exception)
        await context.send(
            "This service encountered an unexpected error, please try again later."
        )


bot.run(TOKEN)
