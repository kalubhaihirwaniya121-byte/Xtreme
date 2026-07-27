from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

import discord


def is_valid_url(value: str) -> bool:
    return bool(value) and re.match(r"^https?://", value) is not None


NAMED_COLORS = {
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
}


def safe_int_color(value: str) -> Optional[int]:
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    if text in NAMED_COLORS:
        return NAMED_COLORS[text]
    if text.startswith("#"):
        text = text[1:]
    if text.startswith("0x") or text.startswith("0X"):
        text = text[2:]
    if re.fullmatch(r"[0-9A-Fa-f]{6}", text):
        return int(text, 16)
    if re.fullmatch(r"[0-9A-Fa-f]{3}", text):
        return int("".join(c * 2 for c in text), 16)
    try:
        return int(text)
    except ValueError:
        return None


def build_embed_from_data(embed_data: Dict[str, Any], extra: Optional[Dict[str, Any]] = None) -> discord.Embed:
    data = dict(embed_data or {})
    if extra:
        data.update(extra)

    embed = discord.Embed()
    title = data.get("title")
    description = data.get("description")
    if title:
        embed.title = title
    if description:
        embed.description = description

    color = data.get("color")
    if color is not None:
        try:
            embed.color = int(color)
        except (TypeError, ValueError):
            embed.color = None
    if data.get("thumbnail_url"):
        embed.set_thumbnail(url=data["thumbnail_url"])
    if data.get("image_url"):
        embed.set_image(url=data["image_url"])
    if data.get("author_name"):
        embed.set_author(
            name=str(data["author_name"]),
            url=data.get("author_url"),
            icon_url=data.get("author_icon_url")
        )
    if data.get("footer_text"):
        embed.set_footer(
            text=str(data["footer_text"]),
            icon_url=data.get("footer_icon_url")
        )
    if data.get("timestamp_enabled"):
        embed.timestamp = discord.utils.utcnow()

    for field in data.get("fields", []) or []:
        name = str(field.get("name") or "\u200b")
        value = str(field.get("value") or "\u200b")
        inline = bool(field.get("inline", False))

        embed.add_field(
            name=name,
            value=value,
            inline=inline
        )

    if embed.is_empty():
        embed.description = "\u200b"
    return embed


def validate_embed_payload(data: Dict[str, Any]) -> None:
    title = data.get("title") or ""
    description = data.get("description") or ""
    author_name = data.get("author_name") or ""
    footer_text = data.get("footer_text") or ""
    fields = data.get("fields") or []

    if len(title) > 256:
        raise ValueError("Title exceeds the 256-character limit.")
    if len(description) > 4096:
        raise ValueError("Description exceeds the 4096-character limit.")
    if len(author_name) > 256:
        raise ValueError("Author name exceeds the 256-character limit.")
    if len(footer_text) > 2048:
        raise ValueError("Footer text exceeds the 2048-character limit.")
    if len(fields) > 25:
        raise ValueError("An embed may have at most 25 fields.")

    total_text = len(title) + len(description) + len(author_name) + len(footer_text)
    for field in fields:
        field_name = str(field.get("name", ""))
        field_value = str(field.get("value", ""))
        if len(field_name) > 256:
            raise ValueError("Field name exceeds the 256-character limit.")
        if len(field_value) > 1024:
            raise ValueError("Field value exceeds the 1024-character limit.")
        total_text += len(field_name) + len(field_value)
    if total_text > 6000:
        raise ValueError("Embed exceeds the 6000-character total content limit.")


class ConfirmView(discord.ui.View):
    def __init__(self, owner_id: int):
        super().__init__(timeout=60)
        self.owner_id = owner_id
        self.value: Optional[bool] = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("You cannot use this menu.", ephemeral=True)
            return False
        return True

    async def on_timeout(self) -> None:
        self.disable_all_items()
        self.stop()

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.value = True
        self.disable_all_items()
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.value = False
        self.disable_all_items()
        self.stop()
        await interaction.response.defer()


