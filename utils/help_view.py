import discord
from discord.ui import (
    LayoutView,
    Button,
    Select,
    Separator,
    Container,
    TextDisplay,
    ActionRow,
    Section,
    Thumbnail,
)
from utils.emojis import Emojis
from utils.help_data import HELP_CATEGORIES


class HelpView(LayoutView):
    def __init__(self, author: discord.Member):
        super().__init__(timeout=300)

        self.author = author
        self.current_page = 0
        self.categories = list(HELP_CATEGORIES.keys())
        self.total_pages = len(self.categories)

        self.build_home()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                f"{Emojis.CROSS} You cannot use this menu.",
                ephemeral=True
            )
            return False
        return True

    # ---------------------------------------------------
    # HOME PAGE
    # ---------------------------------------------------

    def build_home(self):
        self.current_page = 0
        self.clear_items()

        container = Container()

        avatar_url = (
            self.author.guild.me.display_avatar.url
            if self.author.guild and self.author.guild.me
            else None
        )

        if avatar_url:
            header = Section(
                TextDisplay(
                    "# Xtreme\n"
                    "### A Premium Bot\n\n"
                    "Browse commands using the category selector below."
                ),
                accessory=Thumbnail(avatar_url)
            )

            container.add_item(header)

        else:
            container.add_item(
                TextDisplay(
                    "# Xtreme\n"
                    "### A Premium Bot\n\n"
                    "Browse commands using the category selector below."
                )
            )

        container.add_item(Separator())

        category_text = ""

        for name, data in HELP_CATEGORIES.items():
            category_text += f"{data['emoji']} **{name}**\n"

        container.add_item(
            TextDisplay(category_text)
        )

        container.add_item(Separator())

        container.add_item(
            TextDisplay(
                f"**Categories:** {self.total_pages}"
            )
        )

        self.add_item(container)

        self.add_item(
            ActionRow(
                CategorySelect(self)
            )
        )

        self.add_item(
            ActionRow(
                PreviousButton(self),
                HomeButton(self),
                NextButton(self)
            )
        )

    # ---------------------------------------------------
    # CATEGORY PAGE
    # ---------------------------------------------------

    def build_category(self, index: int):
        self.current_page = index + 1
        self.clear_items()

        category = self.categories[index]
        data = HELP_CATEGORIES[category]

        container = Container()

        container.add_item(
            TextDisplay(
                f"# {data['emoji']} {category}"
            )
        )

        container.add_item(Separator())

        for item in data.get("components", []):
            item_type = item.get("type")

            if item_type == "text":
                container.add_item(
                    TextDisplay(item.get("content", ""))
                )

            elif item_type == "separator":
                container.add_item(
                    Separator()
                )

        container.add_item(Separator())

        container.add_item(
            TextDisplay(
                f"**Page:** {index + 1}/{self.total_pages}"
            )
        )

        self.add_item(container)

        self.add_item(
            ActionRow(
                CategorySelect(self)
            )
        )

        self.add_item(
            ActionRow(
                PreviousButton(self),
                HomeButton(self),
                NextButton(self)
            )
        )

    async def update_message(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=self)


# =========================================================
# DROPDOWN
# =========================================================

class CategorySelect(Select):
    def __init__(self, view: HelpView):
        options = []

        for name, data in HELP_CATEGORIES.items():
            options.append(
                discord.SelectOption(
                    label=name,
                    emoji=data["emoji"]
                )
            )

        super().__init__(
            placeholder="Explore Xtreme Feutures...",
            options=options
        )

        self.help_view = view

    async def callback(self, interaction: discord.Interaction):
        selected = self.values[0] if self.values else None
        if selected is None:
            await interaction.response.defer()
            return

        index = self.help_view.categories.index(selected)
        self.help_view.build_category(index)
        await self.help_view.update_message(interaction)


# =========================================================
# BUTTONS
# =========================================================

class PreviousButton(Button):
    def __init__(self, view: HelpView):
        super().__init__(
            emoji=f"{Emojis.LEFT}",
            style=discord.ButtonStyle.secondary
        )
        self.help_view = view

    async def callback(self, interaction: discord.Interaction):
        if self.help_view.current_page <= 1:
            self.help_view.build_home()
        else:
            self.help_view.build_category(self.help_view.current_page - 2)

        await self.help_view.update_message(interaction)


class HomeButton(Button):
    def __init__(self, view: HelpView):
        super().__init__(
            emoji=f"{Emojis.HOME}",
            style=discord.ButtonStyle.primary
        )
        self.help_view = view

    async def callback(self, interaction: discord.Interaction):
        self.help_view.build_home()
        await self.help_view.update_message(interaction)


class NextButton(Button):
    def __init__(self, view: HelpView):
        super().__init__(
            emoji=f"{Emojis.MARK}",
            style=discord.ButtonStyle.secondary
        )
        self.help_view = view

    async def callback(self, interaction: discord.Interaction):
        if self.help_view.current_page == 0:
            self.help_view.build_category(0)
        elif self.help_view.current_page < self.help_view.total_pages:
            self.help_view.build_category(self.help_view.current_page)
        else:
            self.help_view.build_home()

        await self.help_view.update_message(interaction)
