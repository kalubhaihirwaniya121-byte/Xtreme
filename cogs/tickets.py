import discord
import json
from utils.emojis import Emojis
from discord.ext import commands
from utils.ticket_views import TicketView

SETTINGS_FILE = "data/ticket_settings.json"


def load_data():
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_data(data):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="ticket",
        invoke_without_command=True
    )
    @commands.has_permissions(administrator=True)
    async def ticket(self, ctx):

        embed = discord.Embed(
            title=":ticket: Ticket Commands",
            description="""
`.ticket setup`
`.ticket category <category_id>`
`.ticket supportrole <role>`
`.ticket logs <channel>`
""",
            color=0x5865F2
        )

        await ctx.send(embed=embed)

    # =========================
    # CATEGORY
    # =========================

    @ticket.command(name="category")
    async def ticket_category(
        self,
        ctx,
        category: discord.CategoryChannel
    ):
        data = load_data()

        guild_id = str(ctx.guild.id)

        if guild_id not in data:
            data[guild_id] = {}

        data[guild_id]["category"] = category.id

        save_data(data)

        await ctx.send(
            f"{Emojis.TICK} Ticket category set to {category.name}"
        )

    # =========================
    # SUPPORT ROLE
    # =========================

    @ticket.command(name="supportrole")
    async def ticket_supportrole(
        self,
        ctx,
        role: discord.Role
    ):
        data = load_data()

        guild_id = str(ctx.guild.id)

        if guild_id not in data:
            data[guild_id] = {}

        data[guild_id]["support_role"] = role.id

        save_data(data)

        await ctx.send(
            f"{Emojis.TICK} Support role set to {role.mention}"
        )

    # =========================
    # LOGS CHANNEL
    # =========================

    @ticket.command(name="logs")
    async def ticket_logs(
        self,
        ctx,
        channel: discord.TextChannel
    ):
        data = load_data()

        guild_id = str(ctx.guild.id)

        if guild_id not in data:
            data[guild_id] = {}

        data[guild_id]["logs"] = channel.id

        save_data(data)

        await ctx.send(
            f"{Emojis.TICK} Logs channel set to {channel.mention}"
        )

    # =========================
    # SETUP PANEL
    # =========================

    @ticket.command(name="setup")
    async def ticket_setup(self, ctx):

        embed = discord.Embed(
            title=f"{Emojis.TICKET} Support Center",
            description=(
                "Need help?\n\n"
                "Select a category below "
                "to create a ticket."
            ),
            color=0x5865F2
        )

        embed.set_footer(
            text="Xtreme Ticket System"
        )

        await ctx.send(
            embed=embed,
            view=TicketView()
        )


async def setup(bot):
    await bot.add_cog(Tickets(bot))