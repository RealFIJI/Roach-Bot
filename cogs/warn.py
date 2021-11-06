import discord
from discord.ext import commands
from discord.ext.commands import Bot, Cog
from discord.ext.commands.core import command

class Warn(Cog):

    def __init__(self, bot):
        self.bot = bot
    
    #Warn command (currently anyone can warn, does nothing)
    @commands.command()
    async def warn(self, ctx, member:discord.User=None, *, reason=None):
        await ctx.channel.send(f"{ctx.author} has warned {member} for: **{reason or 'No reason provided.'}**")
    @warn.error
    async def warn_error(self, ctx, error):
        await ctx.channel.send(error)


# Setup the cog for the bot
def setup(bot: Bot) -> None:
    bot.add_cog(Warn(bot))