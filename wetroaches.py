import discord
from discord.ext import commands
from discord.ext.commands import bot

import os

bot = commands.Bot(
    command_prefix= ("<:wetroaches:838923368349564960> "),
    intents=discord.Intents.all(),
    case_insensitive=True
)

# Removes default help command
bot.remove_command('help')


@bot.event
async def on_ready():
    await load_cogs()

    # Print "roach bot has logged in" when Roach Bot is ready
    print('\nroach bot has logged in.'.format(bot))

    # Status
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="roaches"))





# Loads all cogs.
async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            cog_name = f'cogs.{filename[:-3]}'
            try:
                print(f"Loading {cog_name}")
                await bot.load_extension(cog_name)
                print(f"Loaded {cog_name} successfully.")
            except Exception as e:
                print(f"Couldn't load {cog_name}: {e}")

#Pass
bot.run('TOKEN')