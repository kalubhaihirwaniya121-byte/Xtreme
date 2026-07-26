import discord
from discord.ext import commands

from utils.help_view import HelpView
from utils.emojis import Emojis

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="help",
        aliases=["madad"],
        description="View all Xtreme commands and categories."
        )
    async def help(self, ctx):

        view = HelpView(ctx.author)

        await ctx.send(
            view=view
        )


async def setup(bot):
    await bot.add_cog(Help(bot))