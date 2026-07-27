import os

import json
import json

import asyncio
import discord

from discord.ext import commands
from utils.storage import load_json, save_json
from dotenv import load_dotenv
from utils.emojis import Emojis
from utils.action_loader import load_action_gifs
from utils.truthdare_loader import load_truth_dare, TRUTHS, DARES
from utils.truthdare_views import TruthDareView
from utils.ticket_views import TicketView, TicketControls


# =========================

# LOAD ENV

# =========================

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not TOKEN:

    raise RuntimeError("DISCORD_BOT_TOKEN not found in .env")


# =========================
# PREFIX + NO PREFIX SYSTEM
# =========================

DEFAULT_PREFIX = "."
PREFIX_FILE = "data/prefixes.json"
NOPREFIX_FILE = "data/noprefix.json"

def load_prefixes():
    if not os.path.exists(PREFIX_FILE):
        return {}

    with open(PREFIX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_prefixes(data):
    with open(PREFIX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

prefixes = load_prefixes()

async def get_prefix(bot, message):

    if not message.guild:
        return DEFAULT_PREFIX

    guild_id = str(message.guild.id)

    try:
        with open(NOPREFIX_FILE, "r", encoding="utf-8") as f:
            noprefix = json.load(f)
    except:
        noprefix = {}
        print("NOPREFIX:", noprefix.get(guild_id, False))

    prefix = prefixes.get(guild_id, DEFAULT_PREFIX)

    if noprefix.get(guild_id, False):
        return ["", prefix]

    return prefix

# =========================

# INTENTS

# =========================

intents = discord.Intents.default()

intents.message_content = True

intents.members = True

intents.voice_states = True

# =========================

# BOT SETUP

# =========================

bot = commands.Bot(
    command_prefix=get_prefix,
    intents=intents
)
bot.remove_command("help")


    

# =========================

# COGS LIST

# =========================

INITIAL_COGS = [

    "cogs.moderation",

    "cogs.afk",

    "cogs.media",

    "cogs.welcomer",

    "cogs.antinuke",

    "cogs.giveaways",
    
    "cogs.autoresponder",
    
    "cogs.botcleaner",
    
    "cogs.whitelist",
    
    "cogs.info",
    
    "cogs.noprefix",
    
    "cogs.tickets",
    
    "cogs.owner",
    
    "cogs.channel",
    
    "cogs.status",
    
    "cogs.gif",
    
    "cogs.relationship",
    
    "cogs.loveletter",
    
    "cogs.action",
    
    "cogs.snipe",
    
    "cogs.truthdare",
    
    "cogs.automod",
    
    "cogs.counting",
    
    "cogs.logging",
    
    "cogs.customize",
    
    "cogs.setuprole",
    
    "cogs.help",
    
    "cogs.embed"
    
]

# =========================

# EVENTS

# =========================

@bot.event
async def on_ready():

    print(f"[XTREME] Logged in as {bot.user}")
    print(f"[XTREME] Connected to {len(bot.guilds)} servers")

    try:
        await bot.tree.sync()
        print("[XTREME] Slash commands synced")

    except Exception as e:
        print("[XTREME] Slash sync failed:", e)
        
    await load_action_gifs(bot)
        
    load_truth_dare()

    bot.add_view(
        TruthDareView(
            bot,
            TRUTHS,
            DARES
        )
    )
    bot.add_view(TicketView())
    bot.add_view(TicketControls())
# =========================

# LOAD COGS

# =========================

async def load_cogs():

    for cog in INITIAL_COGS:

        try:

            await bot.load_extension(cog)

            print(f"[COG] Loaded {cog}")

        except Exception as e:

            print(f"[COG] Failed to load {cog}: {e}")

# =========================

# 🔧 SETPREFIX COMMAND

# =========================

@bot.hybrid_command(name="setprefix")

@commands.has_permissions(manage_guild=True)

async def setprefix(ctx, prefix: str):

    if len(prefix) > 5:

        return await ctx.send(f"{Emojis.CROSS} Prefix too long (max 5 characters).")

    prefixes[str(ctx.guild.id)] = prefix

    save_prefixes(prefixes)

    await ctx.send(

        embed=discord.Embed(

            title="Prefix Updated",

            description=f"New prefix for this server is `{prefix}`",

            color=0x2ecc71

        )

    )


# =========================

# MAIN

# =========================

async def main():

    async with bot:

        await load_cogs()

        await bot.start(TOKEN)

if __name__ == "__main__":

    asyncio.run(main())