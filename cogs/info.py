import discord
from discord.ext import commands
from utils.emojis import Emojis

EMBED_COLOR = 0x5865F2


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =========================
    # USERINFO
    # =========================

    @commands.hybrid_command(
        name="userinfo",
        description="View information about a user."
    )
    async def userinfo(
        self,
        ctx,
        member: discord.Member = None
    ):
        member = member or ctx.author

        embed = discord.Embed(
            title=f"{Emojis.INFO}User Information",
            color=EMBED_COLOR,
            timestamp=discord.utils.utcnow()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.add_field(
            name="User",
            value=f"{member.mention}",
            inline=True
        )

        embed.add_field(
            name="User ID",
            value=f"`{member.id}`",
            inline=True
        )

        embed.add_field(
            name="Nickname",
            value=member.nick or "None",
            inline=True
        )

        embed.add_field(
            name="Top Role",
            value=member.top_role.mention,
            inline=True
        )

        embed.add_field(
            name="Roles",
            value=str(len(member.roles) - 1),
            inline=True
        )

        embed.add_field(
            name="Bot",
            value="Yes" if member.bot else "No",
            inline=True
        )

        embed.add_field(
            name="Account Created",
            value=discord.utils.format_dt(
                member.created_at,
                style="F"
            ),
            inline=False
        )

        embed.add_field(
            name="Joined Server",
            value=discord.utils.format_dt(
                member.joined_at,
                style="F"
            ),
            inline=False
        )

        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)

    # =========================
    # SERVERINFO
    # =========================

    @commands.hybrid_command(
        name="serverinfo",
        description="View information about the server."
    )
    async def serverinfo(self, ctx):

        guild = ctx.guild

        humans = len(
            [m for m in guild.members if not m.bot]
        )

        bots = len(
            [m for m in guild.members if m.bot]
        )

        embed = discord.Embed(
            title=f"{Emojis.INFO}Server Information",
            color=EMBED_COLOR,
            timestamp=discord.utils.utcnow()
        )

        if guild.icon:
            embed.set_thumbnail(
                url=guild.icon.url
            )

        embed.add_field(
            name="Server Name",
            value=guild.name,
            inline=True
        )

        embed.add_field(
            name="Server ID",
            value=f"`{guild.id}`",
            inline=True
        )

        embed.add_field(
            name="Owner",
            value=str(guild.owner),
            inline=True
        )

        embed.add_field(
            name="Members",
            value=f"{guild.member_count}",
            inline=True
        )

        embed.add_field(
            name="Humans",
            value=f"{humans}",
            inline=True
        )

        embed.add_field(
            name="Bots",
            value=f"{bots}",
            inline=True
        )

        embed.add_field(
            name="Roles",
            value=f"{len(guild.roles)}",
            inline=True
        )

        embed.add_field(
            name="Channels",
            value=f"{len(guild.channels)}",
            inline=True
        )

        embed.add_field(
            name="Boosts",
            value=f"{guild.premium_subscription_count}",
            inline=True
        )

        embed.add_field(
            name="Created",
            value=discord.utils.format_dt(
                guild.created_at,
                style="F"
            ),
            inline=False
        )

        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)

    # =========================
    # AVATAR
    # =========================

    @commands.hybrid_command(
        name="avatar",
        description="View a user's avatar."
    )
    async def avatar(
        self,
        ctx,
        member: discord.Member = None
    ):
        member = member or ctx.author

        embed = discord.Embed(
            title=f"{member}'s Avatar",
            color=EMBED_COLOR,
            timestamp=discord.utils.utcnow()
        )

        embed.set_image(
            url=member.display_avatar.url
        )

        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Info(bot))