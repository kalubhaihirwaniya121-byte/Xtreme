import discord

# ==================================================

# CONFIRM VIEW (YES / NO)

# ==================================================

class ConfirmView(discord.ui.View):

    def __init__(self, author_id: int, timeout: int = 30):

        super().__init__(timeout=timeout)

        self.author_id = author_id

        self.value: bool | None = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:

        if interaction.user.id != self.author_id:

            await interaction.response.send_message(

                "❌ You cannot use these buttons.",

                ephemeral=True

            )

            return False

        return True

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)

    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.value = True

        await interaction.response.defer()

        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)

    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.value = False

        await interaction.response.defer()

        self.stop()

    async def on_timeout(self):

        self.value = None

        self.stop()

# ==================================================

# PAGINATOR VIEW (GENERIC EMBED PAGES)

# ==================================================

class PaginatorView(discord.ui.View):

    def __init__(self, pages: list[discord.Embed], author_id: int, timeout: int = 120):

        super().__init__(timeout=timeout)

        self.pages = pages

        self.index = 0

        self.author_id = author_id

        self._update_buttons()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:

        if interaction.user.id != self.author_id:

            await interaction.response.send_message(

                "❌ You cannot control this menu.",

                ephemeral=True

            )

            return False

        return True

    def _update_buttons(self):

        self.first.disabled = self.index == 0

        self.prev.disabled = self.index == 0

        self.next.disabled = self.index == len(self.pages) - 1

        self.last.disabled = self.index == len(self.pages) - 1

    async def update(self, interaction: discord.Interaction):

        self._update_buttons()

        await interaction.response.edit_message(

            embed=self.pages[self.index],

            view=self

        )

    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary)

    async def first(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.index = 0

        await self.update(interaction)

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.primary)

    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.index -= 1

        await self.update(interaction)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.primary)

    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.index += 1

        await self.update(interaction)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)

    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.index = len(self.pages) - 1

        await self.update(interaction)

    @discord.ui.button(emoji="❌", style=discord.ButtonStyle.danger)

    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.message.delete()

        self.stop()

    async def on_timeout(self):

        for child in self.children:

            child.disabled = True

# ==================================================

# HELP VIEW (SPECIFIC FOR HELP SYSTEM)

# ==================================================

class HelpView(discord.ui.View):

    def __init__(self, pages: list[discord.Embed], author_id: int, timeout: int = 120):

        super().__init__(timeout=timeout)

        self.pages = pages

        self.index = 0

        self.author_id = author_id

        self._update_buttons()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:

        if interaction.user.id != self.author_id:

            await interaction.response.send_message(

                "❌ This help menu is not for you.",

                ephemeral=True

            )

            return False

        return True

    def _update_buttons(self):

        self.first.disabled = self.index == 0

        self.prev.disabled = self.index == 0

        self.next.disabled = self.index == len(self.pages) - 1

        self.last.disabled = self.index == len(self.pages) - 1

    async def update(self, interaction: discord.Interaction):

        self._update_buttons()

        await interaction.response.edit_message(

            embed=self.pages[self.index],

            view=self

        )

    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary)

    async def first(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.index = 0

        await self.update(interaction)

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.primary)

    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.index -= 1

        await self.update(interaction)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.primary)

    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.index += 1

        await self.update(interaction)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)

    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):

        self.index = len(self.pages) - 1

        await self.update(interaction)

    @discord.ui.button(emoji="❌", style=discord.ButtonStyle.danger)

    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.message.delete()

        self.stop()

    async def on_timeout(self):

        for child in self.children:

            child.disabled = True