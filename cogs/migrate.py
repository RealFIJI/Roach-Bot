import discord
from discord.ext import commands
from discord.ext.commands import Bot, Cog
from discord.ext.commands.core import command

import asyncpg


class Migrate(Cog):

    def __init__(self, bot):
        self.bot = bot



    @commands.command()
    @commands.has_any_role("janitor")
    async def sync(self, ctx):
        await ctx.channel.send("Synchronizing database...")

        await ctx.channel.typing()


        # The guidelines for each role
        role_baselines = {
            'Roach License - God': 5000, 
            'Roach License - Elite': 500,
            'Roach License - Expert': 100,
            'Roach License - Basic': 15
        }

        updates = 0

        # 2. The Upsert Query: Insert the baseline, but ONLY overwrite if the new number is higher.
        query = """
            INSERT INTO roach_tracker (user_id, roaches) 
            VALUES ($1, $2)
            ON CONFLICT (user_id) 
            DO UPDATE SET roaches = EXCLUDED.roaches 
            WHERE roach_tracker.roaches < EXCLUDED.roaches
        """

        async with self.bot.db_pool.acquire() as conn:
            # Loop through every user
            for member in ctx.guild.members:
                assigned_baseline = 0
                
                # Check role, see if they have a license that needs updating
                for role_name, baseline in role_baselines.items():
                    if discord.utils.get(member.roles, name=role_name):
                        assigned_baseline = baseline
                        break # Found highest rank, stop checking lower ones
                
                # If applicable, add their roahces to the DB
                if assigned_baseline > 0:
                    print("USER DETECTED")
                    await conn.execute(query, member.id, assigned_baseline)
                    updates += 1
                    

        await ctx.channel.send(f"Synchronization complete. Successfully synced {updates} users.")

    @sync.error
    async def sync_error(self, ctx, error):
        await ctx.channel.send(error)

# Setup the cog for the bot
async def setup(bot: Bot) -> None:
    await bot.add_cog(Migrate(bot))