import discord, os
from discord.ext import commands

from dotenv import load_dotenv

# Globals:
load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENAPI_KEY = os.environ.get("OPENAPI_KEY")
STABILITYAI_KEY = os.environ.get("STABILITYAI_KEY")

BOT = commands.Bot(command_prefix="!" , intents=discord.Intents().all())

# Methods:

# Commands:
@BOT.event
async def on_ready():
    print(f'{BOT.user} has connected to Discord!')

    await BOT.load_extension("extensions.StabilityAI")

    print("🟢 | Loaded StabilityAI extension")

    await BOT.tree.sync()

# Main execution:
if __name__ == "__main__":
    BOT.run(BOT_TOKEN)