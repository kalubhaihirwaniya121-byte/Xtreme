import discord
import asyncio 
from discord.ext import commands
from utils.emojis import Emojis
import json
import os 

class NukeConfirmView(discord.ui.View):
    def __init__(self, author):
        super().__init__(timeout=30)
        self.author = author

    @discord.ui.button(
        label="Confirm",
        emoji=f"{Emojis.TICK}",
        style=discord.ButtonStyle.danger
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.user.id != self.author.id:
            return await interaction.response.send_message(
                f"{Emojis.CROSS} You cannot use this button.",
                ephemeral=True
            )

        old_channel = interaction.channel

        new_channel = await old_channel.clone(
            reason=f"Nuked by {interaction.user}"
        )

        await new_channel.edit(
            position=old_channel.position
        )

        await old_channel.delete()

        embed = discord.Embed(
            title=f"{Emojis.TICK} Channel Nuked",
            description=(
                f"Nuked by {interaction.user.mention}"
            ),
            color=0xe74c3c
        )

        await new_channel.send(embed=embed)

    @discord.ui.button(
        label="Cancel",
        emoji=f"{Emojis.CROSS}",
        style=discord.ButtonStyle.secondary
    )
    async def cancel(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.user.id != self.author.id:
            return

        await interaction.response.edit_message(
            content=f"{Emojis.CROSS} Nuke cancelled.",
            embed=None,
            view=None
        )


class Channel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.file = "data/sticky_messages.json"

        if not os.path.exists(self.file):
            with open(self.file, "w") as f:
                json.dump({}, f)

        self.load_data()
        
    def load_data(self):
        with open(self.file, "r") as f:
            self.data = json.load(f)

    def save_data(self):
        with open(self.file, "w") as f:
            json.dump(self.data, f, indent=4)

    def success(self, text):
        return discord.Embed(
            description=f"{Emojis.TICK} {text}",
            color=0x2ecc71
        )

    # LOCK

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):

        overwrite = ctx.channel.overwrites_for(
            ctx.guild.default_role
        )

        overwrite.send_messages = False

        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            overwrite=overwrite
        )

        await ctx.send(
            embed=self.success(
                f"{ctx.channel.mention} locked."
            )
        )

    # UNLOCK

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):

        overwrite = ctx.channel.overwrites_for(
            ctx.guild.default_role
        )

        overwrite.send_messages = True

        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            overwrite=overwrite
        )

        await ctx.send(
            embed=self.success(
                f"{ctx.channel.mention} unlocked."
            )
        )

    # HIDE

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def hide(self, ctx):

        overwrite = ctx.channel.overwrites_for(
            ctx.guild.default_role
        )

        overwrite.view_channel = False

        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            overwrite=overwrite
        )

        await ctx.send(
            embed=self.success(
                f"{ctx.channel.name} hidden."
            )
        )

    # UNHIDE

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def unhide(self, ctx):

        overwrite = ctx.channel.overwrites_for(
            ctx.guild.default_role
        )

        overwrite.view_channel = True

        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            overwrite=overwrite
        )

        await ctx.send(
            embed=self.success(
                f"{ctx.channel.name} visible now."
            )
        )

    # RENAME

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def rename(self, ctx, *, name):

        await ctx.channel.edit(name=name)

        await ctx.send(
            embed=self.success(
                f"Channel renamed to `{name}`"
            )
        )
  
    # SLOWMODE

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def slowmode(
        self,
        ctx,
        seconds: int
    ):

        await ctx.channel.edit(
            slowmode_delay=seconds
        )

        await ctx.send(
            embed=self.success(
                f"Slowmode set to {seconds}s."
            )
        )

    # TOPIC

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def topic(
        self,
        ctx,
        *,
        text
    ):

        await ctx.channel.edit(topic=text)

        await ctx.send(
            embed=self.success(
                f"Channel topic updated."
            )
        )

    # NSFW

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def nsfw(self, ctx):

        await ctx.channel.edit(
            nsfw=not ctx.channel.nsfw
        )

        await ctx.send(
            embed=self.success(
                f"NSFW: {ctx.channel.nsfw}"
            )
        )
        
