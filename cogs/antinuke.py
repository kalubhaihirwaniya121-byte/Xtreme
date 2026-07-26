import discord

from discord.ext import commands

from collections import defaultdict

import time

from utils.emojis import Emojis

class AntiNuke(commands.Cog):

    """AntiNuke system"""

    def __init__(self, bot: commands.Bot):

        self.bot = bot

        # guild_id: settings

        self.settings = {}

        # guild_id: {user_id: count}

        self.action_count = defaultdict(lambda: defaultdict(int))

        self.last_action = defaultdict(lambda: defaultdict(float))

    # --------------------------------------------------

    # HELPERS

    # --------------------------------------------------

    def embed(self, title, desc, color=0x2f3136):

        e = discord.Embed(title=title, description=desc, color=color)

        e.set_footer(text="Thanks for using Xtreme")

        return e

    def get_guild(self, guild_id: int):

        if guild_id not in self.settings:

            self.settings[guild_id] = {

                "enabled": False,

                "log_channel": None,

                "whitelist_users": set(),

                "whitelist_roles": set(),

                "threshold": 3,   # actions

                "timeframe": 10,  # seconds

            }

        return self.settings[guild_id]

    def is_whitelisted(self, member: discord.Member, data: dict):

        if member.id in data["whitelist_users"]:

            return True

        if any(r.id in data["whitelist_roles"] for r in member.roles):

            return True

        return False

    async def punish(self, guild: discord.Guild, member: discord.Member, reason: str):

        try:

            await guild.ban(member, reason=reason)

        except discord.Forbidden:

            pass

    async def log(self, guild: discord.Guild, data: dict, message: str):

        if not data["log_channel"]:

            return

        channel = guild.get_channel(data["log_channel"])

        if channel:

            await channel.send(embed=self.embed(

                "AntiNuke Alert",

                message,

                0xe74c3c

            ))

    # --------------------------------------------------

    # COMMAND

    # --------------------------------------------------

    @commands.hybrid_command(name="antinuke")

    @commands.has_permissions(administrator=True)

    async def antinuke(self, ctx: commands.Context, option: str = None, channel: discord.TextChannel = None):

        data = self.get_guild(ctx.guild.id)

        if option is None:

            await ctx.send(embed=self.embed(

                "AntiNuke Help",

                "Use:\n"

                "`.antinuke on/off`\n"

                "`.antinuke status`\n"

                "`.antinuke log #channel`"

            ))

            return

        if option.lower() in ("on", "off"):

            data["enabled"] = option.lower() == "on"

            await ctx.send(embed=self.embed(

                "AntiNuke",

                f"AntiNuke is now **{option.upper()}**."

            ))

            return

        if option.lower() == "status":

            await ctx.send(embed=self.embed(

                "AntiNuke Status",

                f"Enabled: **{data['enabled']}**\n"

                f"Threshold: **{data['threshold']} actions / {data['timeframe']}s**"

            ))

            return

        if option.lower() == "log" and channel:

            data["log_channel"] = channel.id

            await ctx.send(embed=self.embed(

                "Log Channel Set",

                f"AntiNuke logs will be sent in {channel.mention}"

            ))

            return

        await ctx.send(embed=self.embed(

            "Invalid Usage",

            "Check `.antinuke` help.",

            0xe74c3c

        ))

    # --------------------------------------------------

    # WHITELIST

    # --------------------------------------------------

    @commands.hybrid_command(name="antinukewhitelist")

    @commands.has_permissions(administrator=True)

    async def antinukewhitelist(self, ctx, action: str, target):

        data = self.get_guild(ctx.guild.id)

        if action == "add":

            if isinstance(target, discord.Member):

                data["whitelist_users"].add(target.id)

                name = target.mention

            else:

                data["whitelist_roles"].add(target.id)

                name = target.mention

            await ctx.send(embed=self.embed(

                "Whitelist Added",

                name

            ))

        elif action == "remove":

            if isinstance(target, discord.Member):

                data["whitelist_users"].discard(target.id)

                name = target.mention

            else:

                data["whitelist_roles"].discard(target.id)

                name = target.mention

            await ctx.send(embed=self.embed(

                "Whitelist Removed",

                name

            ))

        elif action == "list":

            users = [f"<@{u}>" for u in data["whitelist_users"]]

            roles = [f"<@&{r}>" for r in data["whitelist_roles"]]

            desc = "**Users:**\n" + (", ".join(users) or "None")

            desc += "\n\n**Roles:**\n" + (", ".join(roles) or "None")

            await ctx.send(embed=self.embed(

                "AntiNuke Whitelist",

                desc

            ))

        else:

            await ctx.send(embed=self.embed(

                "Invalid Usage",

                "Use `.antinukewhitelist add/remove/list @user/@role`",

                0xe74c3c

            ))

    # --------------------------------------------------

    # LISTENERS

    # --------------------------------------------------

    @commands.Cog.listener()

    async def on_guild_channel_delete(self, channel):

        guild = channel.guild

        data = self.settings.get(guild.id)

        if not data or not data["enabled"]:

            return

        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):

            member = entry.user

            if not isinstance(member, discord.Member):

                return

            if self.is_whitelisted(member, data):

                return

            now = time.time()

            last = self.last_action[guild.id][member.id]

            if now - last > data["timeframe"]:

                self.action_count[guild.id][member.id] = 0

            self.last_action[guild.id][member.id] = now

            self.action_count[guild.id][member.id] += 1

            if self.action_count[guild.id][member.id] >= data["threshold"]:

                await self.punish(guild, member, "AntiNuke: Channel delete spam")

                await self.log(

                    guild,

                    data,

                    f"{member.mention} triggered AntiNuke by deleting channels."

                )

    @commands.Cog.listener()

    async def on_guild_role_delete(self, role):

        guild = role.guild

        data = self.settings.get(guild.id)

        if not data or not data["enabled"]:

            return

        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):

            member = entry.user

            if not isinstance(member, discord.Member):

                return

            if self.is_whitelisted(member, data):

                return

            self.action_count[guild.id][member.id] += 1

            if self.action_count[guild.id][member.id] >= data["threshold"]:

                await self.punish(guild, member, "AntiNuke: Role delete spam")

                await self.log(

                    guild,

                    data,

                    f"{member.mention} triggered AntiNuke by deleting roles."

                )

async def setup(bot: commands.Bot):

    await bot.add_cog(AntiNuke(bot))