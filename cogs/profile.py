import discord
from discord.ext import commands
import json
import os
from datetime import datetime

DATA_FILE = "data/profiles.json"

# Ensure the JSON file exists
if not os.path.exists(DATA_FILE):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_profiles():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_profiles(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def calculate_level(xp):
    """Simple leveling: Level = sqrt(xp/10)"""
    import math
    return int(math.sqrt(xp // 10))

class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_cooldowns = {}  # prevent spam XP
        self.xp_per_message = 5
        self.cooldown_seconds = 60  # 1 min cooldown per user
        self.daily_coin_bonus = 10

    # -----------------------------
    # XP from messages
    # -----------------------------
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user_id = str(message.author.id)
        now = datetime.utcnow()
        last_msg_time = self.message_cooldowns.get(user_id)

        if last_msg_time and (now - last_msg_time).total_seconds() < self.cooldown_seconds:
            return  # still in cooldown

        self.message_cooldowns[user_id] = now

        profiles = load_profiles()
        if user_id not in profiles:
            profiles[user_id] = {"xp": 0, "coins": 0, "last_daily": None}

        profiles[user_id]["xp"] += self.xp_per_message
        save_profiles(profiles)

    # -----------------------------
    # Profile command
    # -----------------------------
    @commands.command(name="profile", help="Show your profile card or another user: !profile @user")
    async def profile(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user_id = str(member.id)
        profiles = load_profiles()
        data = profiles.get(user_id, {"xp": 0, "coins": 0, "last_daily": None})

        xp = data["xp"]
        coins = data["coins"]
        level = calculate_level(xp)
        xp_for_next_level = ((level + 1) ** 2) * 10
        xp_bar_filled = int((xp / xp_for_next_level) * 20)
        xp_bar = "█" * xp_bar_filled + "░" * (20 - xp_bar_filled)

        embed = discord.Embed(
            title=f"🎨 {member.display_name}'s Profile",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="🏆 Level", value=f"{level}", inline=True)
        embed.add_field(name="💰 Coins", value=f"{coins}", inline=True)
        embed.add_field(name="XP Progress", value=f"{xp}/{xp_for_next_level}\n{xp_bar}", inline=False)
        await ctx.send(embed=embed)

    # -----------------------------
    # Daily coins bonus
    # -----------------------------
    @commands.command(name="daily", help="Claim your daily coins bonus")
    async def daily(self, ctx):
        user_id = str(ctx.author.id)
        profiles = load_profiles()
        if user_id not in profiles:
            profiles[user_id] = {"xp": 0, "coins": self.daily_coin_bonus, "last_daily": str(datetime.utcnow())}
            save_profiles(profiles)
            return await ctx.send(f"✅ {ctx.author.display_name}, you received {self.daily_coin_bonus} coins!")

        last_daily = profiles[user_id].get("last_daily")
        now = datetime.utcnow()
        if last_daily:
            last = datetime.fromisoformat(last_daily)
            if (now - last).total_seconds() < 86400:
                return await ctx.send("❌ You can only claim daily coins once every 24 hours.")

        profiles[user_id]["coins"] += self.daily_coin_bonus
        profiles[user_id]["last_daily"] = now.isoformat()
        save_profiles(profiles)
        await ctx.send(f"✅ {ctx.author.display_name}, you received {self.daily_coin_bonus} coins!")

async def setup(bot: commands.Bot):
    await bot.add_cog(ProfileCog(bot))
    print("👉 Profile/XP cog loaded (no birthday included)")
