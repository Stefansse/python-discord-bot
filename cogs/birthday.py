import discord
from discord.ext import commands, tasks
import json
import os
from datetime import datetime
import random

BIRTHDAY_FILE = "data/birthdays.json"
BIRTHDAY_CHANNEL_ID = int(os.getenv("BIRTHDAY_CHANNEL_ID", 0))  # channel for birthday messages

# Ensure the JSON file exists
if not os.path.exists(BIRTHDAY_FILE):
    os.makedirs(os.path.dirname(BIRTHDAY_FILE), exist_ok=True)
    with open(BIRTHDAY_FILE, "w") as f:
        json.dump({}, f)

def load_birthdays():
    with open(BIRTHDAY_FILE, "r") as f:
        return json.load(f)

def save_birthdays(data):
    with open(BIRTHDAY_FILE, "w") as f:
        json.dump(data, f, indent=4)

class BirthdayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.birthday_gifs = [
            "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
            "https://media.giphy.com/media/3o6Zt6ML6BklcajjsA/giphy.gif",
            "https://media.giphy.com/media/26gssIytJvy1b1THO/giphy.gif",
            "https://media.giphy.com/media/xUPGcguWZHRC2HyBRS/giphy.gif",
            "https://media.giphy.com/media/5GoVLqeAOo6PK/giphy.gif",
        ]
        self.birthday_check.start()

    def cog_unload(self):
        self.birthday_check.cancel()

    @commands.command(name="setbirthday", help="Set your birthday: !setbirthday DD-MM")
    async def set_birthday(self, ctx, date: str):
        try:
            datetime.strptime(date, "%d-%m")
        except ValueError:
            return await ctx.send("❌ Invalid format! Use DD-MM, e.g., 16-10")
        birthdays = load_birthdays()
        birthdays[str(ctx.author.id)] = date
        save_birthdays(birthdays)
        await ctx.send(f"✅ {ctx.author.display_name}, your birthday has been set to {date} 🎉")

    @commands.command(name="mybirthday", help="Check your birthday")
    async def my_birthday(self, ctx):
        birthdays = load_birthdays()
        date = birthdays.get(str(ctx.author.id))
        if date:
            await ctx.send(f"🎂 {ctx.author.display_name}, your birthday is set to {date}")
        else:
            await ctx.send("❌ You have not set a birthday yet. Use `!setbirthday DD-MM`")

    @commands.command(name="upcomingbirthdays", help="Show upcoming birthdays")
    async def upcoming_birthdays(self, ctx):
        birthdays = load_birthdays()
        today = datetime.now()
        upcoming = []
        for user_id, date_str in birthdays.items():
            day, month = map(int, date_str.split("-"))
            birthday_this_year = datetime(today.year, month, day)
            days_until = (birthday_this_year - today).days
            if days_until >= 0:
                upcoming.append((user_id, date_str, days_until))
        if not upcoming:
            return await ctx.send("No upcoming birthdays found.")
        upcoming.sort(key=lambda x: x[2])
        msg = ""
        for user_id, date_str, days_until in upcoming:
            member = ctx.guild.get_member(int(user_id))
            if member:
                msg += f"🎉 {member.display_name}: {date_str} ({days_until} days)\n"
        await ctx.send(msg or "No upcoming birthdays found.")

    @commands.command(name="testbirthday", help="Test birthday messages now")
    async def test_birthday(self, ctx):
        await self.birthday_check()
        await ctx.send("✅ Birthday check ran!")

    @tasks.loop(hours=24)
    async def birthday_check(self):
        await self.bot.wait_until_ready()
        today_str = datetime.now().strftime("%d-%m")
        birthdays = load_birthdays()

        channel = self.bot.get_channel(BIRTHDAY_CHANNEL_ID)
        if not channel:
            print(f"❌ Birthday channel ID {BIRTHDAY_CHANNEL_ID} not found.")
            return

        for user_id, date_str in birthdays.items():
            if date_str == today_str:
                member = channel.guild.get_member(int(user_id))
                if member:
                    gif_url = random.choice(self.birthday_gifs)
                    embed = discord.Embed(
                        title=f"🎂 Happy Birthday {member.display_name}! 🎉",
                        description=f"Everyone wish **{member.display_name}** a fantastic day! 🥳",
                        color=discord.Color.random()
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    embed.set_image(url=gif_url)
                    embed.set_footer(text="🔒•private-talk 🎈")
                    await channel.send(embed=embed)

    @birthday_check.before_loop
    async def before_birthday_check(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(BirthdayCog(bot))
    print("👉 Birthday cog loaded with GIFs and channel ID support")
