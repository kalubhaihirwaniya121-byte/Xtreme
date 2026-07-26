import discord
import json
import os
from utils.emojis import Emojis
from discord.ext import commands

WHITELIST_FILE = "whitelist.json"


def load_whitelist():

    if not os.path.exists(WHITELIST_FILE):
        return {"users": []}

    with open(
        WHITELIST_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


class Gif(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        if message.content.strip().upper() != "XTREME":
            return

        whitelist = load_whitelist()

        is_owner = await self.bot.is_owner(
            message.author
        )

        if (
            not is_owner
            and
            message.author.id
            not in whitelist["users"]
        ):
            return

        embed = discord.Embed(
            title=f"Hello",
            color=0x5865F2
        )

        embed.set_image(
            url="https://cdn.discordapp.com/attachments/1459572888838344708/1530924775466205194/image0.gif?ex=6a67584d&is=6a6606cd&hm=5938ba4f8e4157b97302e7d6dad53718749b1ab545a12087641f65a6f03c648b&"
        )

        await message.channel.send(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(Gif(bot))