from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

import discord

# ==========================================================
# COLOR PALETTE CONSTANTS
# ==========================================================

NAMED_COLORS: Dict[str, int] = {
    "red": 0xFF0000,
    "green": 0x00FF00,
    "blue": 0x0000FF,
    "yellow": 0xFFFF00,
    "orange": 0xFFA500,
    "purple": 0x800080,
    "pink": 0xFFC0CB,
    "blurple": 0x5865F2,
    "grey": 0x99AAB5,
    "gray": 0x99AAB5,
    "black": 0x000000,
    "white": 0xFFFFFF,
    "gold": 0xFFD700,
    "teal": 0x008080,
    "dark_theme": 0x2B2D31,
}


# ==========================================================
# URL VALIDATION
# ==========================================================

def is_valid_url(value: Optional[str]) -> bool:
    """
    Returns True if the URL starts with http:// or https://.
    Returns False if value is empty or invalid.
    """
    if not value or not isinstance(value, str):
        return False

    return bool(re.match(r"^https?://", value.strip(), re.IGNORECASE))


# ==========================================================
# COLOR PARSER
# ==========================================================

def safe_int_color(value: Any) -> Optional[int]:
    """
    Converts a string or integer color representation into an integer color code.

    Supports:
        - Named colors (red, blurple, etc.)
        - Hexadecimal formats (#5865F2, 5865F2, 0x5865F2)
        - 3-digit hex shortcuts (#FFF -> #FFFFFF)
        - Raw integer representations (5793266)
    """
    if value is None:
        return None

    if isinstance(value, int):
        return value if 0 <= value <= 0xFFFFFF else None

    text = str(value).strip().lower()

    if not text:
        return None

    if text in NAMED_COLORS:
        return NAMED_COLORS[text]

    if text.startswith("#"):
        text = text[1:]

    if text.startswith("0x"):
        text = text[2:]

    if re.fullmatch(r"[0-9a-fA-F]{6}", text):
        return int(text, 16)

    if re.fullmatch(r"[0-9a-fA-F]{3}", text):
        return int("".join(c * 2 for c in text), 16)

    try:
        parsed_int = int(text)
        if 0 <= parsed_int <= 0xFFFFFF:
            return parsed_int
    except ValueError:
        pass

    return None


# ==========================================================
# EMBED BUILDER
# ==========================================================

def build_embed_from_data(
    embed_data: Dict[str, Any],
    extra: Optional[Dict[str, Any]] = None,
) -> discord.Embed:
    """
    Constructs a discord.Embed instance from a dictionary payload.
    """
    data = dict(embed_data or {})

    if extra:
        data.update(extra)

    embed = discord.Embed()

    if data.get("title"):
        embed.title = str(data["title"])

    if data.get("description"):
        embed.description = str(data["description"])

    color = data.get("color")
    if color is not None:
        parsed_color = safe_int_color(color)
        if parsed_color is not None:
            embed.color = discord.Color(parsed_color)

    if data.get("thumbnail_url") and is_valid_url(data["thumbnail_url"]):
        embed.set_thumbnail(url=data["thumbnail_url"])

    if data.get("image_url") and is_valid_url(data["image_url"]):
        embed.set_image(url=data["image_url"])

    if data.get("author_name"):
        author_kwargs: Dict[str, Any] = {"name": str(data["author_name"])}
        if data.get("author_url") and is_valid_url(data["author_url"]):
            author_kwargs["url"] = data["author_url"]
        if data.get("author_icon_url") and is_valid_url(data["author_icon_url"]):
            author_kwargs["icon_url"] = data["author_icon_url"]
        embed.set_author(**author_kwargs)

    if data.get("footer_text"):
        footer_kwargs: Dict[str, Any] = {"text": str(data["footer_text"])}
        if data.get("footer_icon_url") and is_valid_url(data["footer_icon_url"]):
            footer_kwargs["icon_url"] = data["footer_icon_url"]
        embed.set_footer(**footer_kwargs)

    if data.get("timestamp_enabled"):
        embed.timestamp = discord.utils.utcnow()

    for field in data.get("fields", []):
        embed.add_field(
            name=str(field.get("name") or "\u200b"),
            value=str(field.get("value") or "\u200b"),
            inline=bool(field.get("inline", False)),
        )

    if embed.is_empty():
        embed.description = "\u200b"

    return embed