class EmbedListView(discord.ui.View):
    def __init__(self, names: List[str], owner_id: int):
        super().__init__(timeout=120)
        self.names = names
        self.owner_id = owner_id
        self.message: Optional[discord.Message] = None
        self.page = 0
        self.per_page = 8

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("You cannot use this menu.", ephemeral=True)
            return False
        return True

    async def on_timeout(self) -> None:
        self.disable_all_items()
        self.stop()

    def build_embed(self) -> discord.Embed:
        start = self.page * self.per_page
        end = start + self.per_page
        chunk = self.names[start:end]
        description = "\n".join(f"• {name}" for name in chunk)
        embed = discord.Embed(title="Saved embeds", description=description or "No embeds on this page.", color=0x5865F2)
        embed.set_footer(text=f"Page {self.page + 1}/{max(1, (len(self.names) + self.per_page - 1) // self.per_page)}")
        return embed

    @discord.ui.button(label="◀", style=discord.ButtonStyle.blurple)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("You cannot use this menu.", ephemeral=True)
        if self.page > 0:
            self.page -= 1
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message("You cannot use this menu.", ephemeral=True)
        max_pages = max(1, (len(self.names) + self.per_page - 1) // self.per_page)
        if self.page < max_pages - 1:
            self.page += 1
        await interaction.response.edit_message(embed=self.build_embed(), view=self)


class FieldSelect(discord.ui.Select):
    def __init__(self, options: List[discord.SelectOption]):
        super().__init__(placeholder="Select a field to manage", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction) -> None:
        view = self.view
        if not isinstance(view, EmbedEditorView):
            return
        value = self.values[0]
        if value.isdigit():
            view.selected_field_id = int(value)
            await interaction.response.send_message(f"Selected field {self.values[0]}.", ephemeral=True)
        else:
            view.selected_field_id = None
            await interaction.response.send_message("No field selected.", ephemeral=True)


class ContentModal(discord.ui.Modal, title="Embed Content"):
    def __init__(self, controller: Any, guild_id: int, embed_name: str, parent_view: Optional["EmbedEditorView"] = None):
        super().__init__()
        self.controller = controller
        self.guild_id = guild_id
        self.embed_name = embed_name
        self.parent_view = parent_view
        self.title = discord.ui.TextInput(label="Title", required=False, max_length=256)
        self.description = discord.ui.TextInput(label="Description", required=False, style=discord.TextStyle.paragraph, max_length=4096)
        self.add_item(self.title)
        self.add_item(self.description)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            await self.controller.update_content(self.guild_id, self.embed_name, self.title.value, self.description.value)
            if self.parent_view is not None:
                await self.parent_view.load_fields()
                await self.parent_view.refresh_embed_message()
            await interaction.response.send_message("Content updated.", ephemeral=True)
        except ValueError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)


class AppearanceModal(discord.ui.Modal, title="Embed Appearance"):
    def __init__(self, controller: Any, guild_id: int, embed_name: str, parent_view: Optional["EmbedEditorView"] = None):
        super().__init__()
        self.controller = controller
        self.guild_id = guild_id
        self.embed_name = embed_name
        self.parent_view = parent_view
        self.color = discord.ui.TextInput(label="Color", required=False, placeholder="#5865F2")
        self.add_item(self.color)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            await self.controller.update_color(self.guild_id, self.embed_name, self.color.value)
            if self.parent_view is not None:
                await self.parent_view.load_fields()
                await self.parent_view.refresh_embed_message()
            await interaction.response.send_message("Color updated.", ephemeral=True)
        except ValueError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)


class MediaModal(discord.ui.Modal, title="Embed Media"):
    def __init__(self, controller: Any, guild_id: int, embed_name: str, parent_view: Optional["EmbedEditorView"] = None):
        super().__init__()
        self.controller = controller
        self.guild_id = guild_id
        self.embed_name = embed_name
        self.parent_view = parent_view
        self.thumbnail = discord.ui.TextInput(label="Thumbnail URL", required=False, placeholder="https://...")
        self.image = discord.ui.TextInput(label="Image URL", required=False, placeholder="https://...")
        self.add_item(self.thumbnail)
        self.add_item(self.image)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            await self.controller.update_media(self.guild_id, self.embed_name, self.thumbnail.value, self.image.value)
            if self.parent_view is not None:
                await self.parent_view.load_fields()
                await self.parent_view.refresh_embed_message()
            await interaction.response.send_message("Media updated.", ephemeral=True)
        except ValueError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)


class AuthorModal(discord.ui.Modal, title="Embed Author"):
    def __init__(self, controller: Any, guild_id: int, embed_name: str, parent_view: Optional["EmbedEditorView"] = None):
        super().__init__()
        self.controller = controller
        self.guild_id = guild_id
        self.embed_name = embed_name
        self.parent_view = parent_view
        self.name = discord.ui.TextInput(label="Author Name", required=False, max_length=256)
        self.url = discord.ui.TextInput(label="Author URL", required=False, placeholder="https://...")
        self.icon = discord.ui.TextInput(label="Author Icon URL", required=False, placeholder="https://...")
        self.add_item(self.name)
        self.add_item(self.url)
        self.add_item(self.icon)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            await self.controller.update_author(self.guild_id, self.embed_name, self.name.value, self.url.value, self.icon.value)
            if self.parent_view is not None:
                await self.parent_view.load_fields()
                await self.parent_view.refresh_embed_message()
            await interaction.response.send_message("Author updated.", ephemeral=True)
        except ValueError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)


