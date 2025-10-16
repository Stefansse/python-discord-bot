import discord
from discord.ext import commands
import random
from typing import Optional

class RollBattle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_rolls = {}

    @commands.command(name="roll", help="Roll a number between 1 and 100 and compete with your friends!")
    async def roll(self, ctx, opponent: Optional[discord.Member] = None):
        roller = ctx.author
        roll_value = random.randint(1, 100)

        # Track rolls per channel
        if ctx.channel.id not in self.active_rolls:
            self.active_rolls[ctx.channel.id] = {}
        self.active_rolls[ctx.channel.id][roller.id] = roll_value

        # 🎨 Choose color dynamically based on roll result
        color = (
            discord.Color.green() if roll_value > 80 else
            discord.Color.orange() if roll_value > 50 else
            discord.Color.red()
        )

        embed = discord.Embed(
            title="🎲✨ Ultimate Roll Battle ✨🎲",
            description=f"**{roller.display_name}** takes the challenge and rolls the dice... 🎲",
            color=color
        )

        embed.add_field(
            name="🎯 Roll Result",
            value=f"**{roll_value}** / 100",
            inline=False
        )

        # 🆚 If opponent is mentioned
        if opponent:
            opponent_roll = random.randint(1, 100)
            self.active_rolls[ctx.channel.id][opponent.id] = opponent_roll

            # Add opponent result
            embed.add_field(
                name=f"⚔️ {opponent.display_name}'s Turn",
                value=f"**{opponent_roll}** / 100",
                inline=False
            )

            # Determine winner
            if roll_value > opponent_roll:
                winner = roller
                result_emoji = "🏆"
                color = discord.Color.gold()
            elif opponent_roll > roll_value:
                winner = opponent
                result_emoji = "🔥"
                color = discord.Color.blue()
            else:
                winner = None
                result_emoji = "🤝"
                color = discord.Color.greyple()

            # Update embed color for dramatic effect
            embed.color = color

            # Add results
            if winner:
                embed.add_field(
                    name="🏁 Result",
                    value=f"{result_emoji} **{winner.display_name} wins this round!** {result_emoji}",
                    inline=False
                )
            else:
                embed.add_field(
                    name="🤝 Draw!",
                    value="It's a perfect tie — rematch time?",
                    inline=False
                )

        # 🧩 Add footer & thumbnail flair
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/1041/1041916.png")
        embed.set_footer(text="Type !roll @user to challenge someone 🎲 | Luck favors the bold!")

        # Add subtle sparkle in title
        embed.set_author(
            name="Roll Arena",
            icon_url="https://cdn-icons-png.flaticon.com/512/2172/2172891.png"
        )

        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(RollBattle(bot))
    print("👉 Roll Battle cog loaded")
