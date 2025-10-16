import discord
from discord.ext import commands
from deep_translator import GoogleTranslator
from langdetect import detect

def create_modern_embed(author, original_text, translated_text, detected_lang="Auto", target_lang="Target"):
    colors = [0x6A5ACD, 0x1DB954, 0xFF4500, 0x00CED1]
    color = colors[len(original_text) % len(colors)]

    embed = discord.Embed(
        title="🌐 Modern Translation",
        description=f"**Requested by:** {author.mention}",
        color=color
    )

    embed.add_field(
        name=f"📝 Original ({detected_lang})",
        value=f"```fix\n{original_text}```",
        inline=True
    )
    embed.add_field(
        name=f"🌍 Translated ({target_lang})",
        value=f"```css\n{translated_text}```",
        inline=True
    )

    embed.set_author(name=author.display_name, icon_url=author.display_avatar.url)
    embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/5/5e/Google_Translate_logo.png")
    embed.set_footer(text="Powered by GoogleTranslator | Auto language detection")
    embed.timestamp = discord.utils.utcnow()
    return embed

class TranslatorCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="translate", help="Translate text to a target language: !translate <lang> <text>")
    async def translate(self, ctx: commands.Context, target_lang: str, *, text: str):
        try:
            translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
            detected_lang = detect(text)
            embed = create_modern_embed(ctx.author, text, translated, detected_lang.upper(), target_lang.upper())
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Translation failed: {e}")

    @commands.command(name="mk", help="Quick translate to Macedonian: !mk <text>")
    async def mk(self, ctx: commands.Context, *, text: str):
        try:
            translated = GoogleTranslator(source='auto', target='mk').translate(text)
            detected_lang = detect(text)
            embed = create_modern_embed(ctx.author, text, translated, detected_lang.upper(), "MK")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Translation failed: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(TranslatorCog(bot))
    print("👉 Translator (! prefix) cog loaded")
