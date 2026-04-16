import discord
from discord.ext import commands
from discord.ext.commands import Bot, Cog
from discord.ext.commands.core import command

from PIL import Image, ImageFont, ImageDraw, ImageEnhance
from io import BytesIO

import asyncpg

import os

class License(Cog):

    def __init__(self, bot):
        self.bot = bot

        # This is repeated code...
        self.milestones = { 
            15: 'Basic',
            50: 'Intermediate',
            100: 'Expert',
            250: 'Elite',
            500: 'Ultra',
            1000: 'Awesome',
            2500: 'Mega',
            5000: 'God'
         }

        # For prev and next req for progress
        self.sorted_milestones = sorted(self.milestones.items())


    #Generate license command
    @commands.command()
    @commands.has_any_role("License Supplier")
    async def license(self, ctx, user: discord.Member = None, rank = "null"):
        await ctx.channel.typing()

        if user is None:
            user = ctx.author 


        # Get license from function
        file = await self.create_license(user, str(ctx.author)[:15], rank)

        await ctx.channel.send(file=file)


    # See current progress. We're gonna need asyncpg to fetch their progress for this one
    @commands.command()
    async def rank(self, ctx, user: discord.Member = None):
        await ctx.channel.typing()

        if user is None:
            user = ctx.author 

        # Get current roaches from DB
        async with self.bot.db_pool.acquire() as conn:
            roaches = await conn.fetchval(
                "SELECT roaches FROM roach_tracker WHERE user_id = $1", 
                user.id
            )

        ## If no progress
        if roaches is None:
            roaches = 0

        prev_req = 0
        rank_name = "None"
        next_req = 15 # Default next requirement

        # Calcualte next and prev requirements
        for req, name in self.sorted_milestones:
            if roaches >= req:
                prev_req = req
                rank_name = name
            else:
                # If roaches isn't greater than or equal to the req, it MUST be less than.
                next_req = req
                break
        else:
            # If roaches >5000
            next_req = 5000


        # Get license from function
        file = await self.create_license_with_progress(user, 'Roach Bot', rank_name, prev_req, next_req, roaches)

        await ctx.channel.send(file=file)


    async def create_license(self, user: discord.Member, provider: str, rank: str):
        card = Image.open("assets/cardtemplate-notext-wm.png")
        
        # Put pfp in license
        asset = user.display_avatar.replace(size=512)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)

        pfp = pfp.resize((905,901))
        card.paste(pfp, (120, 285))

        # Put text into license
        draw = ImageDraw.Draw(card)
        font = ImageFont.truetype("assets/Rubik-Bold.ttf", 150)

        # Get the username string from user, but just use the providr str we laready have
        username = str(user)[:15]

        draw.text((1775, 440), username, (0, 0, 0), anchor="ms",  font=font, features=["-liga"])
        draw.text((1775, 825), provider, (0, 0, 0), anchor="ms", font=font, features=["-liga"])
        draw.text((1775, 1140), rank, (0, 0, 0), anchor="ms", font=font, features=["-liga"])

        # Save to memory instead of as a file on the disjk
        buffer = BytesIO()
        card.save(buffer, format="PNG")
        buffer.seek(0)

        return discord.File(fp=buffer, filename="license.png")

    async def create_license_with_progress(self,  user: discord.Member, provider: str, rank: str, prev_req, next_req, roaches):
        # Get new progress card, and draw normal stuff
        card = Image.open("assets/cardtemplate-notext-wm-progress.png")
        
        # Put pfp in license
        asset = user.display_avatar.replace(size=512)
        data = BytesIO(await asset.read())
        pfp = Image.open(data)

        pfp = pfp.resize((905,901))
        card.paste(pfp, (120, 285))

        # Put text into license
        draw = ImageDraw.Draw(card)
        font = ImageFont.truetype("assets/Rubik-Bold.ttf", 150)

        # Get the username string from user, but just use the providr str we laready have
        username = str(user)[:15]

        draw.text((1775, 440), username, (0, 0, 0), anchor="ms",  font=font, features=["-liga"])
        draw.text((1775, 825), provider, (0, 0, 0), anchor="ms", font=font, features=["-liga"])
        draw.text((1775, 1140), rank, (0, 0, 0), anchor="ms", font=font, features=["-liga"])



        
        ## POINTS FOR PROGRESS BAR
        # TOP LEFT: 100, 1335
        # BOTTOM LEFT: 100, 1460
        # TOP RIGHT: 2460, 1335
        # BOTTOM RIGHT: 2460, 1460

        ## We want to make the bar itself first
        # Calculate where their progress is
        if next_req == prev_req:
            progress = 1.0
        else:
            progress = (roaches - prev_req) / (next_req - prev_req)
            
        progress = max(0.0, min(1.0, progress))

        # Dimensions of bar
        bar_x1, bar_y1 = 100, 1335
        bar_x2, bar_y2 = 2460, 1460
        
        # Calculate the fill
        max_width = bar_x2 - bar_x1
        fill_width = int(max_width * progress)
        fill_x2 = bar_x1 + fill_width


        # Draw the bar itself
        if fill_width > 0:
            draw.rectangle(
                [bar_x1, bar_y1, fill_x2, bar_y2],
                fill=(0, 0, 0) 
            )

        # Create progress bar (empty rectangle) now
        draw.rectangle(
            [bar_x1, bar_y1, bar_x2, bar_y2],
            fill=None,
            outline=(0, 0, 0),
            width=10
        )

        ## Add the progress markers
        small_font = ImageFont.truetype("assets/Rubik-Regular.ttf", 72)
        text_y = bar_y2 + 10

        draw.text((bar_x1, text_y), str(prev_req), fill=(0, 0, 0), anchor="la", font=small_font)
        draw.text((bar_x2, text_y), str(next_req), fill=(0, 0, 0), anchor="ra", font=small_font)

        ## Add current progress
        text_width = draw.textlength(str(roaches), font=small_font)
        space_remaining = bar_x2 - fill_x2
        
        if space_remaining > (text_width + 30):
            # If there's enough space, put it right of the fill
            prog_x = fill_x2 + 20
            draw.text((prog_x, ((bar_y1 + bar_y2)/2)), str(roaches), fill=(0, 0, 0), anchor="lm", font=small_font)
        else:
            # If not, draw it inside
            prog_x = fill_x2 - 20
            draw.text((prog_x, ((bar_y1 + bar_y2)/2)), str(roaches), fill=(255, 255, 255), anchor="rm", font=small_font)
        

        ## Draw next rank text
        text_next_x = bar_x2
        text_next_y = bar_y1 - 10

        

        next_rank = f"NEXT RANK: {self.milestones.get(next_req)}"

        if prev_req == next_req: next_rank = "NEXT RANK: NONE"

        draw.text((text_next_x, text_next_y), next_rank, fill=(0, 0, 0), anchor="rb", font=small_font)


        # If user is unlicensed, grayscale license w/ red "UNLICENSED" text
        if rank == "None":
            enhancer = ImageEnhance.Color(card)
            card = enhancer.enhance(0.0)

            # Create new layer so red text goes on top
            txt_layer = Image.new('RGBA', card.size, (255, 255, 255, 0))
            stamp_draw = ImageDraw.Draw(txt_layer)
            
            
            # Draw text & rotate
            stamp_font = ImageFont.truetype("assets/Rubik-Bold.ttf", 350)
            
            stamp_draw.text(
                (card.size[0] / 2, card.size[1] / 2), 
                "UNLICENSED", 
                fill=(255, 0, 0, 200), 
                anchor="mm", 
                font=stamp_font
            )
            
            txt_layer = txt_layer.rotate(35, center=(card.size[0] / 2, card.size[1] / 2))
            
            # Combine layers
            card = Image.alpha_composite(card, txt_layer)

        # Finally, save and return
        buffer = BytesIO()
        card.save(buffer, format="PNG")
        buffer.seek(0)
        
        return discord.File(fp=buffer, filename="license_progress.png")


    @license.error
    async def license_error(self, ctx, error):
        await ctx.channel.send(error)


# Setup the cog for the bot
async def setup(bot: Bot) -> None:
    await bot.add_cog(License(bot))