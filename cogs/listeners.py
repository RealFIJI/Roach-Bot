import discord
from discord import client
from discord import member
from discord.ext import commands
from discord.ext.commands import Bot, Cog, bot
from discord.ext.commands.core import command

bot = commands.Bot(
    command_prefix= ("<:wetroaches:838923368349564960> "),
    intents=discord.Intents.all(),
    case_insensitive=True
)

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




    # list of roles to get from emotes
    global emote_roles
    emote_roles = {
        'hesroachyouknow' : 'roach ping',
        'cookedroaches' : 'roach event',
        'cookingroaches' : 'roach decision'
        }

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == 936820490125852732:
            role = discord.utils.get(payload.member.guild.roles, name=emote_roles[payload.emoji.name])

            await payload.member.add_roles(role)
            print(f"Gave {role} to {payload.member}")




    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id == 936820490125852732:
            # i wasted around 5 hours of my life on this single line of code right here
            guild = self.bot.get_guild(payload.guild_id) # be sure to use self.bot.get_guild instead of bot.get_guild to avoid 5 hours of your life being wasted
            member = guild.get_member(payload.user_id)

            role = discord.utils.get(guild.roles, name=emote_roles[payload.emoji.name])

            await member.remove_roles(role)
            print(f"Removed {role} from {payload.member}")




# Setup the cog for the bot
def setup(bot: Bot) -> None:
    bot.add_cog(Listeners(bot))