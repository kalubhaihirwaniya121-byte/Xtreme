import random

import discord
from discord.ext import commands

from utils.action_loader import ACTION_GIFS
from utils.emojis import Emojis
from utils.storage import load_json, save_json


class Actions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    def get_pair_key(self, user1, user2):
        return "_".join(sorted([str(user1.id), str(user2.id)]))

    def increment_action(self, user1, user2, action):
        data = load_json("action_stats.json")
    
        pair = self.get_pair_key(user1, user2)
    
        if pair not in data:
            data[pair] = {
                "kiss": 0,
                "hug": 0
            }
    
        data[pair][action] += 1
    
        save_json("action_stats.json", data)
    
        return data[pair][action]

    def get_action_count(self, user1, user2, action):
        data = load_json("action_stats.json")
    
        pair = self.get_pair_key(user1, user2)
    
        if pair not in data:
            return 0
    
        return data[pair][action]

    async def send_action_embed(
        self,
        ctx,
        member: discord.Member,
        action: str,
        emoji: str,
        past: str,
        count: int | None = None
    ):
        gifs = ACTION_GIFS.get(action, [])

        if not gifs:
            return await ctx.send(
                f"{Emojis.CROSS} No GIFs found for **{action}**."
            )

        gif = random.choice(gifs)

        embed = discord.Embed(
            title=f"{emoji} {ctx.author.mention} {past} {member.mention}!",
            color=discord.Color.random()
        )

        embed.set_image(url=gif)

        if count is not None:
            embed.set_footer(
                text=f"{action.title()} Count: {count} • Loveyapa"
            )
        else:
            embed.set_footer(
                text="Loveyapa • Xtreme Bot"
            )

        await ctx.send(embed=embed)
        
    @commands.hybrid_command(
        name="kiss",
        description="Kiss someone."
    )
    async def kiss(self, ctx, member: discord.Member):

        if member == ctx.author:
            return await ctx.send(
                f"{Emojis.CROSS} You can't kiss yourself!"
            )

        if member.bot:
            return await ctx.send(
                f"{Emojis.CROSS} You can't kiss bots!"
            )

        count = self.increment_action(
            ctx.author,
            member,
            "kiss"
        )

        await self.send_action_embed(
            ctx=ctx,
            member=member,
            action="kiss",
            emoji="😘",
            past="kissed",
            count=count
        )
      
    @commands.hybrid_command(
        name="hug",
        description="Hug someone."
    )
    async def hug(self, ctx, member: discord.Member):

        if member == ctx.author:
            return await ctx.send(
                f"{Emojis.CROSS} You can't hug yourself!"
            )

        if member.bot:
            return await ctx.send(
                f"{Emojis.CROSS} You can't hug bots!"
            )

        count = self.increment_action(
            ctx.author,
            member,
            "hug"
        )

        await self.send_action_embed(
            ctx=ctx,
            member=member,
            action="hug",
            emoji="🤗",
            past="hugged",
            count=count
        )
        
    @commands.hybrid_command(name="cuddle", description="Cuddle someone.")
    async def cuddle(self, ctx, member: discord.Member):

        if member == ctx.author:
            return await ctx.send(f"{Emojis.CROSS} You can't cuddle yourself!")

        if member.bot:
            return await ctx.send(f"{Emojis.CROSS} You can't cuddle bots!")

        await self.send_action_embed(
            ctx=ctx,
            member=member,
            action="cuddle",
            emoji="🥰",
            past="cuddled"
        )


    @commands.hybrid_command(name="holdhand", description="Hold someone's hand.")
    async def holdhand(self, ctx, member: discord.Member):

        if member == ctx.author:
            return await ctx.send(f"{Emojis.CROSS} You can't hold your own hand!")

        if member.bot:
            return await ctx.send(f"{Emojis.CROSS} You can't hold a bot's hand!")

        await self.send_action_embed(
            ctx=ctx,
            member=member,
            action="holdhand",
            emoji="🤝",
            past="held hands with"
        )


    @commands.hybrid_command(name="gift", description="Gift someone.")
    async def gift(self, ctx, member: discord.Member):

        if member == ctx.author:
            return await ctx.send(f"{Emojis.CROSS} You can't gift yourself!")

        if member.bot:
            return await ctx.send(f"{Emojis.CROSS} You can't gift bots!")

        await self.send_action_embed(
            ctx=ctx,
            member=member,
            action="gift",
            emoji="🎁",
            past="gifted"
        )


    @commands.hybrid_command(name="pat", description="Pat someone.")
    async def pat(self, ctx, member: discord.Member):

        if member == ctx.author:
            return await ctx.send(f"{Emojis.CROSS} You can't pat yourself!")

        if member.bot:
            return await ctx.send(f"{Emojis.CROSS} You can't pat bots!")

        await self.send_action_embed(
            ctx=ctx,
            member=member,
            action="pat",
            emoji="🫳",
            past="patted"
        )

    @commands.hybrid_command(name="highfive", description="High-five someone.")
    async def highfive(self, ctx, member: discord.Member):

        if member == ctx.author:
            return await ctx.send(f"{Emojis.CROSS} You can't high-five yourself!")

        if member.bot:
            return await ctx.send(f"{Emojis.CROSS} You can't high-five bots!")

        await self.send_action_embed(
            ctx=ctx,
            member=member,
            action="highfive",
            emoji="🙌",
            past="high-fived"
        )


    @commands.hybrid_command(name="poke", description="Poke someone.")
    async def poke(self, ctx, member: discord.Member):

        if member == ctx.author:
            return await ctx.send(f"{Emojis.CROSS} You can't poke yourself!")

        if member.bot:
            return await ctx.send(f"{Emojis.CROSS} You can't poke bots!")

        await self.send_action_embed(
            ctx=ctx,
            member=member,
            action="poke",
            emoji="👉",
            past="poked"
        )


    @commands.hybrid_command(name="wave", description="Wave at someone.")
    async def wave(self, ctx, member: discord.Member):

        if member == ctx.author:
            return await ctx.send(f"{Emojis.CROSS} You can't wave at yourself!")

        if member.bot:
            return await ctx.send(f"{Emojis.CROSS} You can't wave at bots!")

        await self.send_action_embed(
            ctx=ctx,
            member=member,
            action="wave",
            emoji="👋",
            past="waved at"
        )


    @commands.hybrid_command(name="slap", description="Slap someone.")
    async def slap(self, ctx, member: discord.Member):

        if member == ctx.author:
            return await ctx.send(f"{Emojis.CROSS} You can't slap yourself!")

        if member.bot:
            return await ctx.send(f"{Emojis.CROSS} You can't slap bots!")

        await self.send_action_embed(
            ctx=ctx,
            member=member,
            action="slap",
            emoji="👋",
            past="slapped"
        )


async def setup(bot):
    await bot.add_cog(Actions(bot))