import random
import discord

from discord.ui import View, Button

from utils.emojis import Emojis


class ShipView(View):
    def __init__(
        self,
        bot,
        user1: discord.Member,
        user2: discord.Member,
        ship_callback
    ):
        super().__init__(timeout=180)

        self.bot = bot

        self.user1 = user1
        self.user2 = user2

        self.ship_callback = ship_callback
        

    @discord.ui.button(
        label="Random",
        emoji="🎲",
        style=discord.ButtonStyle.secondary
    )
    async def random_ship(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        user = interaction.user

        members = [
            m for m in interaction.guild.members
            if not m.bot and m.id != user.id
        ]

        if not members:
            return await interaction.response.send_message(
                f"{Emojis.CROSS} No members available.",
                ephemeral=True
            )

        partner = random.choice(members)

        self.user1 = user
        self.user2 = partner

        await self.ship_callback(
            interaction,
            user,
            partner,
            self
        )
        
    @discord.ui.button(
        label="Love",
        emoji="❤️",
        style=discord.ButtonStyle.success
    )
    async def love(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        await self.ship_callback(
            interaction,
            self.user1,
            self.user2,
            self,
            "love"
        )
        
    @discord.ui.button(
        label="Hate",
        emoji="💔",
        style=discord.ButtonStyle.danger
    )
    async def hate(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        await self.ship_callback(
            interaction,
            self.user1,
            self.user2,
            self,
            "hate"
        )
