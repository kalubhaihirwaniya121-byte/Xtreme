import discord

from discord.ext import commands
from utils.storage import load_json, save_json
import json

import os

DATA_FILE = "data/autoresponders.json"

def load_data():

    if not os.path.exists(DATA_FILE):

        return {}

    with open(DATA_FILE, "r", encoding="utf-8") as f:

        return json.load(f)

def save_data(data):

    with open(DATA_FILE, "w", encoding="utf-8") as f:

        json.dump(data, f, indent=4)

autoresponders = load_data()

class AutoResponder(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    # =========================

    # LISTENER (PLAIN TEXT RESPONSE)

    # =========================

    @commands.Cog.listener()

    async def on_message(self, message):

        if message.author.bot or not message.guild:

            return

        guild_id = str(message.guild.id)

        if guild_id not in autoresponders:

            return

        content = message.content.lower()

        for trigger, response in autoresponders[guild_id].items():

            if trigger in content:

                await message.channel.send(response)

                break

    # =========================

    # GROUP COMMAND

    # =========================

    @commands.hybrid_group(name="autoresponder", invoke_without_command=True)

    @commands.has_permissions(administrator=True)

    async def autoresponder_group(self, ctx):

        embed = discord.Embed(

            title="Autoresponder Commands",

            description=(

                "`autoresponder add <trigger> | <response>`\n"

                "`autoresponder remove <trigger>`\n"

                "`autoresponder list`"

            ),

            color=0x5865F2

        )

        embed.set_footer(text="Xtreme • Autoresponder System")

        await ctx.send(embed=embed)

    # =========================

    # ADD

    # =========================

    @autoresponder_group.command(name="add")

    @commands.has_permissions(administrator=True)

    async def add(self, ctx, *, args: str):

        if "|" not in args:

            return await ctx.send(

                embed=discord.Embed(

                    title="Invalid Format",

                    description="Use: `autoresponder add trigger | response`",

                    color=0xe74c3c

                )

            )

        trigger, response = map(str.strip, args.split("|", 1))

        trigger = trigger.lower()

        guild_id = str(ctx.guild.id)

        autoresponders.setdefault(guild_id, {})[trigger] = response

        save_data(autoresponders)

        embed = discord.Embed(

            title="Autoresponder Created",

            color=0x2ecc71

        )

        embed.add_field(name="Trigger", value=trigger, inline=False)

        embed.add_field(name="Response", value=response, inline=False)

        embed.set_footer(text="Xtreme • Autoresponder")

        await ctx.send(embed=embed)

    # =========================

    # REMOVE

    # =========================

    @autoresponder_group.command(name="remove")

    @commands.has_permissions(administrator=True)

    async def remove(self, ctx, *, trigger: str):

        trigger = trigger.lower()

        guild_id = str(ctx.guild.id)

        if guild_id not in autoresponders or trigger not in autoresponders[guild_id]:

            return await ctx.send(

                embed=discord.Embed(

                    title="Not Found",

                    description="That trigger does not exist.",

                    color=0xe74c3c

                )

            )

        del autoresponders[guild_id][trigger]

        save_data(autoresponders)

        await ctx.send(

            embed=discord.Embed(

                title="Autoresponder Removed",

                description=f"Trigger `{trigger}` has been removed.",

                color=0xe74c3c

            )

        )

    # =========================

    # LIST

    # =========================

    @autoresponder_group.command(name="list")

    @commands.has_permissions(administrator=True)

    async def list_autoresponders(self, ctx):

        guild_id = str(ctx.guild.id)

        if guild_id not in autoresponders or not autoresponders[guild_id]:

            return await ctx.send(

                embed=discord.Embed(

                    title="No Autoresponders",

                    description="This server has no autoresponders.",

                    color=0xf1c40f

                )

            )

        desc = ""

        for trigger in autoresponders[guild_id]:

            desc += f"• `{trigger}`\n"

        embed = discord.Embed(

            title="Autoresponders List",

            description=desc,

            color=0x5865F2

        )

        embed.set_footer(text="Xtreme • Autoresponder")

        await ctx.send(embed=embed)

async def setup(bot):

    await bot.add_cog(AutoResponder(bot))