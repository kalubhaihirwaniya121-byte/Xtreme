import discord 
import os
import inspect
import psutil 
import time
from discord.ext import commands
from utils.emojis import Emojis
from cogs.whitelist import owner_or_whitelisted
from utils.action_loader import load_action_gifs

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    @commands.command(name="reload")
    @owner_or_whitelisted()
    async def reload(self, ctx):

        loaded = 0
        failed = []

        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                cog = f"cogs.{filename[:-3]}"

                try:
                    await self.bot.reload_extension(cog)
                    loaded += 1
                except Exception as e:
                    failed.append(f"{filename}: {e}")
        await load_action_gifs(self.bot)
        
        embed = discord.Embed(
            title=f"{Emojis.TICK} Reload Complete",
            color=0x2ecc71
        )

        embed.add_field(
            name=f"{Emojis.MARK}Reloaded Cogs",
            value=str(loaded),
            inline=False
        )
        embed.add_field(
            name=f"{Emojis.MARK}Action GIFs",
            value="Reloaded Successfully",
            inline=False
        )
        
        if failed:
            embed.add_field(
                name="Failed",
                value="\n".join(failed[:10]),
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="emojis")
    @owner_or_whitelisted()
    async def emojis(self, ctx):
        emoji_list = []

        for name, value in inspect.getmembers(Emojis):
            if name.startswith("_"):
                continue

            if isinstance(value, str):
                emoji_list.append(f"`{name}` → {value}")

        if not emoji_list:
            return await ctx.send("❌ No emojis found.")

        embeds = []
        description = ""

        for line in sorted(emoji_list):
            if len(description) + len(line) + 1 > 4000:
                embed = discord.Embed(
                    title="😀 Xtreme Emojis",
                    description=description,
                    color=discord.Color.blurple()
                )
                embeds.append(embed)
                description = ""

            description += line + "\n"

        if description:
            embed = discord.Embed(
                title="😀 Xtreme Emojis",
                description=description,
                color=discord.Color.blurple()
            )
            embeds.append(embed)

        for index, embed in enumerate(embeds, start=1):
            embed.set_footer(
                text=f"Page {index}/{len(embeds)} • Total Emojis: {len(emoji_list)}"
            )
            await ctx.send(embed=embed)


    @commands.hybrid_command(name="botstats", description="View bot statistics")
    @commands.is_owner()
    async def botstats(self, ctx):
        ping = round(self.bot.latency * 1000)

        process = psutil.Process()
        ram = process.memory_info().rss / 1024 / 1024
        cpu = psutil.cpu_percent(interval=1)

        guilds = len(self.bot.guilds)
        users = sum(g.member_count or 0 for g in self.bot.guilds)

        uptime_seconds = int(time.time() - self.start_time)

        days, rem = divmod(uptime_seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)

        uptime = f"{days}d {hours}h {minutes}m {seconds}s"

        embed = discord.Embed(
            title=f"{Emojis.STAT} Xtreme Statistics",
            color=0x5865F2
        )

        embed.add_field(
            name="Latency",
            value=f"`{ping} ms`",
            inline=True
        )

        embed.add_field(
            name="Memory Usage",
            value=f"`{ram:.2f} MB`",
            inline=True
        )

        embed.add_field(
            name="CPU Usage",
            value=f"`{cpu}%`",
            inline=True
        )

        embed.add_field(
            name="Servers",
            value=f"`{guilds}`",
            inline=True
        )

        embed.add_field(
            name="Users",
            value=f"`{users:,}`",
            inline=True
        )

        embed.add_field(
            name="Uptime",
            value=f"`{uptime}`",
            inline=True
        )

        embed.set_footer(text="Xtreme • Owner Statistics")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Owner(bot))