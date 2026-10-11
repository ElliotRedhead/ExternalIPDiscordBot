import asyncio
import json
import logging
import os

import aiohttp
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise SystemExit("DISCORD_TOKEN is not set, add it to the .env file.")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
logging.basicConfig(
    handlers=[logging.FileHandler("externalipdiscordbot.log"), logging.StreamHandler()],
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)

# Lines that host scripts append to this file (e.g. out-of-memory kills)
# are sent to the bot's owner as direct messages.
ALERTS_FILE = "alerts/alerts.log"
alerts_read_offset = None


async def port_is_open(ip, port):
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, int(port)), timeout=5
        )
        writer.close()
        await writer.wait_closed()
        return True
    except Exception as exception:
        logging.info(f"Could not connect through specified port. {exception}")
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
        logging.error(f"Could not connect to the specified URL, reason: {error}")
        return None


def load_command_settings():
    with open("commands.json") as file:
        json_data = json.load(file)
    for server_instance in json_data:
        create_command(
            server_instance["name"],
            server_instance["ping_port"],
            server_instance["connection_port"],
        )


@tasks.loop(minutes=5)
async def update_status():
    external_ip = await get_external_ip()
    if external_ip is not None:
        status = discord.Game(external_ip)
        await bot.change_presence(
            status=discord.Status.online,
            activity=status,
        )
    return external_ip


@tasks.loop(seconds=30)
async def forward_alerts():
    global alerts_read_offset
    try:
        alerts_size = os.path.getsize(ALERTS_FILE)
    except OSError:
        # no file yet: everything written to it later is new
        alerts_read_offset = 0
        return
    if alerts_read_offset is None:
        # skip alerts written before the bot started
        alerts_read_offset = alerts_size
        return
    if alerts_size < alerts_read_offset:
        # the file was truncated or replaced, start again from the top
        alerts_read_offset = 0
    if alerts_size == alerts_read_offset:
        return
    with open(ALERTS_FILE) as file:
        file.seek(alerts_read_offset)
        new_alerts = file.read()
        alerts_read_offset = file.tell()
    owner = (await bot.application_info()).owner
    for alert in new_alerts.splitlines():
        if alert.strip():
            logging.info(f"Sending alert: {alert}")
            try:
                await owner.send(alert)
            except discord.HTTPException as error:
                logging.error(f"Could not send alert to {owner}: {error}")


@bot.event
async def on_ready():
    logging.info("Discord bot startup complete, ready to accept requests.")
    if not update_status.is_running():
        update_status.start()
    if not forward_alerts.is_running():
        forward_alerts.start()
    for guild in bot.guilds:
        logging.info(
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
                    f"Connection successfully made to {name} server on {ping_port}."
                )
                await context.send(
                    f"The server is running, connect with: `client.connect {external_ip}:{connection_port}`"
                )
            else:
                logging.info(
                    f"Connection could not be made to {name} server on {ping_port}."
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


@bot.command(name="refresh_status", help="Refreshes the external IP output.")
async def refresh_discord_status(context):
    external_ip = await update_status()
    if external_ip is None:
        await context.send(
            "Could not determine the server's external IP, please try again later."
        )
        return
    await context.send(f"Discord status refreshed with IP:{external_ip}")


load_command_settings()
bot.run(TOKEN, log_handler=None)
