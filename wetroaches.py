import discord
from discord.ext import commands
from discord.ext.commands import bot
import asyncio
import asyncpg

import os


intents = discord.Intents.default()
intents.presences = True
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix= ("<:wetroaches:838923368349564960> "),
    intents=intents,
    case_insensitive=True,
)

bot.db_pool = None
DATABASE_URL = 'DB_URL'
TOKEN = 'TOKEN'


# Removes default help command
bot.remove_command('help')


@bot.event
async def on_ready():
    # Print "roach bot has logged in" when Roach Bot is ready
    print('\nroach bot has logged in.'.format(bot))

    # Set status
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="roaches"))


# Main function, called when bot wakes up
async def main():
    # Load RoachDB
    await load_db()

    async with bot:
        # Load our cogs, once
        await load_cogs()

        # Log in, and then if stopped, safely close our DB connection.
        try:
            await bot.start(TOKEN)
        except KeyboardInterrupt:
            pass
        finally:
            if bot.db_pool:
                await bot.db_pool.close()
                print("\nRoachDB connection closed")
            if not bot.is_closed():
                await bot.close()
            print("Roach Bot is off")



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

# Load our DB
async def load_db():
    print("Connecting to RoachDB...")

    bot.db_pool = await asyncpg.create_pool(DATABASE_URL)

    # Create default pool if not exists
    async with bot.db_pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS roach_tracker (
                    user_id BIGINT PRIMARY KEY,
                    roaches INT DEFAULT 0
                )
            ''')

    print("Database connected.")


# Run the whole thing
if __name__ == "__main__":
    asyncio.run(main())