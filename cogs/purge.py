import discord
from discord import client
from discord.ext import commands
from discord.ext.commands import Bot, Cog, bot
from discord.ext.commands.core import command

client = discord.Client

class Purge(Cog):

    def __init__(self, bot):
        self.bot = bot

    #Purge command
    @commands.command(pass_context=True)
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount=0):
        # I don't really know if this is the best way to do this. Please let me know if there is a more efficient way.
        messages = []
        async for message in ctx.message.channel.history(limit=amount + 1):
              messages.append(message)

        await ctx.message.channel.delete_messages(messages)

        # Must have channel named server-logs
        logChannel = discord.utils.get(ctx.guild.channels, name='server-logs')
        await logChannel.send(f'{amount} messages have been purged by {ctx.message.author.mention} in {ctx.message.channel}')
    # Will directly tell you the error if you use the command wrong. Maybe make it more easy to understand errors in the future?
    @purge.error
    async def purge_error(self, ctx, error):
        await ctx.channel.send(error)

# Setup the cog for the bot
def setup(bot: Bot) -> None:
    bot.add_cog(Purge(bot))