# CHANNEL CREATE

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def channelcreate(
        self,
        ctx,
        *,
        name
    ):

        channel = await ctx.guild.create_text_channel(
            name=name
        )

        await ctx.send(
            embed=self.success(
                f"Created {channel.mention}"
            )
        )

    # CHANNEL DELETE

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def channeldelete(self, ctx):

        await ctx.send(
            embed=self.success(
                f"Deleting {ctx.channel.name}..."
            )
        )

        await ctx.channel.delete()

    # CATEGORY CREATE

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def categorycreate(
        self,
        ctx,
        *,
        name
    ):

        category = await ctx.guild.create_category(
            name=name
        )

        await ctx.send(
            embed=self.success(
                f"Category `{category.name}` created."
            )
        )

    # CATEGORY DELETE

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def categorydelete(
        self,
        ctx,
        category: discord.CategoryChannel
    ):

        name = category.name

        await category.delete()

        await ctx.send(
            embed=self.success(
                f"Category `{name}` deleted."
            )
        )

    # VC CREATE

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def vccreate(
        self,
        ctx,
        *,
        name
    ):

        vc = await ctx.guild.create_voice_channel(
            name=name
        )

        await ctx.send(
            embed=self.success(
                f"Voice Channel `{vc.name}` created."
            )
        )

    # VC DELETE

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def vcdelete(
        self,
        ctx,
        channel: discord.VoiceChannel
    ):

        name = channel.name

        await channel.delete()

        await ctx.send(
            embed=self.success(
                f"Voice Channel `{name}` deleted."
            )
        )

    # CLONE

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def clone(self, ctx):

        cloned = await ctx.channel.clone()

        await cloned.edit(
            position=ctx.channel.position + 1
        )

        await ctx.send(
            embed=self.success(
                f"Channel cloned: {cloned.mention}"
            )
        )
        
    # sticky msg

    @commands.hybrid_command(
        name="stickymsg",
        description="Set a sticky message."
    )
    @commands.has_permissions(manage_channels=True)
    async def stickymsg(
        self,
        ctx,
        channel: discord.TextChannel,
        *,
        message: str
    ):

        guild_id = str(ctx.guild.id)
        channel_id = str(channel.id)

        if guild_id not in self.data:
            self.data[guild_id] = {}

        self.data[guild_id][channel_id] = {
            "message": message,
            "last_message": None
        }

        self.save_data()

        embed = discord.Embed(
            description=(
                f"{Emojis.TICK} Sticky message has been set for {channel.mention}."
            ),
            color=0x2ECC71
        )

        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="unsticky",
        description="Remove a sticky message."
    )
    @commands.has_permissions(manage_channels=True)
    async def unsticky(
        self,
        ctx,
        channel: discord.TextChannel
    ):

        guild_id = str(ctx.guild.id)
        channel_id = str(channel.id)

        if (
            guild_id not in self.data
            or channel_id not in self.data[guild_id]
        ):
            embed = discord.Embed(
                description=(
                    f"{Emojis.CROSS} No sticky message found for {channel.mention}."
                ),
                color=0xE74C3C
            )

            return await ctx.send(embed=embed)

        last_message = self.data[guild_id][channel_id].get(
            "last_message"
        )

        if last_message:
            try:
                msg = await channel.fetch_message(last_message)
                await msg.delete()
            except:
                pass

        del self.data[guild_id][channel_id]

        if not self.data[guild_id]:
            del self.data[guild_id]

        self.save_data()

        embed = discord.Embed(
            description=(
                f"{Emojis.TICK} Sticky message removed from {channel.mention}."
            ),
            color=0x2ECC71
        )

        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="stickylist",
        description="View all sticky messages."
    )
    @commands.has_permissions(manage_channels=True)
    async def stickylist(self, ctx):

        guild_id = str(ctx.guild.id)

        if (
            guild_id not in self.data
            or not self.data[guild_id]
        ):
            embed = discord.Embed(
                description=f"{Emojis.CROSS} No sticky messages configured.",
                color=0xE74C3C
            )

            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title="📌 Sticky Messages",
            color=0x5865F2
        )

        for channel_id, data in self.data[guild_id].items():

            channel = ctx.guild.get_channel(
                int(channel_id)
            )

            if not channel:
                continue

            message = data["message"]

            if len(message) > 80:
                message = message[:77] + "..."

            embed.add_field(
                name=channel.mention,
                value=message,
                inline=False
            )

        embed.set_footer(
            text=f"Total Sticky Messages: {len(self.data[guild_id])}"
        )

        await ctx.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        if not message.guild:
            return

        guild_id = str(message.guild.id)
        channel_id = str(message.channel.id)

        if guild_id not in self.data:
            return

        if channel_id not in self.data[guild_id]:
            return

        sticky = self.data[guild_id][channel_id]

        last_message = sticky.get("last_message")

        if last_message:
            try:
                old = await message.channel.fetch_message(last_message)
                await old.delete()
            except:
                pass

        embed = discord.Embed(
            description=sticky["message"],
            color=0x5865F2
        )

        embed.set_footer(
            text="📌 Sticky Message"
        )

        msg = await message.channel.send(embed=embed)

        sticky["last_message"] = msg.id

        self.save_data()

    # PURGE
    
    @commands.hybrid_command(
        name="purge",
        description="Delete messages from the current channel."
    )
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):

        if amount < 1:
            return await ctx.send(
                embed=discord.Embed(
                    description=f"{Emojis.CROSS} Amount must be at least **1**.",
                    color=0xE74C3C
                ),
                delete_after=5
            )

        if amount > 50:
            amount = 50

        deleted = await ctx.channel.purge(limit=amount + 1)

        embed = discord.Embed(
            description=f"{Emojis.CLEANER} Deleted **{len(deleted)-1}** messages.",
            color=0x2ECC71
        )

        msg = await ctx.send(embed=embed)

        await msg.delete(delay=5)
    
    # NUKE

    @commands.hybrid_command()
    @commands.has_permissions(manage_channels=True)
    async def nuke(self, ctx):

        embed = discord.Embed(
            title=f"{Emojis.NUKE} Confirm Nuke",
            description=(
                "This will delete all messages "
                "in this channel.\n\n"
                "Are you sure?"
            ),
            color=0xe74c3c
        )

        await ctx.send(
            embed=embed,
            view=NukeConfirmView(
                ctx.author
            )
        )


async def setup(bot):
    await bot.add_cog(Channel(bot))