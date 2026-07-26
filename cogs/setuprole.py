import os
import re
import json
import discord

from discord.ext import commands
from utils.emojis import Emojis

SETUP_ROLE_FILE = "data/setup_roles.json"


# =========================
# JSON FUNCTIONS
# =========================

def load_setup_roles():
    if not os.path.exists(SETUP_ROLE_FILE):
        return {}

    with open(SETUP_ROLE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_setup_roles(data):
    with open(SETUP_ROLE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


setup_roles = load_setup_roles()


# =========================
# COG
# =========================

class SetupRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    # =========================
    # SETUPROLE
    # =========================

    @commands.hybrid_group(
        name="setuprole",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def setuprole(self, ctx):
        embed = discord.Embed(
            title="Setup Role System",
            description=(
                "**Available Commands**\n\n"
                f"{Emojis.MARK} `.setuprole add <alias> @role`\n"
                f"{Emojis.MARK} `.setuprole remove <alias>`\n"
                f"{Emojis.MARK} `.setuprole list`\n"
                f"{Emojis.MARK} `.setuprole reset`"
            ),
            color=0x5865F2
        )

        await ctx.send(embed=embed)

    # =========================
    # SETUPROLE ADD
    # =========================

    @setuprole.command(name="add")
    @commands.has_permissions(manage_guild=True)
    async def setuprole_add(
        self,
        ctx,
        alias: str,
        role: discord.Role
    ):
        alias = alias.lower()

        if not re.fullmatch(r"[a-zA-Z0-9_]{1,20}", alias):
            embed = discord.Embed(
                title="Invalid Alias",
                description=(
                    "Alias can only contain:\n"
                    "• Letters\n"
                    "• Numbers\n"
                    "• Underscores (_)\n\n"
                    "**Maximum Length:** 20 characters."
                ),
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        guild_id = str(ctx.guild.id)

        if guild_id not in setup_roles:
            setup_roles[guild_id] = {}

        if alias in setup_roles[guild_id]:
            embed = discord.Embed(
                title="Alias Already Exists",
                description=(
                    f"The alias `{alias}` already exists.\n\n"
                    "Remove it first or choose a different alias."
                ),
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        setup_roles[guild_id][alias] = role.id
        save_setup_roles(setup_roles)

        embed = discord.Embed(
            title="Alias Created",
            description=(
                f"**Alias:** `{alias}`\n"
                f"**Role:** {role.mention}\n\n"
                f"Members can now use:\n"
                f"`.{alias} @User`"
            ),
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)
        
    # =========================
    # SETUPROLE REMOVE
    # =========================

    @setuprole.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def setuprole_remove(
        self,
        ctx,
        alias: str
    ):
        alias = alias.lower()
        guild_id = str(ctx.guild.id)

        if guild_id not in setup_roles or alias not in setup_roles[guild_id]:
            embed = discord.Embed(
                title="Alias Not Found",
                description=f"No setup role alias named `{alias}` exists.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        del setup_roles[guild_id][alias]

        if not setup_roles[guild_id]:
            del setup_roles[guild_id]

        save_setup_roles(setup_roles)

        embed = discord.Embed(
            title="Alias Removed",
            description=(
                f"Removed alias `{alias}`.\n\n"
                f"Members can no longer use:\n"
                f"`.{alias} @User`"
            ),
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)
        
    # =========================
    # SETUPROLE LIST
    # =========================

    @setuprole.command(name="list")
    @commands.has_permissions(manage_guild=True)
    async def setuprole_list(self, ctx):
        guild_id = str(ctx.guild.id)

        if guild_id not in setup_roles or not setup_roles[guild_id]:
            embed = discord.Embed(
                title="Setup Role Aliases",
                description="No setup role aliases have been configured yet.",
                color=discord.Color.orange()
            )
            return await ctx.send(embed=embed)

        lines = []

        for alias, role_id in setup_roles[guild_id].items():
            role = ctx.guild.get_role(role_id)

            if role:
                lines.append(f"`{alias}` → {role.mention}")
            else:
                lines.append(f"`{alias}` → `Deleted Role ({role_id})`")

        embed = discord.Embed(
            title="Setup Role Aliases",
            description="\n".join(lines),
            color=0x5865F2
        )

        embed.set_footer(
            text=f"Total Aliases: {len(setup_roles[guild_id])}"
        )

        await ctx.send(embed=embed)

    # =========================
    # SETUPROLE RESET
    # =========================

    @setuprole.command(name="reset")
    @commands.has_permissions(manage_guild=True)
    async def setuprole_reset(self, ctx):
        guild_id = str(ctx.guild.id)

        if guild_id not in setup_roles or not setup_roles[guild_id]:
            embed = discord.Embed(
                title="Nothing to Reset",
                description="No setup role aliases have been configured for this server.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        del setup_roles[guild_id]
        save_setup_roles(setup_roles)

        embed = discord.Embed(
            title="Setup Roles Reset",
            description="All setup role aliases have been deleted.",
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)
        
    # =========================
    # DYNAMIC SETUP ROLE
    # =========================

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        prefixes = await self.bot.get_prefix(message)

        if isinstance(prefixes, str):
            prefixes = [prefixes]

        used_prefix = None

        for p in prefixes:
            if message.content.startswith(p):
                used_prefix = p
                break

        if used_prefix is None:
            return

        content = message.content[len(used_prefix):].strip()

        if not content:
            return

        args = content.split()

        if len(args) < 2:
            return

        alias = args[0].lower()

        guild_id = str(message.guild.id)

        if guild_id not in setup_roles:
            return

        if alias not in setup_roles[guild_id]:
            return

        if not message.author.guild_permissions.manage_roles:
            return await message.channel.send(
                embed=discord.Embed(
                    title="Missing Permissions",
                    description="You need the **Manage Roles** permission to use this command.",
                    color=discord.Color.red()
                )
            )

        if not message.guild.me.guild_permissions.manage_roles:
            return await message.channel.send(
                embed=discord.Embed(
                    title="Missing Permissions",
                    description="I need the **Manage Roles** permission.",
                    color=discord.Color.red()
                )
            )

        if not message.mentions:
            return await message.channel.send(
                embed=discord.Embed(
                    title="User Not Found",
                    description="Please mention a user.",
                    color=discord.Color.red()
                )
            )

        member = message.mentions[0]

        role = message.guild.get_role(setup_roles[guild_id][alias])

        if role is None:
            return await message.channel.send(
                embed=discord.Embed(
                    title="Role Not Found",
                    description="The configured role no longer exists.",
                    color=discord.Color.red()
                )
            )

        if role >= message.guild.me.top_role:
            return await message.channel.send(
                embed=discord.Embed(
                    title="Role Hierarchy Error",
                    description="My highest role must be above the target role.",
                    color=discord.Color.red()
                )
            )

        if role >= message.author.top_role and message.author != message.guild.owner:
            return await message.channel.send(
                embed=discord.Embed(
                    title="Role Hierarchy Error",
                    description="You cannot assign or remove a role higher than or equal to your highest role.",
                    color=discord.Color.red()
                )
            )

        if role in member.roles:
            await member.remove_roles(
                role,
                reason=f"Setup Role | {message.author}"
            )

            embed = discord.Embed(
                title="Role Removed",
                description=f"Removed {role.mention} from {member.mention}.",
                color=discord.Color.green()
            )

        else:
            await member.add_roles(
                role,
                reason=f"Setup Role | {message.author}"
            )

            embed = discord.Embed(
                title="Role Assigned",
                description=f"Assigned {role.mention} to {member.mention}.",
                color=discord.Color.green()
            )

        await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SetupRole(bot))