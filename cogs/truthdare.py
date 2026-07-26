import random

import discord

from discord.ext import commands

from utils.truthdare_views import TruthDareView
from utils.truthdare_loader import (
    TRUTHS,
    DARES
)


class TruthDare(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.hybrid_command(
        name="truth",
        description="Get a random truth."
    )
    async def truth(self, ctx):

        if not TRUTHS:
            return await ctx.send(
                "No truth questions found."
            )

        view = TruthDareView(
            self.bot,
            TRUTHS,
            DARES
        )

        await view.send_embed(
            ctx,
            "truth"
        )


    @commands.hybrid_command(
        name="dare",
        description="Get a random dare."
    )
    async def dare(self, ctx):

        if not DARES:
            return await ctx.send(
                "No dare questions found."
            )

        view = TruthDareView(
            self.bot,
            TRUTHS,
            DARES
        )

        await view.send_embed(
            ctx,
            "dare"
        )


    @commands.hybrid_command(
        name="tod",
        description="Truth or Dare."
    )
    async def tod(self, ctx):

        view = TruthDareView(
            self.bot,
            TRUTHS,
            DARES
        )

        await view.send_embed(
            ctx,
            "random"
        )
async def setup(bot):
    await bot.add_cog(
        TruthDare(bot)
    )