class FooterModal(discord.ui.Modal, title="Embed Footer"):
    def __init__(self, controller: Any, guild_id: int, embed_name: str, parent_view: Optional["EmbedEditorView"] = None):
        super().__init__()
        self.controller = controller
        self.guild_id = guild_id
        self.embed_name = embed_name
        self.parent_view = parent_view
        self.text = discord.ui.TextInput(label="Footer Text", required=False, max_length=2048)
        self.icon = discord.ui.TextInput(label="Footer Icon URL", required=False, placeholder="https://...")
        self.add_item(self.text)
        self.add_item(self.icon)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            await self.controller.update_footer(self.guild_id, self.embed_name, self.text.value, self.icon.value)
            if self.parent_view is not None:
                await self.parent_view.load_fields()
                await self.parent_view.refresh_embed_message()
            await interaction.response.send_message("Footer updated.", ephemeral=True)
        except ValueError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)


class FieldModal(discord.ui.Modal, title="Embed Field"):
    def __init__(self, controller: Any, guild_id: int, embed_name: str, embed_id: int, field_id: Optional[int] = None, default_name: str = "", default_value: str = "", default_inline: str = "yes", parent_view: Optional["EmbedEditorView"] = None):
        super().__init__()
        self.controller = controller
        self.guild_id = guild_id
        self.embed_name = embed_name
        self.embed_id = embed_id
        self.field_id = field_id
        self.parent_view = parent_view
        self.name = discord.ui.TextInput(label="Field Name", required=True, max_length=256, default=default_name)
        self.value = discord.ui.TextInput(label="Field Value", required=True, style=discord.TextStyle.paragraph, max_length=1024, default=default_value)
        self.inline = discord.ui.TextInput(label="Inline (yes/no)", required=False, placeholder="yes", default=default_inline)
        self.add_item(self.name)
        self.add_item(self.value)
        self.add_item(self.inline)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            if self.field_id is None:
                await self.controller.add_field(self.guild_id, self.embed_id, self.name.value, self.value.value, self.inline.value)
            else:
                await self.controller.edit_field(self.guild_id, self.embed_id, self.field_id, self.name.value, self.value.value, self.inline.value)
            if self.parent_view is not None:
                await self.parent_view.load_fields()
                await self.parent_view.refresh_embed_message()
            await interaction.response.send_message("Field saved.", ephemeral=True)
        except ValueError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)


