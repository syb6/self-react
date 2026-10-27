import os
from pathlib import Path

import discord
from discord.ext import commands

env_file = Path(__file__).with_name(".env")
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        key, separator, value = line.partition("=")
        if separator and key.strip() == "TOKEN":
            os.environ.setdefault("TOKEN", value.strip().strip("\"'"))

TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("TOKEN is missing. Add it to the .env file.")

channel_input = input("Channel ID: ").strip()
try:
    TARGET_CHANNEL_ID = int(channel_input)
except ValueError as error:
    raise ValueError("Channel ID must be an integer.") from error

EMOJI_TO_REACT = input("Emoji to react with: ").strip()
if not EMOJI_TO_REACT:
    raise ValueError("Emoji cannot be empty.")

bot = commands.Bot(command_prefix=None, self_bot=True)

print(f"Watching channel ID {TARGET_CHANNEL_ID} and reacting with {EMOJI_TO_REACT}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")

@bot.event
async def on_message(message):
    # Ensure the bot doesn't crash on system messages and check the channel ID
    if message.channel.id == TARGET_CHANNEL_ID:
        try:
            await message.add_reaction(EMOJI_TO_REACT)
            print(f"Reacted to message from {message.author}")
        except Exception as e:
            print(f"Failed to react: {e}")

bot.run(TOKEN)
