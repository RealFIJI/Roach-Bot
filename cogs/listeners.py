import discord
from discord import client
from discord import member
from discord.ext import commands
from discord.ext.commands import Bot, Cog, bot
from discord.ext.commands.core import command

import asyncpg

bot = commands.Bot(
    command_prefix= ("<:wetroaches:838923368349564960> "),
    intents=discord.Intents.all(),
    case_insensitive=True
)

class Listeners(Cog):

    def __init__(self, bot):
        self.bot = bot

        self.milestones = { 
            15: 'Basic',
            100: 'Expert',
            500: 'Elite',
            5000: 'God'
         }


    
    @commands.Cog.listener()
    async def on_message(self, message):
        # Make sure it doesn't respond to itself.
        if message.author.bot: return



        if("wet roaches") == message.content:
            await message.channel.send("<:wetroaches:838923368349564960>") 


        # Track our roahces in our DB.
        if("<:wetroaches:838923368349564960>") == message.content:
            # Send some confirmation :)
            #await message.channel.send("<:wetroaches:838923368349564960>") 

            async with self.bot.db_pool.acquire() as conn:
                # Get the amount of roaches the user ahs sent AND increment their value
                roaches = await conn.fetchval('''
                    INSERT INTO roach_tracker (user_id, roaches) 
                    VALUES ($1, 1) 
                    ON CONFLICT (user_id) 
                    DO UPDATE SET roaches = roach_tracker.roaches + 1
                    RETURNING roaches
                ''', message.author.id)

                print(f"[DEBUG] {message.author.name} just hit {roaches} roaches.")

                milestone = self.milestones.get(roaches)

                # The user ranked up
                if milestone is not None:

                    ## We want to give them the new rank and send their new card
                    # Giver user role
                    try:
                        role = discord.utils.get(message.guild.roles, name=("Roach License - " + milestone))
                        await message.author.add_roles(role)
                    except Exception as e:
                        await message.channel.send(e)
                

             

       #await message.channel.send("<:wetroaches:838923368349564960>\nRemember to check your progress with <:wetroaches:838923368349564960> stats or /stats!")




    # list of roles to get from emotes
    global emote_roles
    emote_roles = {
        'wetroaches' : 'roach ping',
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


    # Rank/DB watcher
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        # Stop if their roles didn't actually change 
        if before.roles == after.roles:
            return

        # Find added role
        added_roles = [role for role in after.roles if role not in before.roles]
        
        if not added_roles:
            return 

        # A role was added. Let's see what it was
        role_baselines = {
            'Roach License - God': 5000, 
            'Roach License - Elite': 500,
            'Roach License - Expert': 100,
            'Roach License - Basic': 15
        }

        # Check if new role in baseline
        new_baseline = 0
        granted_role_name = None
        
        # Get the name of the new role
        for role in added_roles:
            if role.name in role_baselines:
                # If they somehow got two roles at once, keep the highest baseline
                if role_baselines[role.name] > new_baseline:
                    new_baseline = role_baselines[role.name]
                    granted_role_name = role.name


        # Update DB if rank changed
        if new_baseline > 0:
            query = """
                INSERT INTO roach_tracker (user_id, roaches) 
                VALUES ($1, $2)
                ON CONFLICT (user_id) 
                DO UPDATE SET roaches = EXCLUDED.roaches 
                WHERE roach_tracker.roaches < EXCLUDED.roaches
            """
            
            try:
                async with self.bot.db_pool.acquire() as conn:
                    await conn.execute(query, after.id, new_baseline)
                    print(f"Auto-synced {after.name} to {new_baseline} roaches based on new role.")
            except Exception as e:
                print(f"Role auto-sync broke")

            # Find out WHO gave the role via Audit Logs
            provider_name = "Admin"
            async for entry in after.guild.audit_logs(limit=5, action=discord.AuditLogAction.member_role_update):
                if entry.target.id == after.id:
                    raw_name = str(entry.user)
                    
                    # Just in case they have a discriminator (#) in their username (bots)
                    clean_name = raw_name.split('#')[0]
                    
                    # 3. Apply your 15 character cap
                    provider_name = clean_name[:15]
                    break
                    

            simple_role_name = granted_role_name.split('-')[1].strip()            
            
            # Get the License Cog and generate the non-progress license
            license_cog = self.bot.get_cog('License')
            file = await license_cog.create_license(
                user=after, 
                provider=provider_name, 
                rank=simple_role_name
            )
            
            

            # Send the license to the withdrawl channel
            target_channel = self.bot.get_channel(838915294084333568)
            await target_channel.send(
                content=f"Congratulations, {after.mention}! You have officially ranked up to {granted_role_name}.", 
                file=file
            )


# Setup the cog for the bot
async def setup(bot: Bot) -> None:
    await bot.add_cog(Listeners(bot))