# ==========================================================
# VALIDATOR
# ==========================================================

def validate_embed_payload(data: Dict[str, Any]) -> None:
    """
    Validates embed structural constraints against Discord's official limitations.
    Raises ValueError if constraints are violated.
    """
    title = str(data.get("title") or "")
    description = str(data.get("description") or "")
    author = str(data.get("author_name") or "")
    footer = str(data.get("footer_text") or "")
    fields = data.get("fields") or []

    if len(title) > 256:
        raise ValueError("Title exceeds 256 characters.")

    if len(description) > 4096:
        raise ValueError("Description exceeds 4096 characters.")

    if len(author) > 256:
        raise ValueError("Author name exceeds 256 characters.")

    if len(footer) > 2048:
        raise ValueError("Footer text exceeds 2048 characters.")

    if len(fields) > 25:
        raise ValueError("Maximum 25 fields allowed.")

    total_characters = len(title) + len(description) + len(author) + len(footer)

    for field in fields:
        name = str(field.get("name", ""))
        value = str(field.get("value", ""))

        if len(name) > 256:
            raise ValueError("Field name exceeds 256 characters.")

        if len(value) > 1024:
            raise ValueError("Field value exceeds 1024 characters.")

        total_characters += len(name) + len(value)

    if total_characters > 6000:
        raise ValueError("Embed total content exceeds Discord's 6000 character limit.")


# ==========================================================
# CONFIRM VIEW
# ==========================================================

class ConfirmView(discord.ui.View):
    """
    Generic confirmation view with Confirm and Cancel buttons.
    Restricted to interaction by the command owner.
    """

    def __init__(self, owner_id: int):
        super().__init__(timeout=60)
        self.owner_id = owner_id
        self.value: Optional[bool] = None
        self.message: Optional[discord.Message] = None

    def disable_items(self) -> None:
        """Disables all UI components attached to this view."""
        for item in self.children:
            if isinstance(item, (discord.ui.Button, discord.ui.Select)):
                item.disabled = True

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "You cannot use this menu.",
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self) -> None:
        self.disable_items()
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass
        self.stop()

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        self.value = True
        self.disable_items()
        await interaction.response.edit_message(view=self)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        self.value = False
        self.disable_items()
        await interaction.response.edit_message(view=self)
        self.stop()


# ==========================================================
# EMBED LIST VIEW
# ==========================================================

