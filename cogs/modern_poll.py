import discord
from discord.ext import commands
from discord.ui import Button, View

# ---------- Modern Poll Classes ----------
class ModernPollView(View):
    def __init__(self, question: str, options: list):
        super().__init__(timeout=None)
        self.question = question
        self.options = options
        self.votes = {opt: 0 for opt in options}
        self.user_votes = {}
        self.emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"][:len(options)]
        for i, opt in enumerate(options):
            self.add_item(ModernPollButton(opt, self, self.emojis[i]))

class ModernPollButton(Button):
    def __init__(self, label: str, poll_view: ModernPollView, emoji: str):
        super().__init__(label=label, style=discord.ButtonStyle.primary, emoji=emoji)
        self.poll_view = poll_view

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        # Remove previous vote if exists
        if user.id in self.poll_view.user_votes:
            prev_vote = self.poll_view.user_votes[user.id]
            self.poll_view.votes[prev_vote] -= 1

        # Add new vote
        self.poll_view.votes[self.label] += 1
        self.poll_view.user_votes[user.id] = self.label

        # Build progress bar embed
        total_votes = sum(self.poll_view.votes.values()) or 1
        description = ""
        for i, opt in enumerate(self.poll_view.options):
            count = self.poll_view.votes[opt]
            percent = int((count / total_votes) * 20)
            bar = "█" * percent + "░" * (20 - percent)
            description += f"{self.poll_view.emojis[i]} **{opt}:** {count} votes {bar}\n"

        embed = discord.Embed(
            title=f"📊 {self.poll_view.question}",
            description=description,
            color=discord.Color.purple()
        )
        embed.set_footer(text=f"Total voters: {len(self.poll_view.user_votes)}")
        await interaction.response.edit_message(embed=embed, view=self.poll_view)


# ---------- Cog ----------
class PollCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="modern_poll")
    async def modern_poll(self, ctx, question: str, *options):
        if len(options) < 2:
            return await ctx.send("❌ You need at least 2 options.")
        if len(options) > 5:
            return await ctx.send("❌ Maximum 5 options allowed.")

        view = ModernPollView(question, list(options))
        embed_description = "\n".join([f"{view.emojis[i]} **{opt}**" for i, opt in enumerate(options)])
        embed = discord.Embed(
            title=f"📊 {question}",
            description=embed_description,
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Click a button to vote! Live updates will appear here.")
        await ctx.send(embed=embed, view=view)


# ---------- Setup ----------
async def setup(bot: commands.Bot):
    print("👉 Poll cog loaded")
    await bot.add_cog(PollCog(bot))