class EmbedEditorView(discord.ui.View):
    def __init__(self, controller: Any, guild_id: int, embed_id: int, embed_name: str, owner_id: int):
        super().__init__(timeout=180)
        self.controller = controller
        self.guild_id = guild_id
        self.embed_id = embed_id
        self.embed_name = embed_name
        self.owner_id = owner_id
        self.message: Optional[discord.Message] = None
        self.selected_field_id: Optional[int] = None
        self.field_select = FieldSelect(options=[discord.SelectOption(label="No fields available", value="-", description="Add a field to manage it.")])
        self.add_item(self.field_select)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("You cannot use this editor.", ephemeral=True)
            return False
        return True

    async def load_fields(self) -> None:
        fields = await self.controller.get_fields_for_embed(self.guild_id, self.embed_id)
        self.field_select.options = [
            discord.SelectOption(label=f"{idx + 1}. {field['name']}", value=str(field["id"]), description=(field["value"][:50] + "...") if len(field["value"]) > 50 else field["value"])
            for idx, field in enumerate(fields)
        ] or [discord.SelectOption(label="No fields available", value="-", description="Add a field to manage it.")]
        if self.selected_field_id is not None and not any(option.value == str(self.selected_field_id) for option in self.field_select.options):
            self.selected_field_id = None

    async def refresh_embed_message(self) -> None:
        if self.message is None:
            return
        data = await self.controller.get_embed_data(self.guild_id, self.embed_name)
        if not data:
            return
        preview = await self.controller.render_embed_for_context(
            data,
            channel=None,
            channel=None,
            author=(
                self.message.guild.get_member(self.owner_id)
                if self.message.guild
                else None
            ),
            guild=self.message.guild,
            channel=None,
            bot_user=self.message.client.user,
        )
        try:
            await self.message.edit(embed=preview, view=self)
        except discord.HTTPException:
            pass

    async def _refresh_message(self, interaction: discord.Interaction) -> None:
        await self.refresh_embed_message()
        if self.message is not None:
            await interaction.response.defer()
        else:
            await interaction.response.send_message("Editor refreshed.", ephemeral=True)

    @discord.ui.button(label="Content", style=discord.ButtonStyle.blurple, custom_id="embed_editor_content")
    async def content_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_modal(ContentModal(self.controller, self.guild_id, self.embed_name, parent_view=self))

    @discord.ui.button(label="Appearance", style=discord.ButtonStyle.blurple, custom_id="embed_editor_appearance")
    async def appearance_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_modal(AppearanceModal(self.controller, self.guild_id, self.embed_name, parent_view=self))

    @discord.ui.button(label="Media", style=discord.ButtonStyle.blurple, custom_id="embed_editor_media")
    async def media_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_modal(MediaModal(self.controller, self.guild_id, self.embed_name, parent_view=self))

    @discord.ui.button(label="Author", style=discord.ButtonStyle.blurple, custom_id="embed_editor_author")
    async def author_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_modal(AuthorModal(self.controller, self.guild_id, self.embed_name, parent_view=self))

    @discord.ui.button(label="Footer", style=discord.ButtonStyle.blurple, custom_id="embed_editor_footer")
    async def footer_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_modal(FooterModal(self.controller, self.guild_id, self.embed_name, parent_view=self))

    @discord.ui.button(label="Timestamp", style=discord.ButtonStyle.green, custom_id="embed_editor_timestamp")
    async def timestamp_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self.controller.toggle_timestamp(self.guild_id, self.embed_name)
        await self.load_fields()
        await self.refresh_embed_message()
        await interaction.response.send_message("Timestamp toggled.", ephemeral=True)

    @discord.ui.button(label="Add Field", style=discord.ButtonStyle.green, custom_id="embed_editor_add_field")
    async def add_field_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_modal(FieldModal(self.controller, self.guild_id, self.embed_name, self.embed_id, parent_view=self))

    @discord.ui.button(label="Edit Field", style=discord.ButtonStyle.gray, custom_id="embed_editor_edit_field")
    async def edit_field_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if self.selected_field_id is None:
            return await interaction.response.send_message("Select a field first.", ephemeral=True)
        field = await self.controller.get_field_by_id(self.guild_id, self.embed_id, self.selected_field_id)
        if not field:
            return await interaction.response.send_message("Field not found.", ephemeral=True)
        await interaction.response.send_modal(FieldModal(
            self.controller,
            self.guild_id,
            self.embed_name,
            self.embed_id,
            field_id=field["id"],
            default_name=field["name"],
            default_value=field["value"],
            default_inline="yes" if field["inline"] else "no",
            parent_view=self,
        ))

    @discord.ui.button(label="Delete Field", style=discord.ButtonStyle.red, custom_id="embed_editor_delete_field")
    async def delete_field_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if self.selected_field_id is None:
            return await interaction.response.send_message("Select a field first.", ephemeral=True)
        await self.controller.remove_field(self.guild_id, self.embed_id, self.selected_field_id)
        self.selected_field_id = None
        await self.load_fields()
        await self.refresh_embed_message()
        await interaction.response.send_message("Field deleted.", ephemeral=True)

    @discord.ui.button(label="Move Up", style=discord.ButtonStyle.gray, custom_id="embed_editor_move_up")
    async def move_up_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if self.selected_field_id is None:
            return await interaction.response.send_message("Select a field first.", ephemeral=True)
        await self.controller.move_field(self.guild_id, self.embed_id, self.selected_field_id, up=True)
        await self.load_fields()
        await self.refresh_embed_message()
        await interaction.response.send_message("Field moved up.", ephemeral=True)

    @discord.ui.button(label="Move Down", style=discord.ButtonStyle.gray, custom_id="embed_editor_move_down")
    async def move_down_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if self.selected_field_id is None:
            return await interaction.response.send_message("Select a field first.", ephemeral=True)
        await self.controller.move_field(self.guild_id, self.embed_id, self.selected_field_id, up=False)
        await self.load_fields()
        await self.refresh_embed_message()
        await interaction.response.send_message("Field moved down.", ephemeral=True)

    @discord.ui.button(label="Refresh", style=discord.ButtonStyle.grey, custom_id="embed_editor_refresh")
    async def refresh_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self._refresh_message(interaction)

    async def on_timeout(self) -> None:
        self.disable_all_items()
        self.stop()
