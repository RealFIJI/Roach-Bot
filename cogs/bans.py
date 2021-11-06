import discord
from discord.ext import commands
from discord.ext.commands import Bot, Cog
from discord.ext.commands.core import command

class Bans(Cog):

    def __init__(self, bot):
        self.bot = bot

    # The ban command. User must have ban_members permission to use it.
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member:discord.User=None, reason=None):
        banner = ctx.author
        if member == None or member == ctx.message.author:
            await ctx.channel.send("Sorry, but you can't ban yourself " + banner)
            return
        if reason == None:
            reason = " no reason whatsoever. Rude..."
        message = f"You have been banned from {ctx.guild.name} for {reason}"
        await member.send(message)
        await ctx.guild.ban(member, reason=reason)
        await ctx.channel.send(f"{member} has been banned by " + banner.mention + " for " + reason) 
    # Will directly tell you the error if you use the command wrong. Maybe make it more easy to understand errors in the future?
    @ban.error
    async def ban_error(self, ctx, error):
        await ctx.channel.send(error)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member:discord.User=None, reason=None):
        unbanner = ctx.author
        if member == None or member == ctx.message.author:
            await ctx.channel.send("Sorry, but you can't unban yourself " + unbanner)
            return
        if reason == None:
            reason = " no reason whatsoever. Nice..."
        
        await ctx.guild.unban(member, reason=reason)
        await ctx.channel.send(f"{member} has been unbanned by " + unbanner.mention + " for " + reason) 

        # Depending on the user's settings this may or may not cause an error. should probably fix in future verions lol
        message = f"You have been unbanned from {ctx.guild.name} for {reason}"
        await member.send(message)
    # Will directly tell you the error if you use the command wrong. Maybe make it more easy to understand errors in the future?
    @unban.error
    async def unban_error(self, ctx, error):
        await ctx.channel.send(error)

# Setup the cog for the bot
def setup(bot: Bot) -> None:
    bot.add_cog(Bans(bot))