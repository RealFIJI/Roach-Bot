import discord
from discord.ext import commands
from discord.ext.commands import Bot, Cog
from discord.ext.commands.core import command

from PIL import Image, ImageFont, ImageDraw
from io import BytesIO

import os

class License(Cog):

    def __init__(self, bot):
        self.bot = bot


    #Generate license command
    @commands.command()
    @commands.has_any_role("License Supplier")
    async def license(self, ctx, user: discord.Member = None, rank = "null"):
        if user == None:
            user = ctx.author 

        card = Image.open("assets/cardtemplate-notext-wm.png")

        # Put pfp in license
        asset = user.avatar_url_as(size = 512)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)

        pfp = pfp.resize((905,901))
        card.paste(pfp, (120, 285))

        # Put text into license
        draw = ImageDraw.Draw(card)
        font = ImageFont.truetype("assets/Rubik-Bold.ttf", 150)

        username = str(user)[:-5]
        provider = str(ctx.author)[:-5]

        draw.text((1775, 440), username, (0, 0, 0), anchor="ms",  font=font)
        draw.text((1775, 825), provider, (0, 0, 0), anchor="ms", font=font)
        draw.text((1775, 1140), rank, (0, 0, 0), anchor="ms", font=font)

        card.save("assets/license.png")
        await ctx.channel.send(file = discord.File("assets/license.png"))

    @license.error
    async def license_error(self, ctx, error):
        await ctx.channel.send(error)


# Setup the cog for the bot
def setup(bot: Bot) -> None:
    bot.add_cog(License(bot))