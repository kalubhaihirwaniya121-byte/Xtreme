import discord

from discord.ext import commands

import asyncio

import random

import time

from utils.emojis import Emojis

class Giveaways(commands.Cog):

    """Giveaway system"""

    def __init__(self, bot: commands.Bot):

        self.bot = bot

        # message_id: data

        self.giveaways = {}

    # --------------------------------------------------

    # HELPERS

    # --------------------------------------------------

    def embed(self, title, desc, color=0x2f3136):

        e = discord.Embed(title=title, description=desc, color=color)

        e.set_footer(text="Thanks for using Xtreme")

        return e

    def parse_time(self, time_str: str):

        unit = time_str[-1]

        value = int(time_str[:-1])

        if unit == "s":

            return value

        if unit == "m":

            return value * 60

        if unit == "h":

            return value * 3600

        return None

    async def end_giveaway(self, channel: discord.TextChannel, message_id: int):

        data = self.giveaways.get(message_id)

        if not data:

            return

        try:

            msg = await channel.fetch_message(message_id)

        except discord.NotFound:

            return

        reaction = discord.utils.get(msg.reactions, emoji="🎉")

        if not reaction:

            await channel.send(embed=self.embed(

                "Giveaway Ended",

                "No valid entries."

            ))

            return

        users = [u async for u in reaction.users() if not u.bot]

        if not users:

            await channel.send(embed=self.embed(

                "Giveaway Ended",

                "No participants."

            ))

            return

        winners = random.sample(users, min(data["winners"], len(users)))

        win_mentions = ", ".join(u.mention for u in winners)

        await channel.send(embed=self.embed(

            "Giveaway Ended 🎉",

            f"**Prize:** {data['prize']}\n"

            f"**Winner(s):** {win_mentions}"

        ))

        self.giveaways.pop(message_id, None)

    # --------------------------------------------------

    # COMMANDS

    # --------------------------------------------------

    @commands.hybrid_command(name="gstart")

    @commands.has_permissions(manage_guild=True)

    async def gstart(self, ctx, duration: str, winners: int, *, prize: str):

        seconds = self.parse_time(duration)

        if not seconds:

            await ctx.send(embed=self.embed(

                "Invalid Time",

                "Use format like `10s`, `5m`, `1h`.",

                0xe74c3c

            ))

            return

        end_time = int(time.time()) + seconds

        embed = discord.Embed(

            title="🎉 Giveaway Started!",

            description=(

                f"**Prize:** {prize}\n"

                f"**Winners:** {winners}\n"

                f"**Ends:** <t:{end_time}:R>\n\n"

                f"React with 🎉 to enter!"

            ),

            color=0x2ecc71

        )

        embed.set_footer(text="Thanks for using Xtreme")

        msg = await ctx.send(embed=embed)

        await msg.add_reaction("🎉")

        self.giveaways[msg.id] = {

            "channel_id": ctx.channel.id,

            "prize": prize,

            "winners": winners,

        }

        await asyncio.sleep(seconds)

        await self.end_giveaway(ctx.channel, msg.id)

    @commands.hybrid_command(name="gend")

    @commands.has_permissions(manage_guild=True)

    async def gend(self, ctx, message_id: int):

        await self.end_giveaway(ctx.channel, message_id)

    @commands.hybrid_command(name="greroll")

    @commands.has_permissions(manage_guild=True)

    async def greroll(self, ctx, message_id: int):

        await self.end_giveaway(ctx.channel, message_id)

    @commands.hybrid_command(name="glist")

    async def glist(self, ctx):

        if not self.giveaways:

            await ctx.send(embed=self.embed(

                "Active Giveaways",

                "No active giveaways."

            ))

            return

        desc = ""

        for mid, data in self.giveaways.items():

            desc += f"• **{data['prize']}** (ID: `{mid}`)\n"

        await ctx.send(embed=self.embed(

            "Active Giveaways",

            desc

        ))

async def setup(bot: commands.Bot):

    await bot.add_cog(Giveaways(bot))