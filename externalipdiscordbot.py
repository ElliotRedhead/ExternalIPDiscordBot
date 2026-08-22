import asyncio
import json
import logging
import os

import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
logging.basicConfig(
    filename="externalipdiscordbot.log",
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)


async def port_is_open(ip, port):
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, int(port)), timeout=5
        )
        writer.close()
        await writer.wait_closed()
        return True
    except Exception as exception:
        print(f"Could not connect through specified port. {exception}")
        return False


async def get_external_ip():
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get("https://checkip.amazonaws.com") as response:
                response.raise_for_status()
                return (await response.text()).strip()
    except (aiohttp.ClientError, asyncio.TimeoutError) as error:
        logging.error(error)
        print(f"Could not connect to the specified URL, reason: {error}")
        return None


def load_command_settings():
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
    external_ip = await get_external_ip()
    if external_ip is not None:
        status = discord.Game(external_ip)
        await bot.change_presence(
            status=discord.Status.online,
            activity=status,
        ),
    for guild in bot.guilds:
        print(
            f"{bot.user} is connected to the following guild:\n"
            f"{guild.name}(id: {guild.id})\n"
        )


def create_command(name, ping_port, connection_port):
    @bot.command(
        name=name,
        help=f"Check if {name} server is up and message the connect instructions.",
    )
    async def server_check(context):
        logging.info(f"{context.author.name} - {context.invoked_with}")
        external_ip = await get_external_ip()
        if external_ip is None:
            await context.send(
                "Could not determine the server's external IP, please try again later."
            )
            return
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
            logging.warning(exception)
            await context.send(
                "This service encountered an unexpected error, please try again later."
            )

    return server_check


load_command_settings()
bot.run(TOKEN)
