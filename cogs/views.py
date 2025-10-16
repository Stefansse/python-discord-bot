import discord
from discord.ext import commands

class MusicControls(discord.ui.View):
    def __init__(self, bot: commands.Bot, channel: discord.TextChannel, title: str, url: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.channel = channel
        self.title = title
        self.url = url

    @discord.ui.button(label="⏸ Pause", style=discord.ButtonStyle.secondary)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸ Paused", ephemeral=True)
        else:
            await interaction.response.send_message("Nothing is playing or already paused.", ephemeral=True)

    @discord.ui.button(label="▶️ Resume", style=discord.ButtonStyle.success)
    async def resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message(f"▶️ Resumed: **{self.title}**", ephemeral=True)
        else:
            await interaction.response.send_message("Nothing is paused or not connected.", ephemeral=True)

    @discord.ui.button(label="⏹ Stop", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc:
            vc.stop()
            await interaction.response.send_message("⏹ Stopped playback.", ephemeral=True)
            # Clear the queue and disconnect
            self.bot.loop_queue.clear()
            await vc.disconnect()
        else:
            await interaction.response.send_message("Not connected to a voice channel.", ephemeral=True)

    @discord.ui.button(label="🔁 Loop", style=discord.ButtonStyle.primary)
    async def toggle_loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.bot.is_looping = not self.bot.is_looping
        status = "🔁 Loop ON" if self.bot.is_looping else "➡️ Loop OFF"
        await interaction.response.send_message(f"{status} | Now playing: **{self.title}**", ephemeral=True)

    @discord.ui.button(label="⏭ Skip", style=discord.ButtonStyle.blurple)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()  # Triggers after_playing to play the next song
            await interaction.response.send_message("⏭ Skipped.", ephemeral=True)
        else:
            await interaction.response.send_message("Nothing is playing.", ephemeral=True)

class ViewsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

async def setup(bot: commands.Bot):
    await bot.add_cog(ViewsCog(bot))