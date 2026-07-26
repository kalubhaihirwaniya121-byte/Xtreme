import discord

from discord.ext import commands

from utils.storage import load_json, save_json

from utils.emojis import Emojis


class Media(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.data = load_json("media.json")

    # --------------------------------------------------
    # STORAGE
    # --------------------------------------------------

    def get_guild(self, guild_id: int):

        guild_id = str(guild_id)

        if guild_id not in self.data:

            self.data[guild_id] = {

                "enabled": False,

                "channels": [],

                "bypass_roles": []

            }

            save_json(
                "media.json",
                self.data
            )

        return self.data[guild_id]

    def save(self):

        save_json(
            "media.json",
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
    # MEDIA SYSTEM
    # --------------------------------------------------

    @commands.hybrid_command(
        name="media",
        description="Manage Media System."
    )
    @commands.has_permissions(
        manage_guild=True
    )
    async def media(
        self,
        ctx,
        action: str
    ):

        action = action.lower()

        data = self.get_guild(
            ctx.guild.id
        )

        if action == "on":

            if data["enabled"]:

                return await self.error(
                    ctx,
                    "Media System is already enabled."
                )

            data["enabled"] = True

            self.save()

            return await self.success(
                ctx,
                "Media System has been enabled."
            )
        elif action == "off":

            if not data["enabled"]:

                return await self.error(
                    ctx,
                    "Media System is already disabled."
                )

            data["enabled"] = False

            self.save()

            return await self.success(
                ctx,
                "Media System has been disabled."
            )

        elif action == "status":

            embed = discord.Embed(

                title="📸 Media System",

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

                name="Media Channels",

                value=str(
                    len(data["channels"])
                ),

                inline=True

            )

            embed.add_field(

                name="Bypass Roles",

                value=str(
                    len(data["bypass_roles"])
                ),

                inline=True

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
                "Usage: .media on | off | status"
            )

    # --------------------------------------------------
    # MEDIA CHANNEL
    # --------------------------------------------------

    @commands.hybrid_command(
        name="mediachannel",
        description="Manage media channels."
    )
    @commands.has_permissions(
        manage_guild=True
    )
    async def mediachannel(
        self,
        ctx,
        action: str,
        channel: discord.TextChannel = None
    ):

        data = self.get_guild(
            ctx.guild.id
        )

        action = action.lower()

        if action == "add":

            if channel is None:

                return await self.error(
                    ctx,
                    "Please mention a channel."
                )

            if channel.id in data["channels"]:

                return await self.error(
                    ctx,
                    "That channel is already configured."
                )

            data["channels"].append(
                channel.id
            )

            self.save()

            return await self.success(
                ctx,
                f"{channel.mention} added as a Media Channel."
            )
        elif action == "remove":

            if channel is None:

                return await self.error(
                    ctx,
                    "Please mention a channel."
                )

            if channel.id not in data["channels"]:

                return await self.error(
                    ctx,
                    "That channel is not configured."
                )

            data["channels"].remove(
                channel.id
            )

            self.save()

            return await self.success(
                ctx,
                f"{channel.mention} removed from Media Channels."
            )

        elif action == "list":

            if not data["channels"]:

                return await self.error(
                    ctx,
                    "No Media Channels have been configured."
                )

            channels = []

            for channel_id in data["channels"]:

                ch = ctx.guild.get_channel(
                    channel_id
                )

                if ch:

                    channels.append(
                        ch.mention
                    )

            embed = discord.Embed(

                title="📸 Media Channels",

                description="\n".join(channels),

                color=0x5865F2

            )

            embed.set_footer(
                text="Thanks for using Xtreme"
            )

            await ctx.send(
                embed=embed
            )

        else:

            return await self.error(
                ctx,
                "Usage: .mediachannel add/remove/list"
            )

    # --------------------------------------------------
    # MEDIA BYPASS
    # --------------------------------------------------

    @commands.hybrid_command(
        name="mediabypass",
        description="Manage media bypass roles."
    )
    @commands.has_permissions(
        manage_guild=True
    )
    async def mediabypass(
        self,
        ctx,
        action: str,
        role: discord.Role = None
    ):

        data = self.get_guild(
            ctx.guild.id
        )

        action = action.lower()

        if action == "add":

            if role is None:

                return await self.error(
                    ctx,
                    "Please mention a role."
                )

            if role.id in data["bypass_roles"]:

                return await self.error(
                    ctx,
                    "That role is already configured."
                )

            data["bypass_roles"].append(
                role.id
            )

            self.save()

            return await self.success(
                ctx,
                f"{role.mention} added as a Media Bypass Role."
            )
        elif action == "remove":

            if role is None:

                return await self.error(
                    ctx,
                    "Please mention a role."
                )

            if role.id not in data["bypass_roles"]:

                return await self.error(
                    ctx,
                    "That role is not configured."
                )

            data["bypass_roles"].remove(
                role.id
            )

            self.save()

            return await self.success(
                ctx,
                f"{role.mention} removed from Media Bypass Roles."
            )

        elif action == "list":

            if not data["bypass_roles"]:

                return await self.error(
                    ctx,
                    "No Media Bypass Roles have been configured."
                )

            roles = []

            for role_id in data["bypass_roles"]:

                role = ctx.guild.get_role(
                    role_id
                )

                if role:

                    roles.append(
                        role.mention
                    )

            embed = discord.Embed(

                title="📸 Media Bypass Roles",

                description="\n".join(roles),

                color=0x5865F2

            )

            embed.set_footer(
                text="Thanks for using Xtreme"
            )

            await ctx.send(
                embed=embed
            )

        else:

            return await self.error(
                ctx,
                "Usage: .mediabypass add/remove/list"
            )

    # --------------------------------------------------
    # MEDIA LINK CHECK
    # --------------------------------------------------

    @staticmethod
    def is_media_link(content: str):

        content = content.lower()

        media_domains = (

            "cdn.discordapp.com",
            "media.discordapp.net",

            "media.tenor.com",
            "tenor.com",

            "giphy.com",

            "imgur.com",
            "i.imgur.com",

            "catbox.moe",

            "youtu.be",
            "youtube.com"
        )

        media_extensions = (

            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp",

            ".mp4",
            ".mov",
            ".avi",
            ".webm",

            ".mp3",
            ".wav",
            ".ogg"
        )

        return (

            any(
                domain in content
                for domain in media_domains
            )

            or

            any(
                content.endswith(ext)
                for ext in media_extensions
            )

        )
        # --------------------------------------------------
    # MEDIA FILTER
    # --------------------------------------------------

    @commands.Cog.listener()
    async def on_message(
        self,
        message: discord.Message
    ):

        if message.author.bot:
            return

        if not message.guild:
            return

        data = self.get_guild(
            message.guild.id
        )

        if not data["enabled"]:
            return

        if message.channel.id not in data["channels"]:
            return

        if any(
            role.id in data["bypass_roles"]
            for role in message.author.roles
        ):
            return

        has_media = False

        if message.attachments:
            has_media = True

        elif self.is_media_link(
            message.content
        ):
            has_media = True

        if has_media:
            return

        try:

            await message.delete()

            embed = discord.Embed(

                description=(
                    f"{Emojis.CROSS} {message.author.mention}, "
                    "this is a **Media Only Channel**."
                ),

                color=0xE74C3C

            )

            embed.set_footer(
                text="Thanks for using Xtreme"
            )

            warning = await message.channel.send(
                embed=embed
            )

            await warning.delete(
                delay=5
            )

        except discord.Forbidden:
            pass

        except discord.HTTPException:
            pass

    @commands.Cog.listener()
    async def on_message_edit(
        self,
        before: discord.Message,
        after: discord.Message
    ):

        await self.on_message(after)


async def setup(bot):

    await bot.add_cog(
        Media(bot)
    )