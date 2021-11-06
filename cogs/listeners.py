import discord
from discord import client
from discord.ext import commands
from discord.ext.commands import Bot, Cog, bot
from discord.ext.commands.core import command

client = commands.Bot (command_prefix = 'fij ')

class Listeners(Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):

        # Make sure it doesn't respond to itself.
        # This is probably not a good permenant fix. Please change this later.
        if message.author.bot: return



        if("wet roaches") == message.content:
            await message.channel.send("<:wetroaches:838923368349564960>") 




# Setup the cog for the bot
def setup(bot: Bot) -> None:
    bot.add_cog(Listeners(bot))