import discord

def create_music_embed(title: str, url: str, author: str = None):
    """Create a modern embed for the currently playing song"""
    embed = discord.Embed(
        title="🎶 Now Playing",
        description=f"[{title}]({url})",
        color=discord.Color.blurple()
    )
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/4/41/YouTube_icon_%282013-2017%29.png")
    if author:
        embed.add_field(name="Added by", value=author, inline=True)
    embed.set_footer(text="Use the buttons below to control playback")
    embed.timestamp = discord.utils.utcnow()
    return embed