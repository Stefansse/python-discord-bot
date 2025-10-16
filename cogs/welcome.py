import discord
from discord.ext import commands
import os

WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID", 0))

# ---------- Helper: Create Welcome Embed ----------
def create_welcome_embed(member: discord.Member):
    embed = discord.Embed(
        title=f"👋 Welcome {member.display_name}!",
        description=f"Welcome to **{member.guild.name}**! Feel free to introduce yourself.",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text="Enjoy your stay! 🎉")
    embed.timestamp = discord.utils.utcnow()
    return embed

# ---------- Welcome Cog ----------
class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- Event: New Member Joins ---
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        if channel:
            embed = create_welcome_embed(member)
            await channel.send(embed=embed)
        else:
            print("❌ Could not find welcome channel. Check the WELCOME_CHANNEL_ID.")

    # --- Test Command ---
    @commands.command(name="test_welcome")
    async def test_welcome(self, ctx):
        """Simulate a new member joining."""
        embed = create_welcome_embed(ctx.author)
        await ctx.send(embed=embed)


# ---------- Setup ----------
async def setup(bot: commands.Bot):
    print("👉 Welcome cog loaded")
    await bot.add_cog(WelcomeCog(bot))
