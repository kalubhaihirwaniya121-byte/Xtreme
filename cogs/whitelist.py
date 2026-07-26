import os

import json

import discord
from utils.storage import load_json, save_json
from discord.ext import commands
from utils.emojis import Emojis


# =========================
# Whitelist json
# =========================
WHITELIST_FILE = "data/whitelist.json"

def load_whitelist():

    if not os.path.exists(WHITELIST_FILE):

        return {"users": []}

    with open(WHITELIST_FILE, "r", encoding="utf-8") as f:

        return json.load(f)

def save_whitelist(data):

    with open(WHITELIST_FILE, "w", encoding="utf-8") as f:

        json.dump(data, f, indent=4)

whitelist = load_whitelist()

def owner_or_whitelisted():

    async def predicate(ctx):

        

        return await ctx.bot.is_owner(ctx.author) or ctx.author.id in whitelist["users"]

    return commands.check(predicate)

# =========================

class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


# =========================

# 🔐 SECRET OWNER COMMANDS

# =========================

# 🔹 Broadcast to ALL servers

    @commands.hybrid_command(name="xcast")

    @owner_or_whitelisted()

    async def xcast(self, ctx, *, message: str):

        embed = discord.Embed(

            title="Xtreme Announcement",

            description=message,

            color=0x5865F2

        )

        embed.set_footer(text="Xtreme • Owner Broadcast")

        sent, failed = 0, 0

        for guild in self.bot.guilds:

            channel = guild.system_channel

            if channel is None:

                for ch in guild.text_channels:

                    if ch.permissions_for(guild.me).send_messages:

                        channel = ch

                        break

            if channel:

                try:

                    await channel.send(embed=embed)

                    sent += 1

                except:

                    failed += 1

        await ctx.send(

            embed=discord.Embed(

                title="Broadcast Complete",

                description=f"{Emojis.TICK} Sent to **{sent}** servers\n{Emojis.CROSS} Failed in **{failed}** servers",

                color=0x2ecc71

            )

        )

# 🔹 List all servers bot is in

    @commands.hybrid_command(name="servers")

    @owner_or_whitelisted()

    async def servers(self, ctx):

        desc = ""

        for i, guild in enumerate(self.bot.guilds, start=1):

            desc += f"`{i}.` {guild.name} (`{guild.id}`)\n"

        embed = discord.Embed(

            title="Xtreme • Connected Servers",

            description=desc[:4090],

            color=0x5865F2

        )

        embed.set_footer(text=f"Total Servers: {len(self.bot.guilds)}")

        await ctx.send(embed=embed)

# 🔹 Broadcast to ONE specific server

    @commands.hybrid_command(name="xcastserver")

    @owner_or_whitelisted()

    async def xcastserver(self, ctx, server_id: int, *, message: str):

        guild = self.bot.get_guild(server_id)

        if not guild:

            return await ctx.send(f"{Emojis.CROSS} Bot is not in that server.")

        channel = guild.system_channel

        if channel is None:

            for ch in guild.text_channels:

                if ch.permissions_for(guild.me).send_messages:

                    channel = ch

                    break

        if not channel:

            return await ctx.send(f"{Emojis.CROSS} No writable channel found.")

        embed = discord.Embed(

            title="Xtreme Announcement",

            description=message,

            color=0x5865F2

        )

        embed.set_footer(text="Xtreme • Owner Message")

        await channel.send(embed=embed)

        await ctx.send(

            embed=discord.Embed(

                title="Message Sent",

                description=f"{Emojis.TICK} Sent to **{guild.name}**",

                color=0x2ecc71

            )

        )


# =========================
# Add user to whitelist 
# =========================
    @commands.hybrid_command(name="whitelistadd")

    @commands.is_owner()

    async def whitelist_add(self, ctx, user: discord.User):

        if user.id in whitelist["users"]:

            return await ctx.send(f"{Emojis.TICK} User is already whitelisted.")

        whitelist["users"].append(user.id)

        save_whitelist(whitelist)

        await ctx.send(

            embed=discord.Embed(

                title="User Whitelisted",

                description=f"{Emojis.TICK}{user.mention} has been added to the whitelist.",

                color=0x2ecc71

            )

        )
# =========================
# Remove user from Whitelist 
# =========================
    @commands.hybrid_command(name="whitelistremove")

    @commands.is_owner()

    async def whitelist_remove(self, ctx, user: discord.User):

        if user.id not in whitelist["users"]:

            return await ctx.send(f"{Emojis.CROSS} User is not whitelisted.")

        whitelist["users"].remove(user.id)

        save_whitelist(whitelist)

        await ctx.send(

            embed=discord.Embed(

                title="User Removed",

                description=f"{Emojis.TICK} {user.mention} has been removed from the whitelist.",

                color=0xe74c3c

            )

        )
# =========================
# Show Whitelist users
# =========================
    @commands.hybrid_command(name="whitelist")

    @commands.is_owner()

    async def whitelist_show(self, ctx):

        if not whitelist["users"]:

            return await ctx.send("Whitelist is empty.")

        desc = ""

        for uid in whitelist["users"]:

            desc += f"<@{uid}> (`{uid}`)\n"

        embed = discord.Embed(

            title="Whitelisted Users",

            description=desc,

            color=0x5865F2

        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Whitelist(bot))