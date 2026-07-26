import discord

from discord.ui import (
    View,
    Button,
    Modal,
    TextInput
)

from utils.storage import load_json, save_json
from utils.emojis import Emojis


class LoveLetterView(View):

    def __init__(
        self,
        bot,
        sender,
        receiver,
        letter,
        regenerate_callback
    ):

        super().__init__(
            timeout=300
        )

        self.bot = bot

        self.sender = sender

        self.receiver = receiver

        self.letter = letter

        self.regenerate_callback = regenerate_callback

        self.data = load_json(
            "loveletter.json"
        )

        if "blocked" not in self.data:

            self.data["blocked"] = {}

    def save(self):

        save_json(
            "loveletter.json",
            self.data
        )
        
    @discord.ui.button(
        label="Send",
        emoji="📩",
        style=discord.ButtonStyle.success
    )
    async def send(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if interaction.user.id != self.sender.id:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} This button isn't for you.",
                ephemeral=True
            )

        blocked = self.data["blocked"].get(
            str(self.receiver.id),
            []
        )

        if self.sender.id in blocked:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} This user isn't accepting your letters.",
                ephemeral=True
            )

        embed = discord.Embed(

            title="💌 You Received a Love Letter",

            description=self.letter,

            color=0xFF69B4

        )

        embed.add_field(
            name="From",
            value=self.sender.mention,
            inline=False
        )

        embed.set_footer(
            text="Sent using Xtreme ❤️"
        )

        try:

            await self.receiver.send(

                embed=embed,

                view=ReplyView(
                    self.sender,
                    self.receiver,
                    self.letter
                )

            )

        except discord.Forbidden:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} I couldn't send the letter because their DMs are closed.",
                ephemeral=True
            )

        success = discord.Embed(

            description=(
                f"{Emojis.TICK} Your love letter has been delivered to "
                f"{self.receiver.mention} ❤️"
            ),

            color=0x2ECC71

        )

        await interaction.response.edit_message(
            embed=success,
            view=None
        )
        
    @discord.ui.button(
        label="Regenerate",
        emoji="🔄",
        style=discord.ButtonStyle.primary
    )
    async def regenerate(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if interaction.user.id != self.sender.id:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} This button isn't for you.",
                ephemeral=True
            )

        await self.regenerate_callback(
            interaction
        )

    @discord.ui.button(
        label="Cancel",
        emoji="❌",
        style=discord.ButtonStyle.danger
    )
    async def cancel(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if interaction.user.id != self.sender.id:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} This button isn't for you.",
                ephemeral=True
            )

        embed = discord.Embed(

            description=(
                f"{Emojis.CROSS} Love letter cancelled."
            ),

            color=0xE74C3C

        )

        embed.set_footer(
            text="Thanks for using Xtreme"
        )

        await interaction.response.edit_message(

            embed=embed,

            view=None

        )
        
class ReplyView(View):

    def __init__(
        self,
        sender,
        receiver,
        letter
    ):

        super().__init__(
            timeout=None
        )

        self.sender = sender

        self.receiver = receiver

        self.letter = letter

        self.data = load_json(
            "loveletter.json"
        )

        if "blocked" not in self.data:

            self.data["blocked"] = {}

    def save(self):

        save_json(
            "loveletter.json",
            self.data
        )

    @discord.ui.button(
        label="Reply",
        emoji="💬",
        style=discord.ButtonStyle.primary
    )
    async def reply(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if interaction.user.id != self.receiver.id:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} This button isn't for you.",
                ephemeral=True
            )

        await interaction.response.send_modal(

            ReplyModal(
                self.sender,
                self.receiver
            )

        )

    @discord.ui.button(
        label="Accept",
        emoji="❤️",
        style=discord.ButtonStyle.success
    )
    async def accept(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if interaction.user.id != self.receiver.id:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} This button isn't for you.",
                ephemeral=True
            )

        await self.sender.send(
            f"❤️ **{self.receiver}** accepted your love letter."
        )

        await interaction.response.send_message(
            "❤️ You accepted the love letter.",
            ephemeral=True
        )

    @discord.ui.button(
        label="Thanks",
        emoji="🙏",
        style=discord.ButtonStyle.secondary
    )
    async def thanks(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if interaction.user.id != self.receiver.id:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} This button isn't for you.",
                ephemeral=True
            )

        await self.sender.send(
            f"🙏 **{self.receiver}** says thanks for your love letter!"
        )

        await interaction.response.send_message(
            "🙏 Your thanks has been sent.",
            ephemeral=True
        )
        
    @discord.ui.button(
        label="Block Sender",
        emoji="🚫",
        style=discord.ButtonStyle.danger
    )
    async def block(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if interaction.user.id != self.receiver.id:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} This button isn't for you.",
                ephemeral=True
            )

        blocked = self.data["blocked"].setdefault(
            str(self.receiver.id),
            []
        )

        if self.sender.id not in blocked:

            blocked.append(
                self.sender.id
            )

            self.save()

        await interaction.response.send_message(
            "🚫 You will no longer receive love letters from this user.",
            ephemeral=True
        )


class ReplyModal(Modal):

    def __init__(
        self,
        sender,
        receiver
    ):

        super().__init__(
            title="Reply to Love Letter"
        )

        self.sender = sender

        self.receiver = receiver

        self.reply = TextInput(
            label="Your Reply",
            placeholder="Write your reply...",
            required=True,
            max_length=1000
        )

        self.add_item(
            self.reply
        )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        embed = discord.Embed(

            title="💌 Love Letter Reply",

            description=self.reply.value,

            color=0xFF69B4

        )

        embed.add_field(
            name="From",
            value=self.receiver.mention,
            inline=False
        )

        embed.set_footer(
            text="Sent using Xtreme ❤️"
        )

        try:

            await self.sender.send(
                embed=embed
            )

        except discord.Forbidden:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} I couldn't deliver your reply.",
                ephemeral=True
            )

        await interaction.response.send_message(
            "✅ Your reply has been delivered.",
            ephemeral=True
        )