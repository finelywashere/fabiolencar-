import discord
from discord.ext import commands
import asyncio
from config import TOKEN

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="/", intents=intents)

INITIAL_EXTENSIONS = [
    "cogs.moderation",
    "cogs.automod",
    "cogs.tickets",
    "cogs.economy",
    "cogs.help",
    "cogs.antinuke"
]

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

async def load_extensions():
    for ext in INITIAL_EXTENSIONS:
        await bot.load_extension(ext)

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

asyncio.run(main())
