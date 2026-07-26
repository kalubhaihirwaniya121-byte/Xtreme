import discord
import aiohttp
import base64
import os
import json
from discord.ext import commands
from discord.http import Route
from utils.emojis import Emojis
from cogs.whitelist import owner_or_whitelisted

class Customize(commands.Cog):
    """Commands to customize the bot's appearance per-server (Bot Owner Only)."""
    
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        # Clean up the aiohttp session when cog is unloaded
        self.bot.loop.create_task(self.session.close())

    async def get_image_bytes(self, ctx, url_or_attachment: str = None) -> bytes:
        """Helper to get image bytes from attachment or URL."""
        if ctx.message.attachments:
            return await ctx.message.attachments[0].read()
        
        if not url_or_attachment:
            raise commands.BadArgument("Please upload an image or provide a valid image URL.")

        try:
            async with self.session.get(url_or_attachment) as resp:
                if resp.status != 200:
                    raise commands.BadArgument(f"Failed to download image (HTTP Status: {resp.status})")
                return await resp.read()
        except Exception as e:
            raise commands.BadArgument(f"Failed to fetch image from URL: {e}")

    def bytes_to_data_uri(self, data: bytes) -> str:
        """Convert image bytes to Discord base64 data URI."""
        encoded = base64.b64encode(data).decode('utf-8')
        # We can default to image/png
        return f"data:image/png;base64,{encoded}"

    # =========================
    # SERVER CUSTOMIZATION COMMANDS (OWNER ONLY)
    # =========================

    @commands.group(name="customize", aliases=["customise"], invoke_without_command=True)
    @owner_or_whitelisted()
    async def customize_group(self, ctx):
        """Customize group command (Bot Owner Only)."""
        embed = discord.Embed(
            title="Customize Bot Settings (Owner Only)",
            description=(
                f"Use the subcommands to customize the bot's profile for the current server:\n\n"
                f"{Emojis.MARK} `customize avatar [url/attachment]` - Set bot server avatar\n"
                f"{Emojis.MARK} `customize banner [url/attachment]` - Set bot server banner\n"
                f"{Emojis.MARK} `customize nick [nickname]` - Set bot server nickname\n"
                f"{Emojis.MARK} `customize bio [bio]` - Set bot server bio\n"
                f"{Emojis.MARK} `customize reset <avatar/banner/bio/nick/all>` - Reset customization"
            ),
            color=0x3498db
        )
        embed.set_footer(text="Xtreme Customization")
        await ctx.send(embed=embed)

    @customize_group.command(name="avatar", aliases=["serveravatar"])
    @owner_or_whitelisted()
    async def serveravatar(self, ctx, url: str = None):
        """Set the bot's avatar specifically for this server (Bot Owner Only)."""
        await ctx.typing()
        try:
            image_data = await self.get_image_bytes(ctx, url)
            data_uri = self.bytes_to_data_uri(image_data)
            
            # Direct API PATCH using discord.py's internal Route/request
            route = Route('PATCH', '/guilds/{guild_id}/members/@me', guild_id=ctx.guild.id)
            res = await self.bot.http.request(route, json={"avatar": data_uri})
            print("AVATAR PATCH RESPONSE:", res)
            
            await ctx.send(f"{Emojis.TICK} Successfully updated the bot's server-specific avatar!")
        except Exception as e:
            await ctx.send(f"{Emojis.CROSS} Error: {e}")

    @customize_group.command(name="banner", aliases=["serverbanner"])
    @owner_or_whitelisted()
    async def serverbanner(self, ctx, url: str = None):
        """Set the bot's banner specifically for this server (Bot Owner Only)."""
        await ctx.typing()
        try:
            image_data = await self.get_image_bytes(ctx, url)
            data_uri = self.bytes_to_data_uri(image_data)
            
            # Direct API PATCH using discord.py's internal Route/request
            route = Route('PATCH', '/guilds/{guild_id}/members/@me', guild_id=ctx.guild.id)
            res = await self.bot.http.request(route, json={"banner": data_uri})
            print("BANNER PATCH RESPONSE:", res)
            
            await ctx.send(f"{Emojis.TICK} Successfully updated the bot's server-specific banner!")
        except Exception as e:
            await ctx.send(f"{Emojis.CROSS} Error: {e}")

    @customize_group.command(name="nick", aliases=["nickname", "servernick"])
    @owner_or_whitelisted()
    async def servernick(self, ctx, *, nickname: str = None):
        """Set the bot's nickname specifically for this server (Bot Owner Only, leave blank to reset)."""
        await ctx.typing()
        try:
            await ctx.guild.me.edit(nick=nickname)
            if nickname:
                await ctx.send(f"{Emojis.TICK} Successfully updated the bot's nickname in this server to **{nickname}**!")
            else:
                await ctx.send(f"{Emojis.TICK} Successfully reset the bot's nickname in this server!")
        except Exception as e:
            await ctx.send(f"{Emojis.CROSS} Error: {e}")

    @customize_group.command(name="bio", aliases=["serverbio"])
    @owner_or_whitelisted()
    async def serverbio(self, ctx, *, bio: str = None):
        """Set the bot's bio specifically for this server (Bot Owner Only, leave blank to reset)."""
        await ctx.typing()
        try:
            route = Route('PATCH', '/guilds/{guild_id}/members/@me', guild_id=ctx.guild.id)
            res = await self.bot.http.request(route, json={"bio": bio})
            print("BIO PATCH RESPONSE:", res)
            if bio:
                await ctx.send(f"{Emojis.TICK} Successfully updated the bot's bio/About Me in this server to: **{bio}**")
            else:
                await ctx.send(f"{Emojis.TICK} Successfully reset the bot's bio/About Me in this server!")
        except Exception as e:
            await ctx.send(f"{Emojis.CROSS} Error: {e}")

    # =========================
    # RESET CUSTOMIZATION
    # =========================

    @customize_group.command(name="reset")
    @owner_or_whitelisted()
    async def customize_reset(self, ctx, option: str):
        """Reset server-specific bot customization."""

        option = option.lower()
        valid_options = ["avatar", "banner", "bio", "nick", "all"]

        if option not in valid_options:
            return await ctx.send(
                f"{Emojis.CROSS} Invalid option. Use: "
                "`avatar`, `banner`, `bio`, `nick`, or `all`."
            )

        await ctx.typing()

        try:
            route = Route(
                "PATCH",
                "/guilds/{guild_id}/members/@me",
                guild_id=ctx.guild.id
            )

            if option == "avatar":
                await self.bot.http.request(
                    route,
                    json={"avatar": None}
                )

            elif option == "banner":
                await self.bot.http.request(
                    route,
                    json={"banner": None}
                )

            elif option == "bio":
                await self.bot.http.request(
                    route,
                    json={"bio": None}
                )

            elif option == "nick":
                await ctx.guild.me.edit(nick=None)

            elif option == "all":
                await self.bot.http.request(
                    route,
                    json={
                        "avatar": None,
                        "banner": None,
                        "bio": None
                    }
                )

                await ctx.guild.me.edit(nick=None)

            await ctx.send(
                f"{Emojis.TICK} Successfully reset bot "
                f"**{option}** customization for this server."
            )

        except Exception as e:
            await ctx.send(
                f"{Emojis.CROSS} Failed to reset customization: `{e}`"
            )

async def setup(bot):
    await bot.add_cog(Customize(bot))
