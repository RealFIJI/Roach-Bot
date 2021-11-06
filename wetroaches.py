import discord
from discord.ext import commands
from discord.ext.commands import bot

import os

bot = commands.Bot(
    command_prefix= ("<:wetroaches:838923368349564960> "),
    intents=discord.Intents(messages=True, guilds=True, bans=True, reactions=True),
    case_insensitive=True
)

# Removes default help command
bot.remove_command('help')


@bot.event
async def on_ready():
    # Print "roach bot has logged in" when Roach Bot is ready
    print('roach bot has logged in.'.format(bot))

    # Status
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="roaches"))
     

# Loads all cogs.
for filename in os.listdir('./cogs'):
  if filename.endswith('.py'):
    bot.load_extension(f'cogs.{filename[:-3]}')

#Pass
bot.run('BOT_TOKEN')