import discord
from discord.ext import commands

from utils.logging_utils import (
    load_logging,
    save_logging,
    get_guild_logging,
    update_guild_logging,
    remove_guild_logging
)

from utils.emojis import Emojis

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _get_config(self, guild):
        if guild is None:
            return None

        config = get_guild_logging(guild.id)
        if not config or not config.get("enabled"):
            return None

        return config

    def _get_log_channel(self, guild, key):
        config = self._get_config(guild)
        if config is None:
            return None

        return guild.get_channel(config.get(key))

    def _mention(self, obj, fallback="Unknown"):
        return getattr(obj, "mention", None) or fallback

    def _build_embed(self, title, color, timestamp=True):
        embed = discord.Embed(title=title, color=color)
        if timestamp:
            embed.timestamp = discord.utils.utcnow()
        embed.set_footer(text="Xtreme Logging")
        return embed

    async def _send_embed(self, channel, embed):
        if channel is None or embed is None:
            return

        try:
            await channel.send(embed=embed)
        except (discord.Forbidden, discord.HTTPException):
            pass

    async def _cleanup_category(self, category):
        if category is None:
            return

        for channel in category.channels:
            try:
                await channel.delete()
            except (discord.Forbidden, discord.HTTPException):
                pass

        try:
            await category.delete()
        except (discord.Forbidden, discord.HTTPException):
            pass

    async def _fetch_audit_info(self, guild, action, target_id=None, within_seconds=10, predicate=None):
        moderator = "Unknown"
        reason = "No reason provided"

        if guild is None:
            return moderator, reason

        now = discord.utils.utcnow()
        try:
            async for entry in guild.audit_logs(limit=6, action=action):
                if target_id is not None and getattr(entry.target, "id", None) != target_id:
                    continue
                if predicate and not predicate(entry):
                    continue
                if (now - entry.created_at).total_seconds() <= within_seconds:
                    moderator = entry.user.mention if entry.user else "Unknown"
                    reason = entry.reason or "No reason provided"
                    break
        except (discord.Forbidden, discord.HTTPException):
            pass

        return moderator, reason

    @commands.group(
        name="logging",
        aliases=["logs"],
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def logging(self, ctx):
        embed = discord.Embed(
            title=f"{Emojis.SETTINGS} Xtreme Logging",
            description=(
                f"`{ctx.prefix}logging setup` - Setup logging system\n"
                f"`{ctx.prefix}logging status` - View logging status\n"
                f"`{ctx.prefix}logging reset` - Reset logging system\n"
                f"`{ctx.prefix}logging remove` - Remove logging system"
            ),
            color=discord.Color.blurple()
        )

        embed.set_footer(
            text="Xtreme Logging System"
        )

        await ctx.send(embed=embed)
        
    @logging.command(name="setup")
    @commands.has_permissions(manage_guild=True)
    async def setup(self, ctx):
        guild = ctx.guild
        if guild is None:
            return

        try:
            old_category = discord.utils.get(guild.categories, name="Xtreme Logs")
            await self._cleanup_category(old_category)

            category = await guild.create_category("Xtreme Logs")

            join_leave = await guild.create_text_channel(
                "join-leave-log",
                category=category
            )

            mod_log = await guild.create_text_channel(
                "mod-log",
                category=category
            )

            msg_log = await guild.create_text_channel(
                "msg-log",
                category=category
            )

            voice_log = await guild.create_text_channel(
                "voice-log",
                category=category
            )

            update_guild_logging(
                guild.id,
                {
                    "category": category.id,
                    "join_leave": join_leave.id,
                    "mod": mod_log.id,
                    "message": msg_log.id,
                    "voice": voice_log.id,
                    "enabled": True
                }
            )

            embed = discord.Embed(
                title=f"{Emojis.TICK} Logging Setup Complete",
                description="Xtreme Logging System has been configured successfully.",
                color=discord.Color.green()
            )

            embed.add_field(
                name="Category",
                value=category.mention,
                inline=False
            )

            embed.add_field(
                name="Channels",
                value=(
                    f"{join_leave.mention}\n"
                    f"{mod_log.mention}\n"
                    f"{msg_log.mention}\n"
                    f"{voice_log.mention}"
                ),
                inline=False
            )

            embed.set_footer(text="Xtreme Logging System")

            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title=f"{Emojis.ERROR} Missing Permissions",
                description="I need Manage Channels permission to setup logging.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except discord.HTTPException:
            embed = discord.Embed(
                title=f"{Emojis.ERROR} Setup Failed",
                description="Unable to configure logging channels due to an unexpected error.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        
    @logging.command(name="status")
    @commands.has_permissions(manage_guild=True)
    async def status(self, ctx):
        config = get_guild_logging(ctx.guild.id)

        if not config:
            embed = discord.Embed(
                title=f"{Emojis.ERROR} Logging Not Configured",
                description=(
                    f"Run `{ctx.prefix}logging setup` to configure the logging system."
                ),
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        category = ctx.guild.get_channel(config.get("category"))
        join_leave = ctx.guild.get_channel(config.get("join_leave"))
        mod_log = ctx.guild.get_channel(config.get("mod"))
        msg_log = ctx.guild.get_channel(config.get("message"))
        voice_log = ctx.guild.get_channel(config.get("voice"))

        embed = discord.Embed(
            title=f"{Emojis.SETTINGS} Logging Status",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Status",
            value="🟢 Enabled" if config.get("enabled") else "🔴 Disabled",
            inline=False
        )

        embed.add_field(
            name="Category",
            value=category.mention if category else "`Not Found`",
            inline=False
        )

        embed.add_field(
            name="Channels",
            value=(
                f"**Join Log:** {join_leave.mention if join_leave else '`Missing`'}\n"
                f"**Mod Log:** {mod_log.mention if mod_log else '`Missing`'}\n"
                f"**Message Log:** {msg_log.mention if msg_log else '`Missing`'}\n"
                f"**Voice Log:** {voice_log.mention if voice_log else '`Missing`'}"
            ),
            inline=False
        )

        embed.set_footer(text="Xtreme Logging System")

        await ctx.send(embed=embed)
        
    @logging.command(name="reset")
    @commands.has_permissions(manage_guild=True)
    async def reset(self, ctx):
        guild = ctx.guild

        # Delete existing logging category
        category = discord.utils.get(guild.categories, name="Xtreme Logs")
        if category:
            for channel in category.channels:
                await channel.delete()
            await category.delete()

        remove_guild_logging(guild.id)

        # Create new category
        category = await guild.create_category("Xtreme Logs")

        join_leave = await guild.create_text_channel(
            "join-leave-log",
            category=category
        )

        mod_log = await guild.create_text_channel(
            "mod-log",
            category=category
        )

        msg_log = await guild.create_text_channel(
            "msg-log",
            category=category
        )

        voice_log = await guild.create_text_channel(
            "voice-log",
            category=category
        )

        update_guild_logging(
            guild.id,
            {
                "category": category.id,
                "join_leave": join_leave.id,
                "mod": mod_log.id,
                "message": msg_log.id,
                "voice": voice_log.id,
                "enabled": True
            }
        )

        embed = discord.Embed(
            title=f"{Emojis.TICK} Logging Reset Complete",
            description="The logging system has been reset successfully.",
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)
        
    @logging.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def remove(self, ctx):
        guild = ctx.guild

        category = discord.utils.get(guild.categories, name="Xtreme Logs")

        if category:
            for channel in category.channels:
                await channel.delete()

            await category.delete()

        remove_guild_logging(guild.id)

        embed = discord.Embed(
            title=f"{Emojis.TICK} Logging Removed",
            description="The Xtreme Logging System has been removed successfully.",
            color=discord.Color.green()
        )

        embed.set_footer(text="Xtreme Logging System")

        await ctx.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        config = get_guild_logging(member.guild.id)

        if not config or not config.get("enabled"):
            return

        channel = member.guild.get_channel(config.get("join_leave"))
        if channel is None:
            return

        roles = [
            role.mention
            for role in member.roles
            if role != member.guild.default_role
        ]

        role_text = ", ".join(roles) if roles else "No Roles"

        embed = discord.Embed(
            title="📥 Member Joined",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(
            name="👤 User",
            value=f"{member.mention}\n`{member.id}`",
            inline=False
        )

        embed.add_field(
            name="📅 Account Created",
            value=discord.utils.format_dt(member.created_at, style="F"),
            inline=False
        )

        embed.add_field(
            name="🎭 Roles",
            value=role_text,
            inline=False
        )

        embed.add_field(
            name="👥 Member Count",
            value=str(member.guild.member_count),
            inline=False
        )

        embed.set_footer(
            text="Xtreme Logging"
        )

        await channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        config = get_guild_logging(member.guild.id)

        if not config or not config.get("enabled"):
            return

        channel = member.guild.get_channel(config.get("join_leave"))
        if channel is None:
            return

        roles = [
            role.mention
            for role in member.roles
            if role != member.guild.default_role
        ]

        role_text = ", ".join(roles) if roles else "No Roles"

        joined_at = (
            discord.utils.format_dt(member.joined_at, style="F")
            if member.joined_at else "Unknown"
        )

        stayed = "Unknown"
        if member.joined_at:
            delta = discord.utils.utcnow() - member.joined_at
            days = delta.days
            hours = delta.seconds // 3600
            stayed = f"{days} Days, {hours} Hours"

        embed = discord.Embed(
            title="📤 Member Left",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(
            name="👤 User",
            value=f"{member}\n`{member.id}`",
            inline=False
        )

        embed.add_field(
            name="📅 Joined Server",
            value=joined_at,
            inline=False
        )

        embed.add_field(
            name="⌛ Time in Server",
            value=stayed,
            inline=False
        )

        embed.add_field(
            name="🎭 Roles",
            value=role_text,
            inline=False
        )

        embed.add_field(
            name="👥 Member Count",
            value=str(member.guild.member_count),
            inline=False
        )

        embed.set_footer(text="Xtreme Logging")

        await channel.send(embed=embed)

        # Kick detection using audit logs instead of unban listener
        try:
            async for entry in member.guild.audit_logs(
                limit=5,
                action=discord.AuditLogAction.kick
            ):
                if (
                    entry.target is not None
                    and getattr(entry.target, "id", None) == member.id
                    and (discord.utils.utcnow() - entry.created_at).total_seconds() <= 10
                ):
                    kick_channel = member.guild.get_channel(config.get("mod"))
                    if kick_channel is None:
                        break

                    kick_embed = discord.Embed(
                        title="👢 Member Kicked",
                        color=discord.Color.orange(),
                        timestamp=discord.utils.utcnow()
                    )

                    kick_embed.set_thumbnail(url=member.display_avatar.url)

                    kick_embed.add_field(
                        name="👤 User",
                        value=f"{member}\n`{member.id}`",
                        inline=False
                    )

                    kick_embed.add_field(
                        name="👮 Moderator",
                        value=entry.user.mention if entry.user else "Unknown",
                        inline=True
                    )

                    kick_embed.add_field(
                        name="📝 Reason",
                        value=entry.reason or "No reason provided",
                        inline=True
                    )

                    kick_embed.set_footer(text="Xtreme Logging")

                    await kick_channel.send(embed=kick_embed)
                    break
        except discord.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild is None or message.author.bot:
            return

        config = get_guild_logging(message.guild.id)

        if not config or not config.get("enabled"):
            return

        channel = message.guild.get_channel(config.get("message"))
        if channel is None:
            return

        content = message.content if message.content else "*No message content.*"

        if len(content) > 1024:
            content = content[:1021] + "..."

        embed = discord.Embed(
            title="💬 Message Deleted",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )

        embed.set_thumbnail(url=message.author.display_avatar.url)

        embed.add_field(
            name="👤 Author",
            value=f"{message.author.mention}\n`{message.author.id}`",
            inline=False
        )

        embed.add_field(
            name="📍 Channel",
            value=message.channel.mention,
            inline=False
        )

        embed.add_field(
            name="📝 Content",
            value=content,
            inline=False
        )

        embed.add_field(
            name="🆔 Message ID",
            value=f"`{message.id}`",
            inline=False
        )

        if message.attachments:
            embed.add_field(
                name="📎 Attachments",
                value="\n".join(a.url for a in message.attachments[:5]),
                inline=False
            )

        embed.set_footer(text="Xtreme Logging")

        await channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.guild is None or before.author.bot:
            return

        if before.content == after.content:
            return

        config = get_guild_logging(before.guild.id)

        if not config or not config.get("enabled"):
            return

        channel = before.guild.get_channel(config.get("message"))
        if channel is None:
            return

        before_content = before.content or "*No Content*"
        after_content = after.content or "*No Content*"

        if len(before_content) > 1024:
            before_content = before_content[:1021] + "..."

        if len(after_content) > 1024:
            after_content = after_content[:1021] + "..."

        embed = discord.Embed(
            title="✏️ Message Edited",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow()
        )

        embed.set_thumbnail(url=before.author.display_avatar.url)

        embed.add_field(
            name="👤 Author",
            value=f"{before.author.mention}\n`{before.author.id}`",
            inline=False
        )

        embed.add_field(
            name="📍 Channel",
            value=before.channel.mention,
            inline=False
        )

        embed.add_field(
            name="📝 Before",
            value=before_content,
            inline=False
        )

        embed.add_field(
            name="📝 After",
            value=after_content,
            inline=False
        )

        embed.add_field(
            name="🔗 Jump to Message",
            value=f"[Click Here]({after.jump_url})",
            inline=False
        )

        embed.set_footer(text="Xtreme Logging")

        await channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        config = get_guild_logging(member.guild.id)

        if not config or not config.get("enabled"):
            return

        channel = member.guild.get_channel(config.get("voice"))
        if channel is None:
            return

        embed = None

        # Joined Voice
        if before.channel is None and after.channel is not None:
            embed = discord.Embed(
                title="🔊 Voice Joined",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )

            embed.add_field(
                name="👤 User",
                value=f"{member.mention}\n`{member.id}`",
                inline=False
            )

            embed.add_field(
                name="🎤 Channel",
                value=after.channel.mention,
                inline=False
            )

        # Left Voice
        elif before.channel is not None and after.channel is None:
            embed = discord.Embed(
                title="🚪 Voice Left",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )

            embed.add_field(
                name="👤 User",
                value=f"{member.mention}\n`{member.id}`",
                inline=False
            )

            embed.add_field(
                name="🎤 Channel",
                value=before.channel.mention,
                inline=False
            )

        # Moved Voice
        elif (
            before.channel is not None
            and after.channel is not None
            and before.channel != after.channel
        ):
            embed = discord.Embed(
                title="🔄 Voice Moved",
                color=discord.Color.blurple(),
                timestamp=discord.utils.utcnow()
            )

            embed.add_field(
                name="👤 User",
                value=f"{member.mention}\n`{member.id}`",
                inline=False
            )

            embed.add_field(
                name="From",
                value=before.channel.mention,
                inline=True
            )

            embed.add_field(
                name="To",
                value=after.channel.mention,
                inline=True
            )

        embeds = []

        if embed:
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text="Xtreme Logging")
            embeds.append(embed)

        # Server Muted
        if before.mute != after.mute:
            mute_embed = discord.Embed(
                title="🔇 Server Muted" if after.mute else "🔊 Server Unmuted",
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )

            mute_embed.add_field(
                name="👤 User",
                value=f"{member.mention}\n`{member.id}`",
                inline=False
            )

            mute_embed.set_thumbnail(url=member.display_avatar.url)
            mute_embed.set_footer(text="Xtreme Logging")
            embeds.append(mute_embed)

        # Server Deafened
        if before.deaf != after.deaf:
            deaf_embed = discord.Embed(
                title="🎧 Server Deafened" if after.deaf else "🎧 Server Undeafened",
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )

            deaf_embed.add_field(
                name="👤 User",
                value=f"{member.mention}\n`{member.id}`",
                inline=False
            )

            deaf_embed.set_thumbnail(url=member.display_avatar.url)
            deaf_embed.set_footer(text="Xtreme Logging")
            embeds.append(deaf_embed)

        # Stream Started / Ended
        if before.self_stream != after.self_stream:
            stream_embed = discord.Embed(
                title="📺 Stream Started" if after.self_stream else "📺 Stream Ended",
                color=discord.Color.blurple(),
                timestamp=discord.utils.utcnow()
            )

            stream_embed.add_field(
                name="👤 User",
                value=f"{member.mention}\n`{member.id}`",
                inline=False
            )

            if after.channel:
                stream_embed.add_field(
                    name="🎤 Channel",
                    value=after.channel.mention,
                    inline=False
                )

            stream_embed.set_thumbnail(url=member.display_avatar.url)
            stream_embed.set_footer(text="Xtreme Logging")
            embeds.append(stream_embed)

        # Camera Enabled / Disabled
        if before.self_video != after.self_video:
            video_embed = discord.Embed(
                title="📹 Camera Enabled" if after.self_video else "📹 Camera Disabled",
                color=discord.Color.blurple(),
                timestamp=discord.utils.utcnow()
            )

            video_embed.add_field(
                name="👤 User",
                value=f"{member.mention}\n`{member.id}`",
                inline=False
            )

            if after.channel:
                video_embed.add_field(
                    name="🎤 Channel",
                    value=after.channel.mention,
                    inline=False
                )

            video_embed.set_thumbnail(url=member.display_avatar.url)
            video_embed.set_footer(text="Xtreme Logging")
            embeds.append(video_embed)

        for embed in embeds:
            await channel.send(embed=embed)
                
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        config = get_guild_logging(guild.id)

        if not config or not config.get("enabled"):
            return

        log_channel = guild.get_channel(config.get("mod"))
        if log_channel is None:
            return

        moderator = "Unknown"
        reason = "No reason provided"

        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                if entry.target.id == user.id:
                    moderator = entry.user.mention
                    reason = entry.reason or "No reason provided"
                    break
        except discord.Forbidden:
            pass

        embed = discord.Embed(
            title="🔨 Member Banned",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )

        embed.set_thumbnail(url=user.display_avatar.url)

        embed.add_field(
            name="👤 User",
            value=f"{user.mention}\n`{user.id}`",
            inline=False
        )

        embed.add_field(
            name="👮 Moderator",
            value=moderator,
            inline=True
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=True
        )

        embed.set_footer(text="Xtreme Logging")

        await log_channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        config = get_guild_logging(guild.id)

        if not config or not config.get("enabled"):
            return

        log_channel = guild.get_channel(config.get("mod"))
        if log_channel is None:
            return

        moderator = "Unknown"
        reason = "No reason provided"

        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
                if entry.target.id == user.id:
                    moderator = entry.user.mention
                    reason = entry.reason or "No reason provided"
                    break
        except discord.Forbidden:
            pass

        embed = discord.Embed(
            title="🔓 Member Unbanned",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )

        embed.set_thumbnail(url=user.display_avatar.url)

        embed.add_field(
            name="👤 User",
            value=f"{user.mention}\n`{user.id}`",
            inline=False
        )

        embed.add_field(
            name="👮 Moderator",
            value=moderator,
            inline=True
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=True
        )

        embed.set_footer(text="Xtreme Logging")

        await log_channel.send(embed=embed)
          
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        config = get_guild_logging(after.guild.id)

        if not config or not config.get("enabled"):
            return

        log_channel = after.guild.get_channel(config.get("mod"))
        if log_channel is None:
            return

        before_timeout = before.timed_out_until
        after_timeout = after.timed_out_until

        if before_timeout == after_timeout:
            return

        moderator = "Unknown"
        reason = "No reason provided"

        try:
            async for entry in after.guild.audit_logs(
                limit=5,
                action=discord.AuditLogAction.member_update
            ):
                if (
                    entry.target.id == after.id
                    and (discord.utils.utcnow() - entry.created_at).total_seconds() <= 10
                ):
                    moderator = entry.user.mention
                    reason = entry.reason or "No reason provided"
                    break
        except discord.Forbidden:
            pass

        if after_timeout:
            embed = discord.Embed(
                title="⏳ Member Timed Out",
                color=discord.Color.orange(),
                timestamp=discord.utils.utcnow()
            )

            embed.add_field(
                name="👤 User",
                value=f"{after.mention}\n`{after.id}`",
                inline=False
            )

            embed.add_field(
                name="👮 Moderator",
                value=moderator,
                inline=True
            )

            embed.add_field(
                name="📝 Reason",
                value=reason,
                inline=True
            )

            embed.add_field(
                name="⏰ Timeout Until",
                value=discord.utils.format_dt(after_timeout, style="F"),
                inline=False
            )

        else:
            embed = discord.Embed(
                title="✅ Timeout Removed",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )

            embed.add_field(
                name="👤 User",
                value=f"{after.mention}\n`{after.id}`",
                inline=False
            )

            embed.add_field(
                name="👮 Moderator",
                value=moderator,
                inline=True
            )

            embed.add_field(
                name="📝 Reason",
                value=reason,
                inline=True
            )

        embed.set_thumbnail(url=after.display_avatar.url)
        embed.set_footer(text="Xtreme Logging")

        await log_channel.send(embed=embed)
        
        # ==========================
        # Member Role Add / Remove
        # ==========================

        before_roles = set(before.roles)
        after_roles = set(after.roles)

        added_roles = after_roles - before_roles
        removed_roles = before_roles - after_roles

        if added_roles or removed_roles:

            moderator = "Unknown"
            reason = "No reason provided"

            try:
                async for entry in after.guild.audit_logs(
                    limit=5,
                    action=discord.AuditLogAction.member_role_update
                ):
                    if (
                        entry.target.id == after.id
                        and (discord.utils.utcnow() - entry.created_at).total_seconds() <= 10
                    ):
                        moderator = entry.user.mention
                        reason = entry.reason or "No reason provided"
                        break
            except discord.Forbidden:
                pass

            if added_roles:
                embed = discord.Embed(
                    title="➕ Member Roles Updated",
                    color=discord.Color.green(),
                    timestamp=discord.utils.utcnow()
                )

                embed.add_field(
                    name="👤 Member",
                    value=f"{after.mention}\n`{after.id}`",
                    inline=False
                )

                embed.add_field(
                    name="🎭 Added Roles",
                    value="\n".join(role.mention for role in added_roles),
                    inline=False
                )

            else:
                embed = discord.Embed(
                    title="➖ Member Roles Updated",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )

                embed.add_field(
                    name="👤 Member",
                    value=f"{after.mention}\n`{after.id}`",
                    inline=False
                )

                embed.add_field(
                    name="🎭 Removed Roles",
                    value="\n".join(role.mention for role in removed_roles),
                    inline=False
                )

            embed.add_field(
                name="👮 Moderator",
                value=moderator,
                inline=True
            )

            embed.add_field(
                name="📝 Reason",
                value=reason,
                inline=True
            )

            embed.set_thumbnail(url=after.display_avatar.url)
            embed.set_footer(text="Xtreme Logging")

            await log_channel.send(embed=embed)
            
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        config = get_guild_logging(role.guild.id)

        if not config or not config.get("enabled"):
            return

        log_channel = role.guild.get_channel(config.get("mod"))
        if log_channel is None:
            return

        moderator = "Unknown"
        reason = "No reason provided"

        try:
            async for entry in role.guild.audit_logs(
                limit=5,
                action=discord.AuditLogAction.role_create
            ):
                if (
                    entry.target.id == role.id
                    and (discord.utils.utcnow() - entry.created_at).total_seconds() <= 10
                ):
                    moderator = entry.user.mention
                    reason = entry.reason or "No reason provided"
                    break
        except discord.Forbidden:
            pass

        permissions = [
            name.replace("_", " ").title()
            for name, value in role.permissions
            if value
        ]

        embed = discord.Embed(
            title="🎭 Role Created",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )

        embed.set_thumbnail(url=role.guild.icon.url if role.guild.icon else None)

        embed.add_field(
            name="Role",
            value=f"{role.mention}\n`{role.id}`",
            inline=False
        )

        embed.add_field(
            name="👮 Moderator",
            value=moderator,
            inline=True
        )

        embed.add_field(
            name="🎨 Color",
            value=str(role.color),
            inline=True
        )

        embed.add_field(
            name="📌 Position",
            value=str(role.position),
            inline=True
        )

        embed.add_field(
            name="🔑 Permissions",
            value=", ".join(permissions[:15]) or "None",
            inline=False
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )

        embed.set_footer(text="Xtreme Logging")

        await log_channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        config = get_guild_logging(role.guild.id)

        if not config or not config.get("enabled"):
            return

        log_channel = role.guild.get_channel(config.get("mod"))
        if log_channel is None:
            return

        moderator = "Unknown"
        reason = "No reason provided"

        try:
            async for entry in role.guild.audit_logs(
                limit=5,
                action=discord.AuditLogAction.role_delete
            ):
                if (
                    entry.target.id == role.id
                    and (discord.utils.utcnow() - entry.created_at).total_seconds() <= 10
                ):
                    moderator = entry.user.mention
                    reason = entry.reason or "No reason provided"
                    break
        except discord.Forbidden:
            pass

        permissions = [
            name.replace("_", " ").title()
            for name, value in role.permissions
            if value
        ]

        embed = discord.Embed(
            title="🗑️ Role Deleted",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )

        if role.guild.icon:
            embed.set_thumbnail(url=role.guild.icon.url)

        embed.add_field(
            name="Role",
            value=f"**{role.name}**\n`{role.id}`",
            inline=False
        )

        embed.add_field(
            name="👮 Moderator",
            value=moderator,
            inline=True
        )

        embed.add_field(
            name="🎨 Color",
            value=str(role.color),
            inline=True
        )

        embed.add_field(
            name="📌 Position",
            value=str(role.position),
            inline=True
        )

        embed.add_field(
            name="🔑 Permissions",
            value=", ".join(permissions[:15]) or "None",
            inline=False
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )

        embed.set_footer(text="Xtreme Logging")

        await log_channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        config = get_guild_logging(after.guild.id)

        if not config or not config.get("enabled"):
            return

        log_channel = after.guild.get_channel(config.get("mod"))
        if log_channel is None:
            return

        moderator = "Unknown"
        reason = "No reason provided"

        try:
            async for entry in after.guild.audit_logs(
                limit=5,
                action=discord.AuditLogAction.role_update
            ):
                if (
                    entry.target.id == after.id
                    and (discord.utils.utcnow() - entry.created_at).total_seconds() <= 10
                ):
                    moderator = entry.user.mention
                    reason = entry.reason or "No reason provided"
                    break
        except discord.Forbidden:
            pass

        changes = []

        if before.name != after.name:
            changes.append(
                f"**Name**\n`{before.name}` → `{after.name}`"
            )

        if before.color != after.color:
            changes.append(
                f"**Color**\n`{before.color}` → `{after.color}`"
            )

        if before.hoist != after.hoist:
            changes.append(
                f"**Hoist**\n`{before.hoist}` → `{after.hoist}`"
            )

        if before.mentionable != after.mentionable:
            changes.append(
                f"**Mentionable**\n`{before.mentionable}` → `{after.mentionable}`"
            )

        if before.position != after.position:
            changes.append(
                f"**Position**\n`{before.position}` → `{after.position}`"
            )

        if before.permissions != after.permissions:
            changes.append("**Permissions Updated**")

        if getattr(before, "icon", None) != getattr(after, "icon", None):
            changes.append("**Role Icon Updated**")

        if getattr(before, "unicode_emoji", None) != getattr(after, "unicode_emoji", None):
            changes.append("**Role Emoji Updated**")

        if not changes:
            return

        embed = discord.Embed(
            title="📝 Role Updated",
            color=discord.Color.blurple(),
            timestamp=discord.utils.utcnow()
        )

        if after.guild.icon:
            embed.set_thumbnail(url=after.guild.icon.url)

        embed.add_field(
            name="🎭 Role",
            value=f"{after.mention}\n`{after.id}`",
            inline=False
        )

        embed.add_field(
            name="🔄 Changes",
            value="\n\n".join(changes),
            inline=False
        )

        embed.add_field(
            name="👮 Moderator",
            value=moderator,
            inline=True
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=True
        )

        embed.set_footer(text="Xtreme Logging")

        await log_channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        config = get_guild_logging(channel.guild.id)

        if not config or not config.get("enabled"):
            return

        log_channel = channel.guild.get_channel(config.get("mod"))
        if log_channel is None:
            return

        moderator = "Unknown"
        reason = "No reason provided"

        try:
            async for entry in channel.guild.audit_logs(
                limit=5,
                action=discord.AuditLogAction.channel_create
            ):
                if (
                    entry.target.id == channel.id
                    and (discord.utils.utcnow() - entry.created_at).total_seconds() <= 10
                ):
                    moderator = entry.user.mention
                    reason = entry.reason or "No reason provided"
                    break
        except discord.Forbidden:
            pass

        if isinstance(channel, discord.TextChannel):
            channel_type = "💬 Text Channel"
        elif isinstance(channel, discord.VoiceChannel):
            channel_type = "🔊 Voice Channel"
        elif isinstance(channel, discord.CategoryChannel):
            channel_type = "📁 Category"
        elif isinstance(channel, discord.StageChannel):
            channel_type = "🎙️ Stage Channel"
        elif hasattr(discord, "ForumChannel") and isinstance(channel, discord.ForumChannel):
            channel_type = "🧵 Forum Channel"
        else:
            channel_type = str(channel.type).title()

        embed = discord.Embed(
            title="📁 Channel Created",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )

        if channel.guild.icon:
            embed.set_thumbnail(url=channel.guild.icon.url)

        embed.add_field(
            name="📂 Channel",
            value=f"{channel.mention if hasattr(channel, 'mention') else channel.name}\n`{channel.id}`",
            inline=False
        )

        embed.add_field(
            name="📌 Type",
            value=channel_type,
            inline=True
        )

        embed.add_field(
            name="📍 Position",
            value=str(channel.position),
            inline=True
        )

        if channel.category:
            embed.add_field(
                name="📁 Category",
                value=channel.category.name,
                inline=True
            )

        embed.add_field(
            name="👮 Moderator",
            value=moderator,
            inline=True
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=True
        )

        embed.set_footer(text="Xtreme Logging")

        await log_channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        config = get_guild_logging(channel.guild.id)

        if not config or not config.get("enabled"):
            return

        log_channel = channel.guild.get_channel(config.get("mod"))
        if log_channel is None:
            return

        moderator = "Unknown"
        reason = "No reason provided"

        try:
            async for entry in channel.guild.audit_logs(
                limit=5,
                action=discord.AuditLogAction.channel_delete
            ):
                if (
                    entry.target.id == channel.id
                    and (discord.utils.utcnow() - entry.created_at).total_seconds() <= 10
                ):
                    moderator = entry.user.mention
                    reason = entry.reason or "No reason provided"
                    break
        except discord.Forbidden:
            pass

        if isinstance(channel, discord.TextChannel):
            channel_type = "💬 Text Channel"
        elif isinstance(channel, discord.VoiceChannel):
            channel_type = "🔊 Voice Channel"
        elif isinstance(channel, discord.CategoryChannel):
            channel_type = "📁 Category"
        elif isinstance(channel, discord.StageChannel):
            channel_type = "🎙️ Stage Channel"
        elif hasattr(discord, "ForumChannel") and isinstance(channel, discord.ForumChannel):
            channel_type = "🧵 Forum Channel"
        else:
            channel_type = str(channel.type).title()

        embed = discord.Embed(
            title="🗑️ Channel Deleted",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )

        if channel.guild.icon:
            embed.set_thumbnail(url=channel.guild.icon.url)

        embed.add_field(
            name="📂 Channel",
            value=f"`{channel.name}`\n`{channel.id}`",
            inline=False
        )

        embed.add_field(
            name="📌 Type",
            value=channel_type,
            inline=True
        )

        embed.add_field(
            name="📍 Position",
            value=str(channel.position),
            inline=True
        )

        embed.add_field(
            name="👮 Moderator",
            value=moderator,
            inline=True
        )

        if channel.category:
            embed.add_field(
                name="📁 Category",
                value=channel.category.name,
                inline=True
            )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )

        embed.set_footer(text="Xtreme Logging")

        await log_channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        config = get_guild_logging(after.guild.id)

        if not config or not config.get("enabled"):
            return

        log_channel = after.guild.get_channel(config.get("mod"))
        if log_channel is None:
            return

        moderator = "Unknown"
        reason = "No reason provided"

        try:
            async for entry in after.guild.audit_logs(
                limit=5,
                action=discord.AuditLogAction.channel_update
            ):
                if (
                    entry.target.id == after.id
                    and (discord.utils.utcnow() - entry.created_at).total_seconds() <= 10
                ):
                    moderator = entry.user.mention
                    reason = entry.reason or "No reason provided"
                    break
        except discord.Forbidden:
            pass

        changes = []

        if before.name != after.name:
            changes.append(
                f"**Name**\n`{before.name}` → `{after.name}`"
            )

        if hasattr(before, "topic") and before.topic != after.topic:
            changes.append(
                f"**Topic**\n`{before.topic or 'None'}` → `{after.topic or 'None'}`"
            )

        if hasattr(before, "slowmode_delay") and before.slowmode_delay != after.slowmode_delay:
            changes.append(
                f"**Slowmode**\n`{before.slowmode_delay}s` → `{after.slowmode_delay}s`"
            )

        if hasattr(before, "nsfw") and before.nsfw != after.nsfw:
            changes.append(
                f"**NSFW**\n`{before.nsfw}` → `{after.nsfw}`"
            )

        if before.category != after.category:
            changes.append(
                f"**Category**\n`{before.category}` → `{after.category}`"
            )

        if before.position != after.position:
            changes.append(
                f"**Position**\n`{before.position}` → `{after.position}`"
            )

        if hasattr(before, "bitrate") and before.bitrate != after.bitrate:
            changes.append(
                f"**Bitrate**\n`{before.bitrate}` → `{after.bitrate}`"
            )

        if hasattr(before, "user_limit") and before.user_limit != after.user_limit:
            changes.append(
                f"**User Limit**\n`{before.user_limit}` → `{after.user_limit}`"
            )

        if before.overwrites != after.overwrites:
            changes.append("**Permission Overwrites Updated**")

        if not changes:
            return

        embed = discord.Embed(
            title="📝 Channel Updated",
            color=discord.Color.blurple(),
            timestamp=discord.utils.utcnow()
        )

        if after.guild.icon:
            embed.set_thumbnail(url=after.guild.icon.url)

        embed.add_field(
            name="📂 Channel",
            value=f"{after.mention if hasattr(after, 'mention') else after.name}\n`{after.id}`",
            inline=False
        )

        embed.add_field(
            name="🔄 Changes",
            value="\n\n".join(changes),
            inline=False
        )

        embed.add_field(
            name="👮 Moderator",
            value=moderator,
            inline=True
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=True
        )

        embed.set_footer(text="Xtreme Logging")

        await log_channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        config = get_guild_logging(after.id)

        if not config or not config.get("enabled"):
            return

        log_channel = after.get_channel(config.get("mod"))
        if log_channel is None:
            return

        moderator = "Unknown"
        reason = "No reason provided"

        try:
            async for entry in after.audit_logs(
                limit=5,
                action=discord.AuditLogAction.guild_update
            ):
                if (discord.utils.utcnow() - entry.created_at).total_seconds() <= 10:
                    moderator = entry.user.mention
                    reason = entry.reason or "No reason provided"
                    break
        except discord.Forbidden:
            pass

        changes = []

        if before.name != after.name:
            changes.append(
                f"**🏷 Name**\n`{before.name}` → `{after.name}`"
            )

        if before.description != after.description:
            changes.append("**📄 Description Updated**")

        if before.icon != after.icon:
            changes.append("**🖼 Server Icon Updated**")

        if before.banner != after.banner:
            changes.append("**🎨 Server Banner Updated**")

        if before.splash != after.splash:
            changes.append("**🌄 Invite Splash Updated**")

        if before.verification_level != after.verification_level:
            changes.append(
                f"**🛡 Verification Level**\n`{before.verification_level}` → `{after.verification_level}`"
            )

        if before.default_notifications != after.default_notifications:
            changes.append(
                f"**📢 Default Notifications**\n`{before.default_notifications}` → `{after.default_notifications}`"
            )

        if before.afk_timeout != after.afk_timeout:
            changes.append(
                f"**⏱ AFK Timeout**\n`{before.afk_timeout}` → `{after.afk_timeout}`"
            )

        if before.afk_channel != after.afk_channel:
            changes.append(
                f"**📺 AFK Channel**\n`{before.afk_channel}` → `{after.afk_channel}`"
            )

        if before.system_channel != after.system_channel:
            changes.append(
                f"**💬 System Channel**\n`{before.system_channel}` → `{after.system_channel}`"
            )

        if before.rules_channel != after.rules_channel:
            changes.append("**📜 Rules Channel Updated**")

        if before.public_updates_channel != after.public_updates_channel:
            changes.append("**📢 Community Updates Channel Updated**")

        if not changes:
            return

        embed = discord.Embed(
            title="🌐 Server Updated",
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow()
        )

        if after.icon:
            embed.set_thumbnail(url=after.icon.url)

        embed.add_field(
            name="🏠 Server",
            value=f"**{after.name}**\n`{after.id}`",
            inline=False
        )

        embed.add_field(
            name="🔄 Changes",
            value="\n\n".join(changes),
            inline=False
        )

        embed.add_field(
            name="👮 Moderator",
            value=moderator,
            inline=True
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=True
        )

        embed.set_footer(text="Xtreme Logging")

        await log_channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        config = get_guild_logging(guild.id)

        if not config or not config.get("enabled"):
            return

        log_channel = guild.get_channel(config.get("mod"))
        if log_channel is None:
            return

        moderator = "Unknown"
        reason = "No reason provided"

        before_ids = {e.id: e for e in before}
        after_ids = {e.id: e for e in after}

        added = set(after_ids) - set(before_ids)
        removed = set(before_ids) - set(after_ids)

        try:
            action = None

            if added:
                action = discord.AuditLogAction.emoji_create
            elif removed:
                action = discord.AuditLogAction.emoji_delete
            else:
                action = discord.AuditLogAction.emoji_update

            async for entry in guild.audit_logs(limit=5, action=action):
                moderator = entry.user.mention
                reason = entry.reason or "No reason provided"
                break

        except discord.Forbidden:
            pass

        embed = discord.Embed(
            color=discord.Color.blurple(),
            timestamp=discord.utils.utcnow()
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        if added:
            emoji = after_ids[added.pop()]
            embed.title = "😀 Emoji Created"
            embed.color = discord.Color.green()

            embed.add_field(
                name="Emoji",
                value=f"{emoji} `{emoji.name}`",
                inline=False
            )

        elif removed:
            emoji = before_ids[removed.pop()]
            embed.title = "🗑️ Emoji Deleted"
            embed.color = discord.Color.red()

            embed.add_field(
                name="Emoji",
                value=f"`{emoji.name}`",
                inline=False
            )

        else:
            for emoji_id, old in before_ids.items():
                if emoji_id in after_ids:
                    new = after_ids[emoji_id]

                    if old.name != new.name:
                        embed.title = "✏️ Emoji Renamed"

                        embed.add_field(
                            name="Before",
                            value=old.name,
                            inline=True
                        )

                        embed.add_field(
                            name="After",
                            value=new.name,
                            inline=True
                        )

                        break
            else:
                return

        embed.add_field(
            name="👮 Moderator",
            value=moderator,
            inline=True
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=True
        )

        embed.set_footer(text="Xtreme Logging")

        await log_channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_guild_stickers_update(self, guild, before, after):
        config = get_guild_logging(guild.id)

        if not config or not config.get("enabled"):
            return

        log_channel = guild.get_channel(config.get("mod"))
        if log_channel is None:
            return

        moderator = "Unknown"
        reason = "No reason provided"

        before_ids = {s.id: s for s in before}
        after_ids = {s.id: s for s in after}

        added = set(after_ids) - set(before_ids)
        removed = set(before_ids) - set(after_ids)

        try:
            if added:
                action = discord.AuditLogAction.sticker_create
            elif removed:
                action = discord.AuditLogAction.sticker_delete
            else:
                action = discord.AuditLogAction.sticker_update

            async for entry in guild.audit_logs(limit=5, action=action):
                moderator = entry.user.mention
                reason = entry.reason or "No reason provided"
                break

        except discord.Forbidden:
            pass

        embed = discord.Embed(
            color=discord.Color.blurple(),
            timestamp=discord.utils.utcnow()
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        if added:
            sticker = after_ids[added.pop()]

            embed.title = "🏷️ Sticker Created"
            embed.color = discord.Color.green()

            embed.add_field(
                name="Sticker",
                value=f"**{sticker.name}**\n`{sticker.id}`",
                inline=False
            )

        elif removed:
            sticker = before_ids[removed.pop()]

            embed.title = "🗑️ Sticker Deleted"
            embed.color = discord.Color.red()

            embed.add_field(
                name="Sticker",
                value=f"**{sticker.name}**\n`{sticker.id}`",
                inline=False
            )

        else:
            for sticker_id, old in before_ids.items():
                if sticker_id in after_ids:
                    new = after_ids[sticker_id]

                    if (
                        old.name != new.name
                        or old.description != new.description
                        or old.emoji != new.emoji
                    ):

                        embed.title = "✏️ Sticker Updated"

                        embed.add_field(
                            name="Sticker",
                            value=f"`{new.name}`",
                            inline=False
                        )

                        if old.name != new.name:
                            embed.add_field(
                                name="Name",
                                value=f"`{old.name}` → `{new.name}`",
                                inline=False
                            )

                        if old.description != new.description:
                            embed.add_field(
                                name="Description",
                                value=f"`{old.description}` → `{new.description}`",
                                inline=False
                            )

                        if old.emoji != new.emoji:
                            embed.add_field(
                                name="Emoji",
                                value=f"`{old.emoji}` → `{new.emoji}`",
                                inline=False
                            )

                        break
            else:
                return

        embed.add_field(
            name="👮 Moderator",
            value=moderator,
            inline=True
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=True
        )

        embed.set_footer(text="Xtreme Logging")

        await log_channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        config = get_guild_logging(invite.guild.id)

        if not config or not config.get("enabled"):
            return

        log_channel = invite.guild.get_channel(config.get("mod"))
        if log_channel is None:
            return

        embed = discord.Embed(
            title="➕ Invite Created",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )

        if invite.guild.icon:
            embed.set_thumbnail(url=invite.guild.icon.url)

        embed.add_field(
            name="🔗 Invite",
            value=f"`{invite.code}`",
            inline=False
        )

        embed.add_field(
            name="👤 Inviter",
            value=invite.inviter.mention if invite.inviter else "Unknown",
            inline=True
        )

        embed.add_field(
            name="📍 Channel",
            value=invite.channel.mention if invite.channel else "Unknown",
            inline=True
        )

        embed.add_field(
            name="👥 Max Uses",
            value=str(invite.max_uses or "Unlimited"),
            inline=True
        )

        embed.add_field(
            name="📊 Current Uses",
            value=str(invite.uses),
            inline=True
        )

        embed.add_field(
            name="⏳ Expires",
            value=discord.utils.format_dt(invite.expires_at, "F") if invite.expires_at else "Never",
            inline=False
        )

        embed.set_footer(text="Xtreme Logging")

        await log_channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_webhooks_update(self, channel):
        config = get_guild_logging(channel.guild.id)

        if not config or not config.get("enabled"):
            return

        log_channel = channel.guild.get_channel(config.get("mod"))
        if log_channel is None:
            return

        action = None
        moderator = "Unknown"
        reason = "No reason provided"
        webhook_name = "Unknown"

        actions = [
            discord.AuditLogAction.webhook_create,
            discord.AuditLogAction.webhook_update,
            discord.AuditLogAction.webhook_delete
        ]

        try:
            for audit_action in actions:
                async for entry in channel.guild.audit_logs(
                    limit=1,
                    action=audit_action
                ):
                    if (
                        (discord.utils.utcnow() - entry.created_at).total_seconds() <= 10
                    ):
                        action = audit_action
                        moderator = entry.user.mention
                        reason = entry.reason or "No reason provided"
                        webhook_name = getattr(entry.target, "name", "Unknown")
                        break

                if action:
                    break

        except discord.Forbidden:
            return

        if not action:
            return

        titles = {
            discord.AuditLogAction.webhook_create: ("🪝 Webhook Created", discord.Color.green()),
            discord.AuditLogAction.webhook_update: ("✏️ Webhook Updated", discord.Color.orange()),
            discord.AuditLogAction.webhook_delete: ("🗑️ Webhook Deleted", discord.Color.red())
        }

        title, color = titles[action]

        embed = discord.Embed(
            title=title,
            color=color,
            timestamp=discord.utils.utcnow()
        )

        if channel.guild.icon:
            embed.set_thumbnail(url=channel.guild.icon.url)

        embed.add_field(
            name="🪝 Webhook",
            value=webhook_name,
            inline=False
        )

        embed.add_field(
            name="📍 Channel",
            value=channel.mention,
            inline=True
        )

        embed.add_field(
            name="👮 Moderator",
            value=moderator,
            inline=True
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )

        embed.set_footer(text="Xtreme Logging")

        await log_channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_thread_create(self, thread):
        config = get_guild_logging(thread.guild.id)

        if not config or not config.get("enabled"):
            return

        log_channel = thread.guild.get_channel(config.get("mod"))
        if log_channel is None:
            return

        embed = discord.Embed(
            title="🧵 Thread Created",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )

        if thread.guild.icon:
            embed.set_thumbnail(url=thread.guild.icon.url)

        embed.add_field(
            name="🧵 Thread",
            value=f"{thread.mention}\n`{thread.id}`",
            inline=False
        )

        embed.add_field(
            name="📍 Parent Channel",
            value=thread.parent.mention,
            inline=True
        )

        embed.add_field(
            name="👤 Owner",
            value=f"<@{thread.owner_id}>" if thread.owner_id else "Unknown",
            inline=True
        )

        embed.add_field(
            name="📦 Archived",
            value=str(thread.archived),
            inline=True
        )

        embed.add_field(
            name="🔒 Locked",
            value=str(thread.locked),
            inline=True
        )

        embed.set_footer(text="Xtreme Logging")

        await log_channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_scheduled_event_create(self, event):
        config = get_guild_logging(event.guild.id)

        if not config or not config.get("enabled"):
            return

        log_channel = event.guild.get_channel(config.get("mod"))
        if log_channel is None:
            return

        embed = discord.Embed(
            title="📅 Scheduled Event Created",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )

        if event.guild.icon:
            embed.set_thumbnail(url=event.guild.icon.url)

        embed.add_field(name="📌 Name", value=event.name, inline=False)
        embed.add_field(name="🆔 Event ID", value=f"`{event.id}`", inline=False)
        embed.add_field(name="🕒 Starts", value=discord.utils.format_dt(event.start_time, "F"), inline=False)

        if event.end_time:
            embed.add_field(
                name="🕒 Ends",
                value=discord.utils.format_dt(event.end_time, "F"),
                inline=False
            )

        embed.set_footer(text="Xtreme Logging")

        await log_channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_scheduled_event_update(self, before, after):
        config = get_guild_logging(after.guild.id)

        if not config or not config.get("enabled"):
            return

        log_channel = after.guild.get_channel(config.get("mod"))
        if log_channel is None:
            return

        changes = []

        if before.name != after.name:
            changes.append(f"**Name**\n`{before.name}` → `{after.name}`")

        if before.description != after.description:
            changes.append("**Description Updated**")

        if before.start_time != after.start_time:
            changes.append("**Start Time Updated**")

        if before.end_time != after.end_time:
            changes.append("**End Time Updated**")

        if before.status != after.status:
            changes.append(f"**Status**\n`{before.status}` → `{after.status}`")

        if before.location != after.location:
            changes.append("**Location Updated**")

        if not changes:
            return

        embed = discord.Embed(
            title="✏️ Scheduled Event Updated",
            color=discord.Color.blurple(),
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(
            name="📌 Event",
            value=after.name,
            inline=False
        )

        embed.add_field(
            name="🔄 Changes",
            value="\n\n".join(changes),
            inline=False
        )

        embed.set_footer(text="Xtreme Logging")

        await log_channel.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        if not messages:
            return

        guild = messages[0].guild

        if guild is None:
            return

        config = get_guild_logging(guild.id)

        if not config or not config.get("enabled"):
            return

        log_channel = guild.get_channel(config.get("message"))
        if log_channel is None:
            return

        deleted = len(messages)

        moderator = "Unknown"
        reason = "No reason provided"

        try:
            async for entry in guild.audit_logs(
                limit=5,
                action=discord.AuditLogAction.message_bulk_delete
            ):
                if (
                    discord.utils.utcnow() - entry.created_at
                ).total_seconds() <= 10:
                    moderator = entry.user.mention
                    reason = entry.reason or "No reason provided"
                    break
        except discord.Forbidden:
            pass

        channel = messages[0].channel

        embed = discord.Embed(
            title="🗑️ Bulk Message Delete",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(
            name="📍 Channel",
            value=channel.mention,
            inline=True
        )

        embed.add_field(
            name="💬 Messages Deleted",
            value=str(deleted),
            inline=True
        )

        embed.add_field(
            name="👮 Moderator",
            value=moderator,
            inline=False
        )

        embed.add_field(
            name="📝 Reason",
            value=reason,
            inline=False
        )

        embed.set_footer(text="Xtreme Logging")

        await log_channel.send(embed=embed)
        
async def setup(bot):
    await bot.add_cog(Logging(bot))