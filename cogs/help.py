import discord
from discord.ext import commands
from discord.ext.commands import Bot, Cog
from discord.ext.commands.core import command

class Help(Cog):

    def __init__(self, bot):
        self.bot = bot


    #Help command
    @commands.command()
    async def help(self, ctx):
        await ctx.channel.send("<:wetroaches:838923368349564960>")


# Setup the cog for the bot
def setup(bot: Bot) -> None:
    bot.add_cog(Help(bot))