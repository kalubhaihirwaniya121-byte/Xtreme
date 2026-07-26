import discord
from discord.ext import commands
from datetime import timedelta

try:
    from utils.automod_utils import is_bypass
    from utils.automod_utils import (
        get_guild_config,
        update_guild_config,
        parse_duration
    )
    from utils.badwords_utils import (
        add_badword,
        remove_badword,
        get_badwords,
        clear_badwords
    )
except ModuleNotFoundError:
    from automod_utils import is_bypass
    from automod_utils import (
        get_guild_config,
        update_guild_config,
        parse_duration
    )
    from badwords_utils import (
        add_badword,
        remove_badword,
        get_badwords,
        clear_badwords
    )

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        import collections
        self.spam_cooldowns = collections.defaultdict(list)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.content != after.content:
            await self.on_message(after)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if not message.guild:
            return

        config = get_guild_config(message.guild.id)

        if not config["enabled"]:
            return

        if is_bypass(message.author, config):
            return

        import re
        import unicodedata
        import time

        normalized_content = unicodedata.normalize("NFKD", message.content).lower()
        clean_content = "".join(c for c in normalized_content if c.isprintable() or c.isspace())

        # Check spam
        is_spam = False
        if config.get("anti_spam"):
            now = time.time()
            user_id = message.author.id
            self.spam_cooldowns[user_id] = [t for t in self.spam_cooldowns[user_id] if now - t < 5]
            self.spam_cooldowns[user_id].append(now)
            if len(self.spam_cooldowns[user_id]) > 5:
                is_spam = True

        # Check mass mentions
        is_mass_mention = False
        max_mentions = config.get("max_mentions", 5)
        if max_mentions > 0 and len(message.mentions) > max_mentions:
            is_mass_mention = True

        # Check invites
        is_invite = False
        if config.get("anti_invites"):
            invite_regex = r"(discord\.gg/|discord\.com/invite/|discordapp\.com/invite/)[a-zA-Z0-9-]+"
            if re.search(invite_regex, clean_content):
                is_invite = True

        # Check links
        is_link = False
        if config.get("anti_links") and not is_invite:
            link_regex = r"(https?://[^\s]+|www\.[^\s]+)"
            if re.search(link_regex, clean_content):
                is_link = True

        matched_badword = False
        badwords = get_badwords(message.guild.id)
        for word in badwords:
            if word.lower() in clean_content:
                matched_badword = True
                break

        violation = None
        reason = ""
        warn_msg = ""

        if is_spam:
            violation = "spam"
            reason = "AutoMod: Spamming"
            warn_msg = f"⚠️ {message.author.mention}, please stop spamming."
        elif is_mass_mention:
            violation = "mentions"
            reason = "AutoMod: Mass Mentions"
            warn_msg = f"⚠️ {message.author.mention}, too many mentions."
        elif is_invite:
            violation = "invite"
            reason = "AutoMod: Invite link"
            warn_msg = f"⚠️ {message.author.mention}, invite links are not allowed here."
        elif is_link:
            violation = "link"
            reason = "AutoMod: Link posting"
            warn_msg = f"⚠️ {message.author.mention}, links are not allowed here."
        elif matched_badword:
            violation = "badword"
            reason = "AutoMod: Bad words"
            warn_msg = f"⚠️ {message.author.mention}, watch your language."

        if violation:
            try:
                await message.delete()
            except discord.HTTPException:
                pass

            punishment = config["punishment"]["type"]

            if punishment == "warn":
                try:
                    await message.channel.send(
                        warn_msg,
                        delete_after=5
                    )
                except discord.HTTPException:
                    pass

            elif punishment == "kick":
                try:
                    await message.author.kick(
                        reason=reason
                    )

                    await message.channel.send(
                        f"👢 {message.author.mention} was kicked by AutoMod."
                    )

                except discord.HTTPException:
                    pass

            elif punishment == "mute":
                try:
                    seconds = config["punishment"]["duration"]

                    await message.author.timeout(
                        timedelta(seconds=seconds),
                        reason=reason
                    )

                    await message.channel.send(
                        f"🔇 {message.author.mention} has been timed out."
                    )

                except discord.HTTPException:
                    pass

    @commands.group(
        name="automod",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def automod(self, ctx):
        """AutoMod Settings"""

        config = get_guild_config(ctx.guild.id)

        status = "🟢 Enabled" if config["enabled"] else "🔴 Disabled"

        punishment = config["punishment"]["type"].title()

        if punishment == "Mute":
            punishment = (
                f"Mute "
                f"({config['punishment']['duration']}s)"
            )

        bypass = len(config["bypass_roles"])

        embed = discord.Embed(
            title="🛡️ Xtreme AutoMod",
            color=discord.Color.blurple()
        )

        anti_links = "🟢 Enabled" if config.get("anti_links") else "🔴 Disabled"
        anti_invites = "🟢 Enabled" if config.get("anti_invites") else "🔴 Disabled"
        anti_spam = "🟢 Enabled" if config.get("anti_spam") else "🔴 Disabled"
        max_mentions = config.get("max_mentions", 5)
        mentions_str = f"🟢 Limit: {max_mentions}" if max_mentions > 0 else "🔴 Disabled"

        embed.add_field(
            name="Status",
            value=status,
            inline=False
        )

        embed.add_field(
            name="Punishment",
            value=punishment,
            inline=True
        )

        embed.add_field(
            name="Bypass Roles",
            value=str(bypass),
            inline=True
        )

        embed.add_field(
            name="Link Protection",
            value=anti_links,
            inline=True
        )

        embed.add_field(
            name="Invite Protection",
            value=anti_invites,
            inline=True
        )

        embed.add_field(
            name="Anti-Spam",
            value=anti_spam,
            inline=True
        )

        embed.add_field(
            name="Max Mentions",
            value=mentions_str,
            inline=True
        )

        embed.set_footer(
            text="Xtreme • AutoMod"
        )

        await ctx.send(embed=embed)
        
    @automod.command(name="enable")
    @commands.has_permissions(manage_guild=True)
    async def enable(self, ctx):
        """Enable AutoMod"""

        config = get_guild_config(ctx.guild.id)

        if config["enabled"]:
            return await ctx.send(
                "⚠️ AutoMod is already enabled."
            )

        config["enabled"] = True
        update_guild_config(
            ctx.guild.id,
            config
        )

        await ctx.send(
            "✅ AutoMod has been enabled."
        )

    @automod.command(name="disable")
    @commands.has_permissions(manage_guild=True)
    async def disable(self, ctx):
        """Disable AutoMod"""

        config = get_guild_config(ctx.guild.id)

        if not config["enabled"]:
            return await ctx.send(
                "⚠️ AutoMod is already disabled."
            )

        config["enabled"] = False
        update_guild_config(
            ctx.guild.id,
            config
        )

        await ctx.send(
            "✅ AutoMod has been disabled."
        )
        
    @automod.command(name="punishment")
    @commands.has_permissions(manage_guild=True)
    async def punishment(self, ctx, action: str = None, duration: str = None):
        """Set AutoMod punishment."""

        if action is None:
            return await ctx.send(
                "❌ Usage: `.automod punishment <warn|kick|mute> [duration]`"
            )

        action = action.lower()

        if action not in ("warn", "kick", "mute"):
            return await ctx.send(
                "❌ Invalid punishment. Choose: `warn`, `kick`, or `mute`."
            )

        config = get_guild_config(ctx.guild.id)

        if action == "mute":
            if duration is None:
                return await ctx.send(
                    "❌ Please provide a duration.\nExample: `.automod punishment mute 30m`"
                )

            td = parse_duration(duration)

            if td is None:
                return await ctx.send(
                    "❌ Invalid duration.\nExamples: `30s`, `10m`, `2h`, `1d`"
                )

            config["punishment"]["type"] = "mute"
            config["punishment"]["duration"] = int(td.total_seconds())

            update_guild_config(ctx.guild.id, config)

            return await ctx.send(
                f"✅ AutoMod punishment set to **Mute ({duration})**."
            )

        config["punishment"]["type"] = action
        update_guild_config(ctx.guild.id, config)

        await ctx.send(
            f"✅ AutoMod punishment set to **{action.title()}**."
        )

    @automod.command(name="links")
    @commands.has_permissions(manage_guild=True)
    async def links(self, ctx, option: str = None):
        """Enable or disable Link protection."""
        if option is None:
            return await ctx.send(
                "❌ Usage: `.automod links <enable|disable>`"
            )

        option = option.lower()
        if option not in ("enable", "disable"):
            return await ctx.send(
                "❌ Invalid option. Choose `enable` or `disable`."
            )

        config = get_guild_config(ctx.guild.id)
        config["anti_links"] = (option == "enable")
        update_guild_config(ctx.guild.id, config)

        await ctx.send(
            f"✅ Link protection has been **{option}d**."
        )

    @automod.command(name="invites")
    @commands.has_permissions(manage_guild=True)
    async def invites(self, ctx, option: str = None):
        """Enable or disable Invite protection."""
        if option is None:
            return await ctx.send(
                "❌ Usage: `.automod invites <enable|disable>`"
            )

        option = option.lower()
        if option not in ("enable", "disable"):
            return await ctx.send(
                "❌ Invalid option. Choose `enable` or `disable`."
            )

        config = get_guild_config(ctx.guild.id)
        config["anti_invites"] = (option == "enable")
        update_guild_config(ctx.guild.id, config)

        await ctx.send(
            f"✅ Invite protection has been **{option}d**."
        )

    @automod.command(name="spam")
    @commands.has_permissions(manage_guild=True)
    async def spam(self, ctx, option: str = None):
        """Enable or disable Anti-Spam protection."""
        if option is None:
            return await ctx.send(
                "❌ Usage: `.automod spam <enable|disable>`"
            )

        option = option.lower()
        if option not in ("enable", "disable"):
            return await ctx.send(
                "❌ Invalid option. Choose `enable` or `disable`."
            )

        config = get_guild_config(ctx.guild.id)
        config["anti_spam"] = (option == "enable")
        update_guild_config(ctx.guild.id, config)

        await ctx.send(
            f"✅ Anti-Spam protection has been **{option}d**."
        )

    @automod.command(name="maxmentions")
    @commands.has_permissions(manage_guild=True)
    async def maxmentions(self, ctx, limit: int = None):
        """Set the maximum number of allowed mentions (0 to disable)."""
        if limit is None:
            return await ctx.send(
                "❌ Usage: `.automod maxmentions <number>`"
            )

        if limit < 0:
            return await ctx.send(
                "❌ Limit must be a non-negative number."
            )

        config = get_guild_config(ctx.guild.id)
        config["max_mentions"] = limit
        update_guild_config(ctx.guild.id, config)

        status_msg = f"set to **{limit}**" if limit > 0 else "**disabled**"
        await ctx.send(
            f"✅ Mass Mentions protection limit has been {status_msg}."
        )
        
    @automod.group(name="bypass", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def bypass(self, ctx):
        await ctx.send(
            "❌ Usage:\n"
            "`.automod bypass add @Role`\n"
            "`.automod bypass remove @Role`\n"
            "`.automod bypass list`"
        )

    @bypass.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def bypass_add(self, ctx, role: discord.Role):
        config = get_guild_config(ctx.guild.id)

        if role.id in config["bypass_roles"]:
            return await ctx.send(
                "⚠️ That role is already bypassed."
            )

        config["bypass_roles"].append(role.id)
        update_guild_config(ctx.guild.id, config)

        await ctx.send(
            f"✅ {role.mention} has been added to AutoMod bypass."
        )

    @bypass.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def bypass_remove(self, ctx, role: discord.Role):
        config = get_guild_config(ctx.guild.id)

        if role.id not in config["bypass_roles"]:
            return await ctx.send(
                "⚠️ That role is not in bypass."
            )

        config["bypass_roles"].remove(role.id)
        update_guild_config(ctx.guild.id, config)

        await ctx.send(
            f"✅ {role.mention} has been removed from AutoMod bypass."
        )

    @bypass.command(name="list")
    @commands.has_permissions(manage_guild=True)
    async def bypass_list(self, ctx):
        config = get_guild_config(ctx.guild.id)

        if not config["bypass_roles"]:
            return await ctx.send(
                "❌ No bypass roles configured."
            )

        roles = []

        for role_id in config["bypass_roles"]:
            role = ctx.guild.get_role(role_id)
            if role:
                roles.append(role.mention)

        embed = discord.Embed(
            title="🛡️ AutoMod Bypass Roles",
            description="\n".join(roles),
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)
        
    @commands.group(name="badwords", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def badwords(self, ctx):
        await ctx.send(
            "❌ Usage:\n"
            "`.badwords add <word>`\n"
            "`.badwords remove <word>`\n"
            "`.badwords list`\n"
            "`.badwords clear`"
        )

    @badwords.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def badwords_add(self, ctx, *, word: str):
        if add_badword(ctx.guild.id, word):
            await ctx.send(
                f"✅ Added `{word.lower()}` to the bad words list."
            )
        else:
            await ctx.send(
                "⚠️ That word already exists."
            )

    @badwords.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def badwords_remove(self, ctx, *, word: str):
        if remove_badword(ctx.guild.id, word):
            await ctx.send(
                f"✅ Removed `{word.lower()}` from the bad words list."
            )
        else:
            await ctx.send(
                "⚠️ That word was not found."
            )

    @badwords.command(name="list")
    @commands.has_permissions(manage_guild=True)
    async def badwords_list(self, ctx):
        words = get_badwords(ctx.guild.id)

        if not words:
            return await ctx.send(
                "❌ No bad words have been added."
            )

        embed = discord.Embed(
            title="🚫 Bad Words",
            description="\n".join(
                f"• `{word}`" for word in words
            ),
            color=discord.Color.red()
        )

        embed.set_footer(text=f"Total: {len(words)}")

        await ctx.send(embed=embed)

    @badwords.command(name="clear")
    @commands.has_permissions(manage_guild=True)
    async def badwords_clear(self, ctx):
        clear_badwords(ctx.guild.id)

        await ctx.send(
            "✅ All bad words have been cleared."
        )
        
async def setup(bot):
    await bot.add_cog(AutoMod(bot))