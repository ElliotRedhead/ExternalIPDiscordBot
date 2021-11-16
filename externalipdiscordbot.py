import json
import logging
import os
import socket
import urllib.request

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

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


async def load_command_settings():
    file = open("commands.json")
    json_data = json.load(file)
    for server_instance in json_data:
        create_command(
            server_instance["name"],
            server_instance["ping_port"],
            server_instance["connection_port"],
        )


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
    await load_command_settings()


def create_command(name, ping_port, connection_port):
    @bot.command(
        name=name,
        help=f"Check if {name} server is up and message the connect instructions.",
    )
    async def server_check(context):
        logging.info(f"{context.author.name} - {context.invoked_with}")
        external_ip = get_external_ip()
        try:
            if await port_is_open(external_ip, ping_port):
                logging.info(
                    "Connection successfully made to {name} server on {ping_port}."
                )
                await context.send(
                    f"The server is running, connect with: `client.connect {external_ip}:{connection_port}`"
                )
            else:
                logging.info(
                    "Connection could not be made to {name} server on {ping_port}."
                )
                await context.send(
                    f"The server for {name} may not be running. To attempt connection: `client.connect {external_ip}:{connection_port}`"
                )
        except Exception as exception:
            logging.warn(exception)
            await context.send(
                "This service encountered an unexpected error, please try again later."
            )

    return server_check


bot.run(TOKEN)
