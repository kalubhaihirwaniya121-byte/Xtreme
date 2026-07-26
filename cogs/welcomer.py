import discord
import re

from discord.ext import commands

from utils.storage import load_json, save_json
from utils.emojis import Emojis

class Welcomer(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.data = load_json("welcomer.json")


    # --------------------------------------------------
    # STORAGE
    # --------------------------------------------------

    def get_guild(self, guild_id: int):

        guild_id = str(guild_id)

        if guild_id not in self.data:

            self.data[guild_id] = {

                "enabled": False,

                "channel": None,

                "message": "Welcome {user} to **{server}**!",

                "dm": False,

                "autoroles": []

            }
            self.save()

        return self.data[guild_id]

    def save(self):

        save_json(
            "welcomer.json",
            self.data
        )

    # --------------------------------------------------
    # EMBEDS
    # --------------------------------------------------

    async def success(
        self,
        ctx,
        message
    ):

        embed = discord.Embed(

            description=f"{Emojis.TICK} {message}",

            color=0x2ECC71

        )

        embed.set_footer(
            text="Thanks for using Xtreme"
        )

        await ctx.send(
            embed=embed
        )

    async def error(
        self,
        ctx,
        message
    ):

        embed = discord.Embed(

            description=f"{Emojis.CROSS} {message}",

            color=0xE74C3C

        )

        embed.set_footer(
            text="Thanks for using Xtreme"
        )

        await ctx.send(
            embed=embed
        )

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------

    def format_message(
        self,
        member: discord.Member,
        text: str
    ):

        return (

            text

            .replace(
                "{user}",
                member.mention
            )

            .replace(
                "{username}",
                member.name
            )

            .replace(
                "{server}",
                member.guild.name
            )

            .replace(
                "{membercount}",
                str(member.guild.member_count)
            )

        )

    def extract_image(
        self,
        text: str
    ):

        match = re.search(
            r"(https?://\S+\.(?:png|jpg|jpeg|gif|webp))",
            text,
            re.IGNORECASE
        )

        if match:

            return match.group(1)

        return None
    
    # --------------------------------------------------
    # WELCOMER SYSTEM
    # --------------------------------------------------

    @commands.hybrid_command(
        name="welcomer",
        description="Enable or disable the Welcomer System."
    )
    @commands.has_permissions(
        manage_guild=True
    )
    async def welcomer(
        self,

        ctx,
        action: str
    ):

        data = self.get_guild(
            ctx.guild.id
        )

        action = action.lower()

        if action == "on":

            if data["enabled"]:

                return await self.error(
                    ctx,
                    "Welcomer is already enabled."
                )

            data["enabled"] = True

            self.save()

            return await self.success(
                ctx,
                "Welcomer has been enabled."
            )

        elif action == "off":

            if not data["enabled"]:

                return await self.error(
                    ctx,
                    "Welcomer is already disabled."
                )

            data["enabled"] = False

            self.save()

            return await self.success(
                ctx,
                "Welcomer has been disabled."
            )

        else:

            return await self.error(
                ctx,
                "Usage: .welcomer on | off"
            )

    # --------------------------------------------------
    # WELCOME STATUS
    # --------------------------------------------------

    @commands.hybrid_command(
        name="welcomestatus",
        description="Show Welcomer settings."
    )
    @commands.has_permissions(
        manage_guild=True
    )
    async def welcomestatus(
        self,
        ctx
    ):

        data = self.get_guild(
            ctx.guild.id
        )

        channel = "Not Set"

        if data["channel"]:

            ch = ctx.guild.get_channel(
                data["channel"]
            )

            if ch:

                channel = ch.mention

        embed = discord.Embed(

            title=f"{Emojis.WLCM} Welcomer Status",

            color=0x5865F2

        )

        embed.add_field(
            name="Status",
            value=(
                f"{Emojis.TICK} Enabled"
                if data["enabled"]
                else f"{Emojis.CROSS} Disabled"
            ),
            inline=False
        )

        embed.add_field(
            name="Channel",
            value=channel,
            inline=False
        )

        embed.add_field(
            name="DM Welcome",
            value=(
                "Enabled"
                if data["dm"]
                else "Disabled"
            ),
            inline=True
        )

        embed.add_field(
            name="Auto Roles",
            value=str(
                len(data["autoroles"])
            ),
            inline=True
        )

        embed.set_footer(
            text="Thanks for using Xtreme"
        )

        await ctx.send(
            embed=embed
        )    

    # --------------------------------------------------
    # WELCOME CHANNEL
    # --------------------------------------------------

    @commands.hybrid_command(
        name="welcomechannel",
        description="Set the welcome channel."
    )
    @commands.has_permissions(
        manage_guild=True
    )
    async def welcomechannel(
        self,
        ctx,
        channel: discord.TextChannel
    ):

        data = self.get_guild(
            ctx.guild.id
        )

        data["channel"] = channel.id

        self.save()

        await self.success(
            ctx,
            f"{Emojis.TICK}Welcome channel set to {channel.mention}."
        )

    # --------------------------------------------------
    # WELCOME MESSAGE
    # --------------------------------------------------

    @commands.hybrid_command(
        name="welcomemessage",
        description="Set the welcome message."
    )
    @commands.has_permissions(
        manage_guild=True
    )
    async def welcomemessage(
        self,
        ctx,
        *,
        message: str
    ):

        data = self.get_guild(
            ctx.guild.id
        )

        data["message"] = message

        self.save()

        embed = discord.Embed(
            title=f"{Emojis.TICK} Welcome Message Updated",
            description=(
                "**Available Variables**\n\n"
                "`{user}` → Mention User\n"
                "`{username}` → Username\n"
                "`{server}` → Server Name\n"
                "`{membercount}` → Member Count\n\n"
                "You can also add a **GIF/Image URL** anywhere in the message."
            ),
            color=0x2ECC71
        )

        embed.set_footer(
            text="Thanks for using Xtreme"
        )

        await ctx.send(
            embed=embed
        )

    # --------------------------------------------------
    # WELCOME DM
    # --------------------------------------------------

    @commands.hybrid_command(
        name="welcomedm",
        description="Enable or disable welcome DMs."
    )
    @commands.has_permissions(
        manage_guild=True
    )
    async def welcomedm(
        self,
        ctx,
        action: str
    ):

        data = self.get_guild(
            ctx.guild.id
        )

        action = action.lower()

        if action not in (
            "on",
            "off"
        ):

            return await self.error(
                ctx,
                "Usage: .welcomedm on | off"
            )

        data["dm"] = (
            action == "on"
        )

        self.save()

        await self.success(
            ctx,
            f"Welcome DM has been **{action.upper()}**."
        )

    # --------------------------------------------------
    # WELCOME TEST
    # --------------------------------------------------

    @commands.hybrid_command(
        name="welcometest",
        description="Send a test welcome message."
    )
    @commands.has_permissions(
        manage_guild=True
    )
    async def welcometest(
        self,
        ctx
    ):

        data = self.get_guild(
            ctx.guild.id
        )

        if not data["channel"]:

            return await self.error(
                ctx,
                "No welcome channel has been configured."
            )

        channel = ctx.guild.get_channel(
            data["channel"]
        )

        if not channel:

            return await self.error(
                ctx,
                "Configured welcome channel no longer exists."
            )

        message = self.format_message(
            ctx.author,
            data["message"]
        )

        image = self.extract_image(
            message
        )

        if image:

            message = message.replace(
                image,
                ""
            ).strip()

        embed = discord.Embed(
            title=f"{Emojis.WLCM} Welcome",
            description=message,
            color=0x2ECC71
        )

        if image:

            embed.set_image(
                url=image
            )

        embed.set_footer(
            text="Thanks for using Xtreme"
        )

        await channel.send(
            embed=embed
        )

        await self.success(
            ctx,
            "Test welcome message sent."
        )

    # --------------------------------------------------
    # AUTOROLE
    # --------------------------------------------------

    @commands.hybrid_command(
        name="autorole",
        description="Manage welcome autoroles."
    )
    @commands.has_permissions(
        manage_roles=True
    )
    async def autorole(
        self,
        ctx,
        action: str,
        role: discord.Role = None
    ):

        data = self.get_guild(
            ctx.guild.id
        )

        action = action.lower()

        # ---------------- ADD ----------------

        if action == "add":

            if role is None:

                return await self.error(
                    ctx,
                    "Please mention a role."
                )

            if role.id in data["autoroles"]:

                return await self.error(
                    ctx,
                    "That role is already in Autoroles."
                )

            data["autoroles"].append(
                role.id
            )

            self.save()

            return await self.success(
                ctx,
                f"{role.mention} added to Autoroles."
            )

        # ---------------- REMOVE ----------------

        elif action == "remove":

            if role is None:

                return await self.error(
                    ctx,
                    "Please mention a role."
                )

            if role.id not in data["autoroles"]:

                return await self.error(
                    ctx,
                    "That role is not in Autoroles."
                )

            data["autoroles"].remove(
                role.id
            )

            self.save()

            return await self.success(
                ctx,
                f"{role.mention} removed from Autoroles."
            )

        # ---------------- LIST ----------------

        elif action == "list":

            if not data["autoroles"]:

                return await self.error(
                    ctx,
                    "No Autoroles have been configured."
                )

            roles = []

            for role_id in data["autoroles"]:

                role = ctx.guild.get_role(
                    role_id
                )

                if role:

                    roles.append(
                        role.mention
                    )

            embed = discord.Embed(
                title="🎭 Autoroles",
                description="\n".join(roles),
                color=0x5865F2
            )

            embed.set_footer(
                text="Thanks for using Xtreme"
            )

            return await ctx.send(
                embed=embed
            )

        else:

            return await self.error(
                ctx,
                "Usage: .autorole add/remove/list"
            )
        
    # --------------------------------------------------
    # MEMBER JOIN
    # --------------------------------------------------

    @commands.Cog.listener()
    async def on_member_join(
        self,
        member: discord.Member
    ):

        data = self.get_guild(
            member.guild.id
        )

        if not data["enabled"]:
            return

        # ---------------- AUTOROLES ----------------

        for role_id in data["autoroles"]:

            role = member.guild.get_role(
                role_id
            )

            if role:

                try:
                    await member.add_roles(
                        role,
                        reason="Welcomer Autorole"
                    )
                except discord.Forbidden:
                    pass

        # ---------------- EMBED ----------------

        message = self.format_message(
            member,
            data["message"]
        )

        image = self.extract_image(
            message
        )

        if image:

            message = message.replace(
                image,
                ""
            ).strip()

        embed = discord.Embed(

            title=f"{Emojis.WLCM} Welcome",

            description=message,

            color=0x2ECC71

        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        if image:

            embed.set_image(
                url=image
            )

        embed.set_footer(
            text=f"Member #{member.guild.member_count}"
        )

        # ---------------- CHANNEL ----------------

        if data["channel"]:

            channel = member.guild.get_channel(
                data["channel"]
            )

            if channel:

                try:
                    await channel.send(
                        embed=embed
                    )
                except discord.Forbidden:
                    pass

        # ---------------- DM ----------------

        if data["dm"]:

            try:
                await member.send(
                    embed=embed
                )
            except discord.Forbidden:
                pass


async def setup(bot):

    await bot.add_cog(
        Welcomer(bot)
    )