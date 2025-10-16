# cogs/music.py
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp as youtube_dl
import logging

from .playlist import get_playlist, add_song_to_playlist, get_song_url
from .views import MusicControls

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        if not hasattr(bot, "loop_queue"):
            bot.loop_queue = []
        if not hasattr(bot, "currently_playing"):
            bot.currently_playing = None

    async def fetch_info(self, search: str):
        """Fetch song info from YouTube dynamically."""
        try:
            def ydl_extract():
                ydl_opts = {
                    "format": "bestaudio/best",
                    "quiet": True,
                    "default_search": "ytsearch1",
                    "noplaylist": True
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(search, download=False)
                    if "entries" in info:
                        info = info["entries"][0]
                    return info
            return await asyncio.to_thread(ydl_extract)
        except Exception as e:
            logger.error(f"Error fetching YouTube info for '{search}': {e}")
            return None

    async def play_next(self, vc: discord.VoiceClient, channel: discord.TextChannel):
        """Play the next song in queue."""
        if not self.bot.loop_queue:
            self.bot.currently_playing = None
            return

        item = self.bot.loop_queue[0]
        self.bot.currently_playing = item

        try:
            # Fetch URL if not present
            if not item.get("url"):
                info = await self.fetch_info(item["song"])
                if not info:
                    await channel.send(f"Failed to fetch info for: {item['song']}")
                    self.bot.loop_queue.pop(0)
                    await self.play_next(vc, channel)
                    return
                item["url"] = info["url"]
                item["song"] = info.get("title", item["song"])
                # Add to DB without url
                add_song_to_playlist(item["song"], item["author"])

            source = await discord.FFmpegOpusAudio.from_probe(item["url"], **FFMPEG_OPTIONS)

            def after_playing(error):
                if error:
                    logger.error(f"Playback error: {error}")
                # Remove finished song
                if self.bot.loop_queue and self.bot.loop_queue[0] == item:
                    self.bot.loop_queue.pop(0)
                if self.bot.loop_queue:
                    asyncio.run_coroutine_threadsafe(
                        self.play_next(vc, channel), self.bot.loop
                    )

            vc.play(source, after=after_playing)

            embed = discord.Embed(
                title=f"Now Playing: {item['song']}",
                description=f"Added by: {item['author']}",
                color=discord.Color.blurple()
            )
            await channel.send(embed=embed, view=MusicControls(self.bot, channel, item["song"], item["url"]))

        except Exception as e:
            logger.error(f"Error in play_next: {e}")
            if self.bot.loop_queue and self.bot.loop_queue[0] == item:
                self.bot.loop_queue.pop(0)
            if self.bot.loop_queue:
                await self.play_next(vc, channel)

    @app_commands.command(name="play", description="Play a song or add it to the queue")
    @app_commands.describe(song="The name or URL of the song to play")
    async def play(self, interaction: discord.Interaction, song: str):
        await interaction.response.defer()
        if not interaction.user.voice:
            return await interaction.followup.send("Join a voice channel first.", ephemeral=True)

        vc = interaction.guild.voice_client
        if not vc:
            vc = await interaction.user.voice.channel.connect()

        # Always fetch dynamic info; we no longer store URL in DB
        info = await self.fetch_info(song)
        if not info:
            return await interaction.followup.send("Failed to fetch song info.", ephemeral=True)

        title = info.get("title", song)
        url = info["url"]

        # Prevent duplicates in queue
        if any(item["song"] == title for item in self.bot.loop_queue):
            return await interaction.followup.send(f"**{title}** is already in the queue!", ephemeral=True)

        song_entry = {"song": title, "author": interaction.user.display_name, "url": url}
        self.bot.loop_queue.append(song_entry)

        # Add to DB without URL
        add_song_to_playlist(title, interaction.user.display_name)

        if not vc.is_playing() and self.bot.loop_queue:
            await self.play_next(vc, interaction.channel)

        await interaction.followup.send(f"Added to queue: **{title}**")

    @app_commands.command(name="play_playlist", description="Play all songs from the stored playlist")
    async def play_playlist(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not interaction.user.voice:
            return await interaction.followup.send("Join a voice channel first.", ephemeral=True)

        vc = interaction.guild.voice_client
        if not vc:
            vc = await interaction.user.voice.channel.connect()

        songs = get_playlist()
        if not songs:
            return await interaction.followup.send("Playlist is empty!", ephemeral=True)

        new_songs = []
        for song in songs:
            if not any(item["song"] == song["song"] for item in self.bot.loop_queue):
                # Fetch URL dynamically for each playlist song
                info = await self.fetch_info(song["song"])
                if not info:
                    continue
                song_entry = {"song": info.get("title", song["song"]),
                              "author": song["author"],
                              "url": info["url"]}
                self.bot.loop_queue.append(song_entry)
                new_songs.append(song_entry)

        if not vc.is_playing() and self.bot.loop_queue:
            await self.play_next(vc, interaction.channel)

        await interaction.followup.send(f"Added **{len(new_songs)} unique songs** from playlist to the queue.")

    @app_commands.command(name="queue", description="Show the current music queue")
    async def queue(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not self.bot.loop_queue:
            return await interaction.followup.send("Queue is empty.", ephemeral=True)

        description = "\n".join([f"{i+1}. {item['song']} (added by {item['author']})"
                                for i, item in enumerate(self.bot.loop_queue)])
        embed = discord.Embed(title="Current Queue", description=description, color=discord.Color.blurple())
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
