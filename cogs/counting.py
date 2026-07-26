import discord
from discord.ext import commands
from utils.emojis import Emojis
try:
    from utils.counting_utils import (
        get_guild_data,
        update_guild_data,
        get_user_stats
    )
except ModuleNotFoundError:
    from counting_utils import (
        get_guild_data,
        update_guild_data,
        get_user_stats)
        
class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="counting",
        invoke_without_command=True
    )
    @commands.has_permissions(manage_guild=True)
    async def counting(self, ctx):

        data = get_guild_data(ctx.guild.id)

        status = "🟢 Enabled" if data["enabled"] else "🔴 Disabled"

        channel = (
            f"<#{data['channel']}>"
            if data["channel"]
            else "`Not Configured`"
        )

        last_counter = (
            f"<@{data['last_user']}>"
            if data["last_user"]
            else "`None`"
        )

        embed = discord.Embed(
            title="🔢 Xtreme Counting",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Status",
            value=status,
            inline=True
        )

        embed.add_field(
            name="Channel",
            value=channel,
            inline=True
        )

        embed.add_field(
            name="Current Number",
            value=f"`{data['current']}`",
            inline=True
        )

        embed.add_field(
            name="Current Streak",
            value=f"`{data['current_streak']}`",
            inline=True
        )

        embed.add_field(
            name="Best Streak",
            value=f"`{data['best_streak']}`",
            inline=True
        )

        embed.add_field(
            name="Last Counter",
            value=last_counter,
            inline=True
        )

        embed.set_footer(
            text="Xtreme • Counting System"
        )

        await ctx.send(embed=embed)
        
    @counting.command(name="set")
    @commands.has_permissions(manage_guild=True)
    async def counting_set(
        self,
        ctx,
        channel: discord.TextChannel = None
    ):

        if channel is None:
            return await ctx.send(
                f"{Emojis.CROSS} Usage: `.counting set #channel`"
            )

        data = get_guild_data(ctx.guild.id)

        data["enabled"] = True
        data["channel"] = channel.id
        data["current"] = 1
        data["current_streak"] = 0
        data["last_user"] = 0

        update_guild_data(
            ctx.guild.id,
            data
        )

        embed = discord.Embed(
            title="🔢 Counting Enabled",
            description=(
                f"**Channel:** {channel.mention}\n"
                f"**Starting Number:** `1`"
            ),
            color=discord.Color.green()
        )

        embed.set_footer(
            text="Xtreme • Counting"
        )

        await ctx.send(embed=embed)
        
    @counting.command(name="remove")
    @commands.has_permissions(manage_guild=True)
    async def counting_remove(self, ctx):

        data = get_guild_data(ctx.guild.id)

        if not data["enabled"]:
            return await ctx.send(
                f"{Emojis.CROSS} Counting is already disabled."
            )

        data["enabled"] = False
        data["channel"] = None
        data["current"] = 1
        data["current_streak"] = 0
        data["last_user"] = 0

        update_guild_data(
            ctx.guild.id,
            data
        )

        embed = discord.Embed(
            title=f"{Emojis.TICK} Counting Disabled",
            description="Counting has been disabled successfully.",
            color=discord.Color.red()
        )

        embed.set_footer(
            text="Xtreme • Counting"
        )

        await ctx.send(embed=embed)
        
    @counting.command(name="reset")
    @commands.has_permissions(manage_guild=True)
    async def counting_reset(self, ctx):

        data = get_guild_data(ctx.guild.id)

        if not data["enabled"]:
            return await ctx.send(
                f"{Emojis.TICK} Counting is not enabled."
            )

        data["current"] = 1
        data["current_streak"] = 0
        data["last_user"] = 0

        update_guild_data(
            ctx.guild.id,
            data
        )

        embed = discord.Embed(
            title=f"{Emojis.TICK} Counting Reset",
            description=(
                "The counting chain has been reset.\n\n"
                "**Next Number:** `1`"
            ),
            color=discord.Color.orange()
        )

        embed.set_footer(
            text="Xtreme • Counting"
        )

        await ctx.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        if not message.guild:
            return

        data = get_guild_data(message.guild.id)

        if not data["enabled"]:
            return

        if message.channel.id != data["channel"]:
            return

        # Ignore everything except pure numbers
        if not message.content.isdigit():
            return

        expected = data["current"]
        received = int(message.content)

        # Same user can't count twice
        if message.author.id == data["last_user"]:

            embed = discord.Embed(
                title="⚠️ Wait!",
                description=(
                    "You can't count twice in a row.\n\n"
                    "Let another member continue the chain."
                ),
                color=discord.Color.orange()
            )

            await message.channel.send(embed=embed)
            return
          
        # Correct number
        if received == expected:

            await message.add_reaction(f"{Emojis.TICK}")

            data["current"] += 1
            data["current_streak"] += 1
            data["last_user"] = message.author.id

            stats = get_user_stats(
                data,
                message.author.id
            )

            stats["correct"] += 1

            if data["current_streak"] > stats["best_streak"]:
                stats["best_streak"] = data["current_streak"]

            record_broken = False

            if data["current_streak"] > data["best_streak"]:
                old_record = data["best_streak"]
                data["best_streak"] = data["current_streak"]
                record_broken = True

            update_guild_data(
                message.guild.id,
                data
            )

            if record_broken:

                embed = discord.Embed(
                    title="🏆 New Server Record!",
                    description=(
                        f"**Previous Record:** `{old_record}`\n"
                        f"**New Record:** `{data['best_streak']}`\n\n"
                        "🎉 Congratulations everyone!\n"
                        "Keep the chain alive! 🔥"
                    ),
                    color=discord.Color.gold()
                )

                embed.set_footer(
                    text="Xtreme • Counting"
                )

                await message.channel.send(embed=embed)

            return
          
        # Wrong number
        await message.add_reaction(f"{Emojis.CROSS}")

        stats = get_user_stats(
            data,
            message.author.id
        )

        stats["broken"] += 1

        broken_streak = data["current_streak"]

        embed = discord.Embed(
            title="💥 Chain Broken!",
            description=(
                "The counting chain has been broken.\n\n"
                f"**Expected Number:** `{expected}`\n"
                f"**Received Number:** `{received}`\n"
                f"**Chain Broken By:** {message.author.mention}\n"
                f"**Current Streak:** `{broken_streak}`\n\n"
                "🔄 **Counting has been reset.**\n"
                "**Next Number:** `1`"
            ),
            color=discord.Color.red()
        )

        embed.set_footer(
            text="Xtreme • Counting"
        )

        data["current"] = 1
        data["current_streak"] = 0
        data["last_user"] = 0

        update_guild_data(
            message.guild.id,
            data
        )

        await message.channel.send(embed=embed)

    @counting.command(name="leaderboard")
    async def counting_leaderboard(self, ctx):

        data = get_guild_data(ctx.guild.id)

        users = data["user_stats"]

        if not users:
            return await ctx.send(
                f"{Emojis.CROSS} No counting data found."
            )

        sorted_users = sorted(
            users.items(),
            key=lambda x: x[1]["correct"],
            reverse=True
        )[:10]

        embed = discord.Embed(
            title="🏆 Counting Leaderboard",
            color=discord.Color.gold()
        )

        description = ""

        medals = ["🥇", "🥈", "🥉"]

        for index, (user_id, stats) in enumerate(sorted_users):

            member = ctx.guild.get_member(int(user_id))

            if member:
                name = member.mention
            else:
                name = f"`{user_id}`"

            if index < 3:
                place = medals[index]
            else:
                place = f"**{index+1}.**"

            description += (
                f"{place} {name} — "
                f"`{stats['correct']}` counts\n"
            )

        embed.description = description
        embed.set_footer(text="Xtreme • Counting")

        await ctx.send(embed=embed)
        
    @counting.command(name="stats")
    async def counting_stats(
        self,
        ctx,
        member: discord.Member = None
    ):

        member = member or ctx.author

        data = get_guild_data(ctx.guild.id)

        stats = get_user_stats(
            data,
            member.id
        )

        embed = discord.Embed(
            title="📊 Counting Stats",
            color=discord.Color.blurple()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.add_field(
            name="User",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="Correct Counts",
            value=f"`{stats['correct']}`",
            inline=True
        )

        embed.add_field(
            name="Chains Broken",
            value=f"`{stats['broken']}`",
            inline=True
        )

        embed.add_field(
            name="Best Streak",
            value=f"`{stats['best_streak']}`",
            inline=True
        )

        embed.set_footer(
            text="Xtreme • Counting"
        )

        await ctx.send(embed=embed)
        
async def setup(bot):
    await bot.add_cog(Counting(bot))