class EmbedListView(discord.ui.View):
    """
    Paginated view displaying saved embeds list.
    """

    def __init__(self, names: List[str], owner_id: int):
        super().__init__(timeout=120)
        self.names = names
        self.owner_id = owner_id
        self.page = 0
        self.per_page = 8
        self.message: Optional[discord.Message] = None

    def disable_items(self) -> None:
        """Disables all UI components attached to this view."""
        for item in self.children:
            if isinstance(item, (discord.ui.Button, discord.ui.Select)):
                item.disabled = True

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "You cannot use this menu.",
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self) -> None:
        self.disable_items()
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass
        self.stop()

    def build_embed(self) -> discord.Embed:
        start = self.page * self.per_page
        end = start + self.per_page
        current_page_items = self.names[start:end]

        embed = discord.Embed(
            title="Saved Embeds",
            color=0x5865F2,
        )

        if current_page_items:
            embed.description = "\n".join(f"• `{name}`" for name in current_page_items)
        else:
            embed.description = "No embeds found."

        total_pages = max(1, (len(self.names) + self.per_page - 1) // self.per_page)
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages}")

        return embed

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.secondary)
    async def previous_page(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        if self.page > 0:
            self.page -= 1

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self,
        )

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.secondary)
    async def next_page(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        total_pages = max(1, (len(self.names) + self.per_page - 1) // self.per_page)
        if self.page < total_pages - 1:
            self.page += 1

        await interaction.response.edit_message(
            embed=self.build_embed(),
            view=self,
        )


# ==========================================================
# FIELD SELECT COMPONENT
# ==========================================================

class FieldSelect(discord.ui.Select):
    """
    Dropdown component for selecting fields within an embed.
    """

    def __init__(self, fields: List[Dict[str, Any]], selected_id: Optional[int] = None):
        options: List[discord.SelectOption] = []

        for field in fields[:25]:
            field_id = field["id"]
            name = (str(field.get("name") or "Untitled"))[:25]
            val = (str(field.get("value") or "No content"))[:50]
            pos = field.get("position", 0) + 1
            is_inline = " [Inline]" if field.get("inline") else ""

            label = f"Field {pos}: {name}"[:100]
            description = f"{val}{is_inline}"[:100]

            options.append(
                discord.SelectOption(
                    label=label,
                    value=str(field_id),
                    description=description,
                    default=(field_id == selected_id),
                )
            )

        if not options:
            options.append(
                discord.SelectOption(
                    label="No fields available",
                    value="none",
                    description="Click 'Add Field' to create one",
                )
            )
            super().__init__(
                placeholder="Select a field to manage...",
                min_values=1,
                max_values=1,
                options=options,
                disabled=True,
                row=1,
            )
        else:
            super().__init__(
                placeholder="Select a field to manage...",
                min_values=1,
                max_values=1,
                options=options,
                disabled=False,
                row=1,
            )

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        view: EmbedEditorView = self.view
        selected_val = self.values[0]

        if selected_val != "none":
            view.selected_field_id = int(selected_val)
            await view.update_components()
            await interaction.response.edit_message(view=view)


# ==========================================================
# MODALS
# ==========================================================

class ContentModal(discord.ui.Modal, title="Edit Content"):
    """Modal for editing embed Title and Description."""

    title_input = discord.ui.TextInput(
        label="Title",
        style=discord.TextStyle.short,
        placeholder="Enter embed title...",
        required=False,
        max_length=256,
    )
    desc_input = discord.ui.TextInput(
        label="Description",
        style=discord.TextStyle.paragraph,
        placeholder="Enter embed description...",
        required=False,
        max_length=4096,
    )

    def __init__(
        self,
        view: EmbedEditorView,
        title_val: Optional[str] = None,
        desc_val: Optional[str] = None,
    ):
        super().__init__()
        self.view = view

        if title_val:
            self.title_input.default = title_val
        if desc_val:
            self.desc_input.default = desc_val

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            await self.view.controller.update_content(
                self.view.guild_id,
                self.view.embed_name,
                self.title_input.value,
                self.desc_input.value,
            )
            await self.view.refresh_preview(interaction)
        except Exception as exc:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"Failed to update content: {exc}",
                    ephemeral=True,
                )


class AppearanceModal(discord.ui.Modal, title="Edit Appearance"):
    """Modal for editing embed Color."""

    color_input = discord.ui.TextInput(
        label="Color (Name, Hex, or Decimal)",
        style=discord.TextStyle.short,
        placeholder="e.g. #5865F2, blurple, red, or 5793266",
        required=False,
        max_length=50,
    )

    def __init__(self, view: EmbedEditorView, color_val: Optional[Any] = None):
        super().__init__()
        self.view = view

        if color_val is not None:
            if isinstance(color_val, int):
                self.color_input.default = f"#{color_val:06X}"
            else:
                self.color_input.default = str(color_val)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            await self.view.controller.update_color(
                self.view.guild_id,
                self.view.embed_name,
                self.color_input.value,
            )
            await self.view.refresh_preview(interaction)
        except Exception as exc:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"Failed to update color: {exc}",
                    ephemeral=True,
                )


