import discord

from discord.ext import commands

from datetime import timedelta

from utils.emojis import Emojis

# =========================

# PERMISSION HELPER (OWNER + NORMAL PERMS)

# =========================

def perms_or_owner(**perms):

    return commands.check_any(

        commands.has_permissions(**perms),

        commands.is_owner()

    )

# =========================

# CONFIRM BUTTON VIEW

# =========================

class ConfirmAction(discord.ui.View):

    def __init__(self):

        super().__init__(timeout=20)

        self.value = None

    @discord.ui.button(label=f"YES", style=discord.ButtonStyle.danger)

    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.value = True

        self.stop()

        await interaction.response.defer()

    @discord.ui.button(label=f"NO", style=discord.ButtonStyle.secondary)

    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.value = False

        self.stop()

        await interaction.response.defer()

class Moderation(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    # =========================

    # EMBED

    # =========================

    def embed(self, title, desc, color=0x2f3136):

        e = discord.Embed(title=title, description=desc, color=color)

        e.set_footer(text="Thanks for using Xtreme")

        return e

    # =========================

    # BAN COMMAND

    # =========================

    @commands.hybrid_command(name="ban")

    @perms_or_owner(ban_members=True)

    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):

        view = ConfirmAction()

        msg = await ctx.send(embed=self.embed(

            "Confirm Ban",

            f"Are you sure you want to ban **{member}**?\n**Reason:** {reason}",

            0xe74c3c

        ), view=view)

        await view.wait()

        if view.value is None or view.value is False:

            return await msg.edit(embed=self.embed("Cancelled", "Ban cancelled."), view=None)

        await member.ban(reason=reason)

        await msg.edit(embed=self.embed(

            f"{Emojis.TICK} User Banned",

            f"**{member}** has been banned.\n**Reason:** {reason}",

            0xe74c3c

        ), view=None)

    # =========================

    # KICK COMMAND

    # =========================

    @commands.hybrid_command(name="kick")

    @perms_or_owner(kick_members=True)

    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):

        view = ConfirmAction()

        msg = await ctx.send(embed=self.embed(

            "Confirm Kick",

            f"Are you sure you want to kick **{member}**?\n**Reason:** {reason}",

            0xf39c12

        ), view=view)

        await view.wait()

        if view.value is None or view.value is False:

            return await msg.edit(embed=self.embed("Cancelled", "Kick cancelled."), view=None)

        await member.kick(reason=reason)

        await msg.edit(embed=self.embed(

            f"{Emojis.TICK} User Kicked",

            f"**{member}** has been kicked.\n**Reason:** {reason}",

            0xf39c12

        ), view=None)

    # =========================

    # TIMEOUT COMMAND

    # =========================

    @commands.hybrid_command(name="timeout")

    @perms_or_owner(moderate_members=True)

    async def timeout(

        self,

        ctx,

        member: discord.Member,

        duration: int,

        unit: str,

        *,

        reason="No reason provided"

    ):

        unit = unit.lower()

        if unit not in ["s", "m", "h", "d"]:

            return await ctx.send(embed=self.embed(

                "Invalid Unit",

                "Use: s (seconds), m (minutes), h (hours), d (days)",

                0xe74c3c

            ))

        seconds = duration

        if unit == "m":

            seconds *= 60

        elif unit == "h":

            seconds *= 3600

        elif unit == "d":

            seconds *= 86400

        try:

            await member.timeout(

                timedelta(seconds=seconds),

                reason=reason

            )

        except Exception as e:

            return await ctx.send(embed=self.embed(

                f"{Emojis.CROSS} Timeout Failed",

                f"```{e}```",

                0xe74c3c

            ))

        await ctx.send(embed=self.embed(

            f"{Emojis.TICK} User Timed Out",

            f"**{member}** has been timed out for **{duration}{unit}**.\n**Reason:** {reason}",

            0x3498db

        ))

async def setup(bot):

    await bot.add_cog(Moderation(bot))