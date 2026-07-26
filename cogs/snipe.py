import discord

from discord.ext import commands


class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # channel_id -> deleted message
        self.snipes = {}

        # channel_id -> edited message
        self.edit_snipes = {}
        
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):

        if message.author.bot:
            return

        if not message.guild:
            return

        attachments = []

        for attachment in message.attachments:
            attachments.append(attachment.url)

        self.snipes[message.channel.id] = {
            "author": message.author,
            "content": message.content,
            "attachments": attachments,
            "created_at": message.created_at
        }
        
    @commands.Cog.listener()
    async def on_message_edit(
        self,
        before: discord.Message,
        after: discord.Message
    ):

        if before.author.bot:
            return

        if not before.guild:
            return

        if before.content == after.content:
            return

        attachments = []

        for attachment in after.attachments:
            attachments.append(attachment.url)

        self.edit_snipes[before.channel.id] = {
            "author": before.author,
            "before": before.content,
            "after": after.content,
            "attachments": attachments,
            "edited_at": discord.utils.utcnow()
        }
        
    @commands.hybrid_command(
        name="snipe",
        description="Show the last deleted message."
    )
    async def snipe(self, ctx):

        data = self.snipes.get(ctx.channel.id)

        if not data:
            embed = discord.Embed(
                description="❌ Nothing to snipe in this channel.",
                color=0xE74C3C
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            description=data["content"] or "*No text content.*",
            color=0x5865F2,
            timestamp=data["created_at"]
        )

        embed.set_author(
            name=str(data["author"]),
            icon_url=data["author"].display_avatar.url
        )

        if data["attachments"]:
            embed.set_image(
                url=data["attachments"][0]
            )

        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)
        
    @commands.hybrid_command(
        name="editsnipe",
        description="Show the last edited message."
    )
    async def editsnipe(self, ctx):

        data = self.edit_snipes.get(ctx.channel.id)

        if not data:
            embed = discord.Embed(
                description="❌ Nothing to editsnipe in this channel.",
                color=0xE74C3C
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title="✏️ Edited Message",
            color=0xF1C40F,
            timestamp=data["edited_at"]
        )

        embed.set_author(
            name=str(data["author"]),
            icon_url=data["author"].display_avatar.url
        )

        embed.add_field(
            name="Before",
            value=data["before"] or "*No text content.*",
            inline=False
        )

        embed.add_field(
            name="After",
            value=data["after"] or "*No text content.*",
            inline=False
        )

        if data["attachments"]:
            embed.set_image(
                url=data["attachments"][0]
            )

        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)
        
async def setup(bot):
    await bot.add_cog(Snipe(bot))