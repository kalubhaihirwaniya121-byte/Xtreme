import discord
from discord.ext import commands
import json
from utils.emojis import Emojis

class NoPrefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_data(self):
        try:
            with open("data/noprefix.json", "r") as f:
                return json.load(f)
        except:
            return {}

    def save_data(self, data):
        with open("data/noprefix.json", "w") as f:
            json.dump(data, f, indent=4)

    @commands.hybrid_command(name="noprefix")
    @commands.has_permissions(administrator=True)
    async def noprefix(self, ctx, mode: str):
        data = self.load_data()

        guild_id = str(ctx.guild.id)

        if mode.lower() == "on":
            data[guild_id] = True
            self.save_data(data)

            return await ctx.send(
                f"{Emojis.TICK} No Prefix enabled for this server."
            )

        elif mode.lower() == "off":
            data[guild_id] = False
            self.save_data(data)

            return await ctx.send(
                f"{Emojis.TICK} No Prefix disabled for this server."
            )

        elif mode.lower() == "status":
            enabled = data.get(guild_id, False)

            return await ctx.send(
                f"{Emoji.MARK} No Prefix: {'Enabled' if enabled else 'Disabled'}"
            )

        await ctx.send(
            "Usage: `.noprefix on/off/status`"
        )

async def setup(bot):
    await bot.add_cog(NoPrefix(bot))