class MediaModal(discord.ui.Modal, title="Edit Media"):
    """Modal for editing Thumbnail URL and Main Image URL."""

    thumb_input = discord.ui.TextInput(
        label="Thumbnail URL",
        style=discord.TextStyle.short,
        placeholder="https://example.com/thumbnail.png",
        required=False,
        max_length=1000,
    )
    image_input = discord.ui.TextInput(
        label="Main Image URL",
        style=discord.TextStyle.short,
        placeholder="https://example.com/image.png",
        required=False,
        max_length=1000,
    )

    def __init__(
        self,
        view: EmbedEditorView,
        thumb_val: Optional[str] = None,
        img_val: Optional[str] = None,
    ):
        super().__init__()
        self.view = view

        if thumb_val:
            self.thumb_input.default = thumb_val
        if img_val:
            self.image_input.default = img_val

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            await self.view.controller.update_media(
                self.view.guild_id,
                self.view.embed_name,
                self.thumb_input.value,
                self.image_input.value,
            )
            await self.view.refresh_preview(interaction)
        except Exception as exc:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"Failed to update media: {exc}",
                    ephemeral=True,
                )


class AuthorModal(discord.ui.Modal, title="Edit Author"):
    """Modal for editing Author details."""

    name_input = discord.ui.TextInput(
        label="Author Name",
        style=discord.TextStyle.short,
        placeholder="Enter author name...",
        required=False,
        max_length=256,
    )
    url_input = discord.ui.TextInput(
        label="Author URL",
        style=discord.TextStyle.short,
        placeholder="https://example.com",
        required=False,
        max_length=1000,
    )
    icon_input = discord.ui.TextInput(
        label="Author Icon URL",
        style=discord.TextStyle.short,
        placeholder="https://example.com/icon.png",
        required=False,
        max_length=1000,
    )

    def __init__(
        self,
        view: EmbedEditorView,
        name_val: Optional[str] = None,
        url_val: Optional[str] = None,
        icon_val: Optional[str] = None,
    ):
        super().__init__()
        self.view = view

        if name_val:
            self.name_input.default = name_val
        if url_val:
            self.url_input.default = url_val
        if icon_val:
            self.icon_input.default = icon_val

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            await self.view.controller.update_author(
                self.view.guild_id,
                self.view.embed_name,
                self.name_input.value,
                self.url_input.value,
                self.icon_input.value,
            )
            await self.view.refresh_preview(interaction)
        except Exception as exc:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"Failed to update author: {exc}",
                    ephemeral=True,
                )


class FooterModal(discord.ui.Modal, title="Edit Footer"):
    """Modal for editing Footer details."""

    text_input = discord.ui.TextInput(
        label="Footer Text",
        style=discord.TextStyle.short,
        placeholder="Enter footer text...",
        required=False,
        max_length=2048,
    )
    icon_input = discord.ui.TextInput(
        label="Footer Icon URL",
        style=discord.TextStyle.short,
        placeholder="https://example.com/icon.png",
        required=False,
        max_length=1000,
    )

    def __init__(
        self,
        view: EmbedEditorView,
        text_val: Optional[str] = None,
        icon_val: Optional[str] = None,
    ):
        super().__init__()
        self.view = view

        if text_val:
            self.text_input.default = text_val
        if icon_val:
            self.icon_input.default = icon_val

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            await self.view.controller.update_footer(
                self.view.guild_id,
                self.view.embed_name,
                self.text_input.value,
                self.icon_input.value,
            )
            await self.view.refresh_preview(interaction)
        except Exception as exc:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"Failed to update footer: {exc}",
                    ephemeral=True,
                )


