import discord

from discord.ext import commands

import json

import os
from utils.storage import load_json, save_json
from utils.emojis import Emojis

DATA_FILE = "data/botcleaner.json"

EMBED_COLOR = 0x5865F2

FOOTER = "Xtreme • Auto Cleanup"

# =========================

# DATA

# =========================

def load():

    if not os.path.exists(DATA_FILE):

        return {"channels": {}, "bypass": []}

    with open(DATA_FILE, "r", encoding="utf-8") as f:

        return json.load(f)

def save():

    with open(DATA_FILE, "w", encoding="utf-8") as f:

        json.dump(data, f, indent=4)

data = load()

# =========================

# CHECKS

# =========================

def admin_or_owner():

    async def predicate(ctx):

        if await ctx.bot.is_owner(ctx.author):

            return True

        return ctx.author.guild_permissions.administrator

    return commands.check(predicate)

# =========================

# COG

# =========================

class BotCleaner(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    # =====================

    # AUTO DELETE LISTENER

    # =====================

    @commands.Cog.listener()

    async def on_message(self, message: discord.Message):

        if not message.guild or not message.author.bot:

            return

        # bypass specific bots

        if str(message.author.id) in data["bypass"]:

            return

        cfg = data["channels"].get(str(message.channel.id))

        if not cfg:

            return

        try:

            await message.delete(delay=cfg["delay"])

        except:

            pass

    # =====================

    # MANUAL DELETE: .bot 5

    # =====================

    @commands.hybrid_command(name="bot")

    @admin_or_owner()

    async def bot(self, ctx, amount: int):

        """Delete recent bot messages. Usage: .bot 5"""

        if amount <= 0:

            return await ctx.send(

                "Amount must be greater than 0.",

                delete_after=5

            )

        deleted = 0

        async for msg in ctx.channel.history(limit=200):

            if msg.author.bot:

                try:

                    await msg.delete()

                    deleted += 1

                except:

                    pass

                if deleted >= amount:

                    break

        embed = discord.Embed(

            title=f"{Emojis.CLEANER} Bot Messages Cleaned",

            description=f"Successfully deleted **{deleted}** bot messages.",

            color=EMBED_COLOR

        )

        embed.set_footer(text=FOOTER)

        await ctx.send(embed=embed, delete_after=10)

    # =====================

    # GROUP: .botc

    # =====================

    @commands.hybrid_group(name="botc")

    async def botc(self, ctx):

        if ctx.invoked_subcommand is None:

            await ctx.send(

                "Use: `set`, `off`, `status`, `bypass`",

                delete_after=5

            )

    # =====================

    # SET AUTO DELETE

    # =====================

    @botc.command(name="set")

    @admin_or_owner()

    async def set(self, ctx, channel: discord.TextChannel, time: int):

        data["channels"][str(channel.id)] = {"delay": time}

        save()

        embed = discord.Embed(

            title=f"{Emojis.TICK} Auto Delete Enabled",

            description=(

                f"Bot messages in {channel.mention} will be "

                f"deleted after **{time} seconds**."

            ),

            color=0x2ECC71

        )

        embed.set_footer(text=FOOTER)

        await ctx.send(embed=embed, delete_after=10)

    # =====================

    # DISABLE AUTO DELETE

    # =====================

    @botc.command(name="off")

    @admin_or_owner()

    async def off(self, ctx, channel: discord.TextChannel):

        data["channels"].pop(str(channel.id), None)

        save()

        embed = discord.Embed(

            title=f"{Emojis.TICK} Auto Delete Disabled",

            description=f"Auto delete disabled in {channel.mention}.",

            color=0xE74C3C

        )

        embed.set_footer(text=FOOTER)

        await ctx.send(embed=embed, delete_after=10)

    # =====================

    # STATUS

    # =====================

    @botc.command(name="status")

    @admin_or_owner()

    async def status(self, ctx):

        if not data["channels"]:

            return await ctx.send(

                "No channels have auto-delete enabled.",

                delete_after=10

            )

        lines = []

        for cid, cfg in data["channels"].items():

            ch = ctx.guild.get_channel(int(cid))

            if ch:

                lines.append(f"{ch.mention} → {cfg['delay']}s")

        embed = discord.Embed(

            title=f"{Emojis.MARK} Bot Auto-Delete Status",

            description="\n".join(lines),

            color=EMBED_COLOR

        )

        embed.set_footer(text=FOOTER)

        await ctx.send(embed=embed, delete_after=10)

    # =====================

    # BYPASS GROUP

    # =====================

    @botc.group(name="bypass")

    async def bypass(self, ctx):

        pass

    @bypass.command(name="add")

    @admin_or_owner()

    async def bypass_add(self, ctx, bot_id: int):

        if str(bot_id) not in data["bypass"]:

            data["bypass"].append(str(bot_id))

            save()

        await ctx.send(

            f"Bot `{bot_id}` added to bypass list.",

            delete_after=10

        )

    @bypass.command(name="remove")

    @admin_or_owner()

    async def bypass_remove(self, ctx, bot_id: int):

        if str(bot_id) in data["bypass"]:

            data["bypass"].remove(str(bot_id))

            save()

        await ctx.send(

            f"Bot `{bot_id}` removed from bypass list.",

            delete_after=10

        )

    @bypass.command(name="list")

    @admin_or_owner()

    async def bypass_list(self, ctx):

        if not data["bypass"]:

            return await ctx.send(

                "No bots are bypassed.",

                delete_after=10

            )

        await ctx.send(

            "Bypassed bots:\n" + "\n".join(data["bypass"]),

            delete_after=10

        )

async def setup(bot):

    await bot.add_cog(BotCleaner(bot))