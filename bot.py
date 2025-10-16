import os
import asyncio
from dotenv import load_dotenv
from discord.ext import commands
import discord

# ─── Load environment variables ───────────────────────
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))  # your test guild/server ID

# ─── Bot setup ───────────────────────────────────────
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ─── Load cogs ──────────────────────────────────────
async def load_cogs():
    """Load only actual cogs from cogs folder."""
    ignored_files = ("playlist.py", "views.py")  # utility modules
    for filename in os.listdir("cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            if filename in ignored_files:
                continue
            cog_name = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(cog_name)
                print(f"✅ Loaded cog: {cog_name}")
            except Exception as e:
                print(f"❌ Failed to load cog {cog_name}: {e}")

# ─── Event: Bot is ready ─────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

    guild = discord.Object(id=GUILD_ID)

    # 1️⃣ Fetch existing commands and remove them
    existing_commands = await bot.tree.fetch_commands(guild=guild)
    for cmd in existing_commands:
        await bot.tree.remove_command(cmd.name, guild=guild)
        print(f"🗑 Removed old command: {cmd.name}")

    # 2️⃣ Sync commands after clearing
    await bot.tree.sync(guild=guild)
    print(f"🌐 Synced slash commands for guild ID {GUILD_ID}")

# ─── Main entry point ───────────────────────────────
async def main():
    async with bot:
        # Load all cogs first
        await load_cogs()
        # Start the bot (on_ready will handle syncing)
        await bot.start(TOKEN)

# ─── Run bot ────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(main())
