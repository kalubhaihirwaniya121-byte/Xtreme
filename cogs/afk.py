import discord

from discord.ext import commands

from datetime import datetime

from utils.emojis import Emojis

class AFK(commands.Cog):

    """AFK system"""

    def __init__(self, bot: commands.Bot):

        self.bot = bot

        # user_id -> {reason, time}

        self.afk_users = {}

    # ==========================

    # AFK COMMAND

    # ==========================

    @commands.hybrid_command(name="afk")

    async def afk(self, ctx: commands.Context, *, reason: str = "AFK"):

        self.afk_users[ctx.author.id] = {

            "reason": reason,

            "time": datetime.utcnow()

        }

        embed = discord.Embed(

            title=f"{Emojis.TICK}AFK Enabled",

            description=f"**Reason:** {reason}",

            color=0xf1c40f

        )

        await ctx.send(embed=embed)

    # ==========================

    # LISTENER

    # ==========================

    @commands.Cog.listener()

    async def on_message(self, message: discord.Message):

        if message.author.bot:

            return

        user_id = message.author.id

        # Ignore AFK command message itself

        ctx = await self.bot.get_context(message)

        if ctx.valid and ctx.command and ctx.command.name == "afk":
          
            return

        # ======================

        # REMOVE AFK (SELF)

        # ======================

        if user_id in self.afk_users:

            data = self.afk_users.pop(user_id)

            embed = discord.Embed(

                title="AFK Removed",

                description=f"{Emojis.WLCM}Welcome back {message.author.mention}!",

                color=0x2ecc71

            )

            await message.channel.send(embed=embed)

        # ======================

        # MENTION CHECK

        # ======================

        for user in message.mentions:

            if user.id in self.afk_users:

                data = self.afk_users[user.id]

                reason = data["reason"]

                embed = discord.Embed(

                    title="User is AFK",

                    description=f"**{user.display_name}** is currently AFK.\n**Reason:** {reason}",

                    color=0xe67e22

                )

                await message.channel.send(embed=embed)

async def setup(bot: commands.Bot):

    await bot.add_cog(AFK(bot))