class FieldModal(discord.ui.Modal, title="Edit Field"):
    """Modal for adding or editing an embed Field."""

    name_input = discord.ui.TextInput(
        label="Field Name",
        style=discord.TextStyle.short,
        placeholder="Enter field name...",
        required=True,
        max_length=256,
    )
    value_input = discord.ui.TextInput(
        label="Field Value",
        style=discord.TextStyle.paragraph,
        placeholder="Enter field value...",
        required=True,
        max_length=1024,
    )
    inline_input = discord.ui.TextInput(
        label="Inline (true / false)",
        style=discord.TextStyle.short,
        placeholder="true or false",
        required=False,
        max_length=5,
        default="false",
    )

    def __init__(
        self,
        view: EmbedEditorView,
        field_id: Optional[int] = None,
        name_val: Optional[str] = None,
        value_val: Optional[str] = None,
        inline_val: bool = False,
    ):
        super().__init__()
        self.view = view
        self.field_id = field_id

        if field_id is not None:
            self.title = "Edit Field"
        else:
            self.title = "Add Field"

        if name_val:
            self.name_input.default = name_val
        if value_val:
            self.value_input.default = value_val
        self.inline_input.default = "true" if inline_val else "false"

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            if self.field_id is None:
                await self.view.controller.add_field(
                    self.view.guild_id,
                    self.view.embed_id,
                    self.name_input.value,
                    self.value_input.value,
                    self.inline_input.value,
                )
            else:
                await self.view.controller.edit_field(
                    self.view.guild_id,
                    self.view.embed_id,
                    self.field_id,
                    self.name_input.value,
                    self.value_input.value,
                    self.inline_input.value,
                )
            await self.view.refresh_preview(interaction)
        except Exception as exc:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"Failed to save field: {exc}",
                    ephemeral=True,
                )


# ==========================================================
# EMBED EDITOR VIEW
# ==========================================================

