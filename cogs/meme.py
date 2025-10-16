import discord
from discord.ext import commands
import os
import requests
from dotenv import load_dotenv

load_dotenv()
IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME")
IMGFLIP_PASSWORD = os.getenv("IMGFLIP_PASSWORD")

class Meme(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="meme", help="Generate a meme: !meme <template> <top_text> | <bottom_text>")
    async def meme(self, ctx: commands.Context, template: str = "buzz", *, text: str = "Top Text | Bottom Text"):
        # Split top and bottom text
        if "|" in text:
            top_text, bottom_text = [t.strip() for t in text.split("|", 1)]
        else:
            top_text = text
            bottom_text = ""

        templates = {
            "buzz": "61579",
            "drake": "181913649",
            "distracted": "112126428",
        }

        template_id = templates.get(template.lower())
        if not template_id:
            return await ctx.send(f"❌ Unknown template. Available: {', '.join(templates.keys())}")

        url = "https://api.imgflip.com/caption_image"
        payload = {
            "template_id": template_id,
            "username": IMGFLIP_USERNAME,
            "password": IMGFLIP_PASSWORD,
            "text0": top_text,
            "text1": bottom_text
        }

        response = requests.post(url, data=payload).json()
        if response["success"]:
            meme_url = response["data"]["url"]
            embed = discord.Embed(title="🖼 Meme Generator", color=discord.Color.orange())
            embed.set_image(url=meme_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Failed to generate meme.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Meme(bot))
    print("👉 Meme (! prefix) cog loaded")