class EmbedEditorView(discord.ui.View):
    """
    Main Interactive View for managing and building embeds.
    """

    def __init__(
        self,
        controller: Any,
        guild_id: int,
        embed_id: int,
        embed_name: str,
        owner_id: int,
    ):
        super().__init__(timeout=300)
        self.controller = controller
        self.guild_id = guild_id
        self.embed_id = embed_id
        self.embed_name = embed_name
        self.owner_id = owner_id

        self.fields: List[Dict[str, Any]] = []
        self.selected_field_id: Optional[int] = None
        self.message: Optional[discord.Message] = None

    def disable_items(self) -> None:
        """Disables all UI components attached to this view."""
        for item in self.children:
            if isinstance(item, (discord.ui.Button, discord.ui.Select)):
                item.disabled = True

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "You cannot use this menu.",
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self) -> None:
        self.disable_items()
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass
        self.stop()

    async def load_fields(self) -> None:
        """Loads and synchronizes fields from the controller database."""
        self.fields = await self.controller.get_fields_for_embed(
            self.guild_id,
            self.embed_id,
        )
        valid_field_ids = [f["id"] for f in self.fields]
        if self.selected_field_id not in valid_field_ids:
            self.selected_field_id = valid_field_ids[0] if valid_field_ids else None

        await self.update_components()

    async def update_components(self) -> None:
        """Refreshes select menu and updates button state based on current fields."""
        for item in list(self.children):
            if isinstance(item, FieldSelect):
                self.remove_item(item)

        self.add_item(FieldSelect(self.fields, self.selected_field_id))

        has_selection = self.selected_field_id is not None
        self.btn_edit_field.disabled = not has_selection
        self.btn_delete_field.disabled = not has_selection
        self.btn_move_up.disabled = not has_selection
        self.btn_move_down.disabled = not has_selection
        self.btn_add_field.disabled = len(self.fields) >= 25

    async def refresh_preview(self, interaction: discord.Interaction) -> None:
        """Re-renders the embed preview and edits interaction message."""
        data = await self.controller.get_embed_data(self.guild_id, self.embed_name)
        if not data:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "Embed data could not be found.",
                    ephemeral=True,
                )
            return

        await self.load_fields()
        preview = await self.controller.render_embed_for_context(
            data,
            author=interaction.user,
            guild=interaction.guild,
            channel=interaction.channel,
            bot_user=interaction.client.user,
        )

        if interaction.response.is_done():
            if self.message:
                await self.message.edit(embed=preview, view=self)
            else:
                await interaction.followup.edit_message(
                    interaction.message.id,
                    embed=preview,
                    view=self,
                )
        else:
            await interaction.response.edit_message(embed=preview, view=self)

    # --- ROW 0: BASIC PROPERTIES ---

    @discord.ui.button(label="Content", style=discord.ButtonStyle.primary, row=0)
    async def btn_content(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        data = await self.controller.get_embed_data(self.guild_id, self.embed_name) or {}
        modal = ContentModal(
            view=self,
            title_val=data.get("title"),
            desc_val=data.get("description"),
        )
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Appearance", style=discord.ButtonStyle.primary, row=0)
    async def btn_appearance(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        data = await self.controller.get_embed_data(self.guild_id, self.embed_name) or {}
        modal = AppearanceModal(
            view=self,
            color_val=data.get("color"),
        )
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Media", style=discord.ButtonStyle.primary, row=0)
    async def btn_media(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        data = await self.controller.get_embed_data(self.guild_id, self.embed_name) or {}
        modal = MediaModal(
            view=self,
            thumb_val=data.get("thumbnail_url"),
            img_val=data.get("image_url"),
        )
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Author", style=discord.ButtonStyle.primary, row=0)
    async def btn_author(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        data = await self.controller.get_embed_data(self.guild_id, self.embed_name) or {}
        modal = AuthorModal(
            view=self,
            name_val=data.get("author_name"),
            url_val=data.get("author_url"),
            icon_val=data.get("author_icon_url"),
        )
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Footer", style=discord.ButtonStyle.primary, row=0)
    async def btn_footer(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        data = await self.controller.get_embed_data(self.guild_id, self.embed_name) or {}
        modal = FooterModal(
            view=self,
            text_val=data.get("footer_text"),
            icon_val=data.get("footer_icon_url"),
        )
        await interaction.response.send_modal(modal)

    # --- ROW 2: FIELD ACTIONS ---

    @discord.ui.button(label="Add Field", style=discord.ButtonStyle.success, row=2)
    async def btn_add_field(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        if len(self.fields) >= 25:
            await interaction.response.send_message(
                "Maximum limit of 25 fields reached.",
                ephemeral=True,
            )
            return

        modal = FieldModal(view=self)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Edit Field", style=discord.ButtonStyle.secondary, row=2)
    async def btn_edit_field(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        if self.selected_field_id is None:
            await interaction.response.send_message(
                "Please select a field to edit.",
                ephemeral=True,
            )
            return

        field = await self.controller.get_field_by_id(
            self.guild_id,
            self.embed_id,
            self.selected_field_id,
        )
        if not field:
            await interaction.response.send_message(
                "Selected field was not found.",
                ephemeral=True,
            )
            return

        modal = FieldModal(
            view=self,
            field_id=field["id"],
            name_val=field["name"],
            value_val=field["value"],
            inline_val=bool(field["inline"]),
        )
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Delete Field", style=discord.ButtonStyle.danger, row=2)
    async def btn_delete_field(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        if self.selected_field_id is None:
            await interaction.response.send_message(
                "Please select a field to delete.",
                ephemeral=True,
            )
            return

        await self.controller.remove_field(
            self.guild_id,
            self.embed_id,
            self.selected_field_id,
        )
        self.selected_field_id = None
        await self.refresh_preview(interaction)

    @discord.ui.button(label="Move Up", style=discord.ButtonStyle.secondary, row=2)
    async def btn_move_up(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        if self.selected_field_id is None:
            await interaction.response.send_message(
                "Please select a field first.",
                ephemeral=True,
            )
            return

        await self.controller.move_field(
            self.guild_id,
            self.embed_id,
            self.selected_field_id,
            up=True,
        )
        await self.refresh_preview(interaction)

    @discord.ui.button(label="Move Down", style=discord.ButtonStyle.secondary, row=2)
    async def btn_move_down(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        if self.selected_field_id is None:
            await interaction.response.send_message(
                "Please select a field first.",
                ephemeral=True,
            )
            return

        await self.controller.move_field(
            self.guild_id,
            self.embed_id,
            self.selected_field_id,
            up=False,
        )
        await self.refresh_preview(interaction)

    # --- ROW 3: EXTRA TOGGLES ---

    @discord.ui.button(label="Toggle Timestamp", style=discord.ButtonStyle.secondary, row=3)
    async def btn_timestamp(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ) -> None:
        await self.controller.toggle_timestamp(self.guild_id, self.embed_name)
        await self.refresh_preview(interaction)