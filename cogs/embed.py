from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiosqlite
import discord
from discord.ext import commands

from utils import embed_utils
from utils.emojis import Emojis


def now_iso() -> str:
    return datetime.utcnow().isoformat()


def normalize_name(name: str) -> str:
    return (name or "").strip().lower()


class EmbedCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_path = os.path.join("data", "embeds.db")
        self.db: Optional[aiosqlite.Connection] = None
        self._init_task = bot.loop.create_task(self._init_db())

    async def _init_db(self) -> None:
        os.makedirs("data", exist_ok=True)
        self.db = await aiosqlite.connect(self.db_path)
        self.db.row_factory = aiosqlite.Row
        await self.db.execute("PRAGMA foreign_keys = ON")
        await self.db.execute("PRAGMA journal_mode = WAL")
        await self.db.execute("PRAGMA busy_timeout = 5000")
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS saved_embeds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                title TEXT,
                description TEXT,
                color INTEGER,
                thumbnail_url TEXT,
                image_url TEXT,
                author_name TEXT,
                author_url TEXT,
                author_icon_url TEXT,
                footer_text TEXT,
                footer_icon_url TEXT,
                timestamp_enabled INTEGER DEFAULT 0,
                created_by INTEGER,
                created_at TEXT,
                updated_at TEXT,
                UNIQUE(guild_id, name)
            );
            """
        )
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS embed_fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                embed_id INTEGER NOT NULL,
                position INTEGER NOT NULL,
                name TEXT NOT NULL,
                value TEXT NOT NULL,
                inline INTEGER DEFAULT 0,
                FOREIGN KEY(embed_id) REFERENCES saved_embeds(id) ON DELETE CASCADE
            );
            """
        )
        await self.db.execute("CREATE INDEX IF NOT EXISTS idx_saved_embeds_guild ON saved_embeds(guild_id)")
        await self.db.execute("CREATE INDEX IF NOT EXISTS idx_saved_embeds_guild_name ON saved_embeds(guild_id, name)")
        await self.db.execute("CREATE INDEX IF NOT EXISTS idx_fields_embed ON embed_fields(embed_id)")
        await self.db.commit()

    async def cog_unload(self) -> None:
        if self._init_task is not None:
            await self._init_task
            self._init_task = None
        if self.db is not None:
            await self.db.close()
            self.db = None

    async def _ensure_ready(self) -> None:
        if self._init_task is not None:
            await self._init_task
            self._init_task = None
        if self.db is None:
            raise RuntimeError("Database initialization failed.")

    async def _embed_belongs_to_guild(self, guild_id: int, embed_id: int) -> bool:
        await self._ensure_ready()
        cur = await self.db.execute(
            "SELECT 1 FROM saved_embeds WHERE id = ? AND guild_id = ?",
            (embed_id, guild_id),
        )
        row = await cur.fetchone()
        await cur.close()
        return bool(row)

    async def _get_embed_row(self, guild_id: int, name: str) -> Optional[Dict[str, Any]]:
        await self._ensure_ready()
        cur = await self.db.execute("SELECT * FROM saved_embeds WHERE guild_id = ? AND name = ?", (guild_id, name))
        row = await cur.fetchone()
        await cur.close()
        return dict(row) if row else None

    async def _get_fields(self, embed_id: int) -> List[Dict[str, Any]]:
        await self._ensure_ready()
        cur = await self.db.execute(
            "SELECT id, position, name, value, inline FROM embed_fields WHERE embed_id = ? ORDER BY position ASC",
            (embed_id,),
        )
        rows = await cur.fetchall()
        await cur.close()
        return [dict(row) for row in rows]

    async def get_fields_for_embed(self, guild_id: int, embed_id: int) -> List[Dict[str, Any]]:
        if not await self._embed_belongs_to_guild(guild_id, embed_id):
            return []
        await self._ensure_ready()
        cur = await self.db.execute(
            "SELECT id, position, name, value, inline FROM embed_fields WHERE embed_id = ? ORDER BY position ASC",
            (embed_id,),
        )
        rows = await cur.fetchall()
        await cur.close()
        return [dict(row) for row in rows]

    async def get_field_by_id(self, guild_id: int, embed_id: int, field_id: int) -> Optional[Dict[str, Any]]:
        if not await self._embed_belongs_to_guild(guild_id, embed_id):
            return None
        await self._ensure_ready()
        cur = await self.db.execute(
            "SELECT id, position, name, value, inline FROM embed_fields WHERE embed_id = ? AND id = ?",
            (embed_id, field_id),
        )
        row = await cur.fetchone()
        await cur.close()
        return dict(row) if row else None

    async def list_embeds(self, guild_id: int) -> List[str]:
        await self._ensure_ready()
        cur = await self.db.execute(
            "SELECT name FROM saved_embeds WHERE guild_id = ? ORDER BY name COLLATE NOCASE ASC",
            (guild_id,),
        )
        rows = await cur.fetchall()
        await cur.close()
        return [row[0] for row in rows]

    async def create_embed(self, guild_id: int, name: str, author_id: int) -> int:
        name = normalize_name(name)
        if not name or len(name) > 64:
            raise ValueError("Invalid embed name.")
        await self._ensure_ready()
        now = now_iso()
        try:
            cur = await self.db.execute(
                "INSERT INTO saved_embeds (guild_id, name, created_by, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (guild_id, name, author_id, now, now),
            )
            await self.db.commit()
            embed_id = cur.lastrowid
            await cur.close()
            return int(embed_id)
        except aiosqlite.IntegrityError as exc:
            raise ValueError("An embed with that name already exists.") from exc

    async def get_embed_data(self, guild_id: int, name: str) -> Optional[Dict[str, Any]]:
        row = await self._get_embed_row(guild_id, name)
        if not row:
            return None
        row["fields"] = await self._get_fields(row["id"])
        return row

    async def update_content(self, guild_id: int, embed_name: str, title: Optional[str], description: Optional[str]) -> None:
        await self._ensure_ready()
        if title is not None and len(title) > 256:
            raise ValueError("Title exceeds the 256-character limit.")
        if description is not None and len(description) > 4096:
            raise ValueError("Description exceeds the 4096-character limit.")
        await self.db.execute(
            "UPDATE saved_embeds SET title = ?, description = ?, updated_at = ? WHERE guild_id = ? AND name = ?",
            (title or None, description or None, now_iso(), guild_id, normalize_name(embed_name)),
        )
        await self.db.commit()

    async def update_color(self, guild_id: int, embed_name: str, color_input: str) -> None:
        await self._ensure_ready()
        if not color_input or not str(color_input).strip():
            await self.db.execute(
                "UPDATE saved_embeds SET color = NULL, updated_at = ? WHERE guild_id = ? AND name = ?",
                (now_iso(), guild_id, normalize_name(embed_name)),
            )
            await self.db.commit()
            return
        parsed = embed_utils.safe_int_color(color_input)
        if parsed is None:
            raise ValueError("Invalid color. Try #5865F2, 5865F2, 0x5865F2, or a common color name.")
        await self.db.execute(
            "UPDATE saved_embeds SET color = ?, updated_at = ? WHERE guild_id = ? AND name = ?",
            (parsed, now_iso(), guild_id, normalize_name(embed_name)),
        )
        await self.db.commit()

    async def update_media(self, guild_id: int, embed_name: str, thumbnail: str, image: str) -> None:
        await self._ensure_ready()
        if thumbnail and not embed_utils.is_valid_url(thumbnail):
            raise ValueError("Thumbnail URL must start with http:// or https://")
        if image and not embed_utils.is_valid_url(image):
            raise ValueError("Image URL must start with http:// or https://")
        await self.db.execute(
            "UPDATE saved_embeds SET thumbnail_url = ?, image_url = ?, updated_at = ? WHERE guild_id = ? AND name = ?",
            (thumbnail or None, image or None, now_iso(), guild_id, normalize_name(embed_name)),
        )
        await self.db.commit()

    async def update_author(self, guild_id: int, embed_name: str, name: str, url: str, icon: str) -> None:
        await self._ensure_ready()
        if name and len(name) > 256:
            raise ValueError("Author name exceeds the 256-character limit.")
        if url and not embed_utils.is_valid_url(url):
            raise ValueError("Author URL must start with http:// or https://")
        if icon and not embed_utils.is_valid_url(icon):
            raise ValueError("Author icon URL must start with http:// or https://")
        await self.db.execute(
            "UPDATE saved_embeds SET author_name = ?, author_url = ?, author_icon_url = ?, updated_at = ? WHERE guild_id = ? AND name = ?",
            (name or None, url or None, icon or None, now_iso(), guild_id, normalize_name(embed_name)),
        )
        await self.db.commit()

    async def update_footer(self, guild_id: int, embed_name: str, text: str, icon: str) -> None:
        await self._ensure_ready()
        if text and len(text) > 2048:
            raise ValueError("Footer text exceeds the 2048-character limit.")
        if icon and not embed_utils.is_valid_url(icon):
            raise ValueError("Footer icon URL must start with http:// or https://")
        await self.db.execute(
            "UPDATE saved_embeds SET footer_text = ?, footer_icon_url = ?, updated_at = ? WHERE guild_id = ? AND name = ?",
            (text or None, icon or None, now_iso(), guild_id, normalize_name(embed_name)),
        )
        await self.db.commit()

    async def toggle_timestamp(self, guild_id: int, embed_name: str) -> None:
        await self._ensure_ready()
        row = await self.db.execute(
            "SELECT timestamp_enabled FROM saved_embeds WHERE guild_id = ? AND name = ?",
            (guild_id, normalize_name(embed_name)),
        )
        current = await row.fetchone()
        await row.close()
        new_value = 0 if (current[0] if current else 0) else 1
        await self.db.execute(
            "UPDATE saved_embeds SET timestamp_enabled = ?, updated_at = ? WHERE guild_id = ? AND name = ?",
            (new_value, now_iso(), guild_id, normalize_name(embed_name)),
        )
        await self.db.commit()

    async def add_field(self, guild_id: int, embed_id: int, name: str, value: str, inline: str) -> None:
        if not await self._embed_belongs_to_guild(guild_id, embed_id):
            raise KeyError("Embed not found.")
        await self._ensure_ready()
        if len(name) > 256:
            raise ValueError("Field name exceeds the 256-character limit.")
        if len(value) > 1024:
            raise ValueError("Field value exceeds the 1024-character limit.")
        fields = await self.get_fields_for_embed(guild_id, embed_id)
        if len(fields) >= 25:
            raise ValueError("You cannot have more than 25 fields.")
        inline_bool = str(inline).strip().lower() in {"true", "1", "yes", "y"}
        await self.db.execute(
            "INSERT INTO embed_fields (embed_id, position, name, value, inline) VALUES (?, ?, ?, ?, ?)",
            (embed_id, len(fields), name, value, int(inline_bool)),
        )
        await self.db.commit()

    async def edit_field(self, guild_id: int, embed_id: int, field_id: int, name: str, value: str, inline: str) -> None:
        if not await self._embed_belongs_to_guild(guild_id, embed_id):
            raise KeyError("Embed not found.")
        await self._ensure_ready()
        if len(name) > 256:
            raise ValueError("Field name exceeds the 256-character limit.")
        if len(value) > 1024:
            raise ValueError("Field value exceeds the 1024-character limit.")
        inline_bool = str(inline).strip().lower() in {"true", "1", "yes", "y"}
        cur = await self.db.execute(
            "UPDATE embed_fields SET name = ?, value = ?, inline = ? WHERE id = ? AND embed_id = ?",
            (name, value, int(inline_bool), field_id, embed_id),
        )
        if cur.rowcount == 0:
            await cur.close()
            raise KeyError("Field not found.")
        await cur.close()
        await self.db.commit()

    async def remove_field(self, guild_id: int, embed_id: int, field_id: int) -> None:
        if not await self._embed_belongs_to_guild(guild_id, embed_id):
            raise KeyError("Embed not found.")
        await self._ensure_ready()
        await self.db.execute("DELETE FROM embed_fields WHERE id = ? AND embed_id = ?", (field_id, embed_id))
        await self.db.commit()

    async def move_field(self, guild_id: int, embed_id: int, field_id: int, up: bool) -> None:
        if not await self._embed_belongs_to_guild(guild_id, embed_id):
            raise KeyError("Embed not found.")
        await self._ensure_ready()
        fields = await self.get_fields_for_embed(guild_id, embed_id)
        index = None
        for idx, field in enumerate(fields):
            if field["id"] == field_id:
                index = idx
                break
        if index is None:
            return
        target = index - 1 if up else index + 1
        if target < 0 or target >= len(fields):
            return
        first = fields[index]
        second = fields[target]
        await self.db.execute("UPDATE embed_fields SET position = ? WHERE id = ?", (target, first["id"]))
        await self.db.execute("UPDATE embed_fields SET position = ? WHERE id = ?", (index, second["id"]))
        await self.db.commit()

    async def touch_embed(self, guild_id: int, embed_name: str) -> None:
        await self._ensure_ready()
        await self.db.execute(
            "UPDATE saved_embeds SET updated_at = ? WHERE guild_id = ? AND name = ?",
            (now_iso(), guild_id, normalize_name(embed_name)),
        )
        await self.db.commit()

    async def delete_embed(self, guild_id: int, name: str) -> bool:
        await self._ensure_ready()
        cur = await self.db.execute(
            "DELETE FROM saved_embeds WHERE guild_id = ? AND name = ?",
            (guild_id, normalize_name(name)),
        )
        await self.db.commit()
        return cur.rowcount > 0

    async def clone_embed(self, guild_id: int, src_name: str, dest_name: str, author_id: int) -> int:
        await self._ensure_ready()
        src = await self.get_embed_data(guild_id, normalize_name(src_name))
        if not src:
            raise KeyError("not found")
        dest = normalize_name(dest_name)
        if not dest or len(dest) > 64:
            raise ValueError("Invalid embed name.")
        try:
            await self.db.execute("BEGIN")
            cur = await self.db.execute(
                "INSERT INTO saved_embeds (guild_id, name, title, description, color, thumbnail_url, image_url, author_name, author_url, author_icon_url, footer_text, footer_icon_url, timestamp_enabled, created_by, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    guild_id,
                    dest,
                    src.get("title"),
                    src.get("description"),
                    src.get("color"),
                    src.get("thumbnail_url"),
                    src.get("image_url"),
                    src.get("author_name"),
                    src.get("author_url"),
                    src.get("author_icon_url"),
                    src.get("footer_text"),
                    src.get("footer_icon_url"),
                    src.get("timestamp_enabled"),
                    author_id,
                    now_iso(),
                    now_iso(),
                ),
            )
            new_embed_id = cur.lastrowid
            for field in src.get("fields", []):
                await self.db.execute(
                    "INSERT INTO embed_fields (embed_id, position, name, value, inline) VALUES (?, ?, ?, ?, ?)",
                    (new_embed_id, field.get("position", 0), field.get("name"), field.get("value"), int(bool(field.get("inline", False)))),
                )
            await self.db.commit()
            return int(new_embed_id)
        except aiosqlite.IntegrityError as exc:
            await self.db.execute("ROLLBACK")
            raise ValueError("An embed with that name already exists.") from exc

    async def rename_embed(self, guild_id: int, old_name: str, new_name: str) -> None:
        await self._ensure_ready()
        old = normalize_name(old_name)
        new = normalize_name(new_name)
        if not new or len(new) > 64:
            raise ValueError("Invalid embed name.")
        cur = await self.db.execute("SELECT id FROM saved_embeds WHERE guild_id = ? AND name = ?", (guild_id, new))
        if await cur.fetchone():
            await cur.close()
            raise ValueError("An embed with that name already exists.")
        await cur.close()
        cur = await self.db.execute(
            "UPDATE saved_embeds SET name = ?, updated_at = ? WHERE guild_id = ? AND name = ?",
            (new, now_iso(), guild_id, old),
        )
        await self.db.commit()
        if cur.rowcount == 0:
            raise KeyError("not found")

    def _safe_avatar_url(self, user: Optional[discord.abc.User]) -> Optional[str]:
        if not user:
            return None
        try:
            return str(user.display_avatar.replace(size=512).url)
        except Exception:
            try:
                return str(user.avatar.url)
            except Exception:
                return None

    def resolve_placeholders(self, template: str, *, user: Optional[discord.abc.User] = None, guild: Optional[discord.Guild] = None, channel: Optional[discord.abc.Messageable] = None, bot_user: Optional[discord.ClientUser] = None) -> str:
        if not template:
            return template
        import re

        def repl(match: Any) -> str:
            key = match.group(1).strip()
            try:
                if key == "user":
                    return str(user) if user is not None else match.group(0)
                if key.startswith("user."):
                    part = key.split(".", 1)[1]
                    if part == "mention":
                        return user.mention if user is not None else match.group(0)
                    if part == "name":
                        return user.name if user is not None else match.group(0)
                    if part == "display_name":
                        return getattr(user, "display_name", user.name) if user is not None else match.group(0)
                    if part == "id":
                        return str(user.id) if user is not None else match.group(0)
                    if part == "avatar":
                        return self._safe_avatar_url(user) or match.group(0)
                if key == "server":
                    return guild.name if guild is not None else match.group(0)
                if key.startswith("server."):
                    part = key.split(".", 1)[1]
                    if part == "name":
                        return guild.name if guild is not None else match.group(0)
                    if part == "id":
                        return str(guild.id) if guild is not None else match.group(0)
                    if part == "icon":
                        try:
                            return str(guild.icon.url) if guild is not None and guild.icon else match.group(0)
                        except Exception:
                            return match.group(0)
                    if part == "membercount":
                        return str(guild.member_count) if guild is not None else "0"
                if key == "channel":
                    return getattr(channel, "name", str(channel)) if channel is not None else match.group(0)
                if key.startswith("channel."):
                    part = key.split(".", 1)[1]
                    if part == "name":
                        return getattr(channel, "name", str(channel)) if channel is not None else match.group(0)
                    if part == "id":
                        return str(getattr(channel, "id", "")) if channel is not None else match.group(0)
                    if part == "mention":
                        return getattr(channel, "mention", str(channel)) if channel is not None else match.group(0)
                if key == "bot":
                    return bot_user.name if bot_user is not None else match.group(0)
                if key.startswith("bot."):
                    part = key.split(".", 1)[1]
                    if part == "name":
                        return bot_user.name if bot_user is not None else match.group(0)
                    if part == "mention":
                        return bot_user.mention if bot_user is not None else match.group(0)
                    if part == "avatar":
                        return self._safe_avatar_url(bot_user) or match.group(0)
            except Exception:
                return match.group(0)
            return match.group(0)

        return re.sub(r"\{([^{}]+)\}", repl, template)

    async def render_embed_for_context(self, data: Dict[str, Any], *, author: Optional[discord.User], guild: Optional[discord.Guild], channel: Optional[discord.abc.Messageable], bot_user: Optional[discord.ClientUser]) -> discord.Embed:
        resolved = dict(data)
        for key in ["title", "description", "author_name", "author_url", "author_icon_url", "footer_text", "footer_icon_url", "thumbnail_url", "image_url"]:
            value = resolved.get(key)
            if value:
                resolved[key] = self.resolve_placeholders(
                    str(value),
                    user=author,
                    guild=guild,
                    channel=channel,
                    bot_user=bot_user,
                )
        fields = []
        for field in resolved.get("fields", []):
            fields.append(
                {
                    "name": self.resolve_placeholders(str(field.get("name", "")), user=author, guild=guild, channel=channel, bot_user=bot_user),
                    "value": self.resolve_placeholders(str(field.get("value", "")), user=author, guild=guild, channel=channel, bot_user=bot_user),
                    "inline": bool(field.get("inline", False)),
                }
            )
        resolved["fields"] = fields
        embed_utils.validate_embed_payload(resolved)
        return embed_utils.build_embed_from_data(resolved, {})

    async def _can_manage(self, ctx: commands.Context) -> bool:
        if await self.bot.is_owner(ctx.author):
            return True
        perms = ctx.author.guild_permissions
        return bool(perms.manage_messages or perms.manage_guild)

    # -----------------
    # Commands
    # -----------------
    @commands.hybrid_group(name="embed", invoke_without_command=True)
    @commands.guild_only()
    async def embed(self, ctx: commands.Context) -> None:
        prefix = ctx.prefix
        embed = discord.Embed(title="Xtreme Embed Builder", description="Create and manage custom server embeds.", color=0x5865F2)
        embed.add_field(
            name="Commands",
            value=(
                f"`{prefix}embed create <name>`\n"
                f"`{prefix}embed edit <name>`\n"
                f"`{prefix}embed preview <name>`\n"
                f"`{prefix}embed send <name> [#channel]`\n"
                f"`{prefix}embed list`\n"
                f"`{prefix}embed clone <name> <new_name>`\n"
                f"`{prefix}embed rename <name> <new_name>`\n"
                f"`{prefix}embed delete <name>`"
            ),
        )
        await ctx.send(embed=embed)

    @embed.command(name="create")
    @commands.guild_only()
    async def embed_create(self, ctx: commands.Context, name: str) -> None:
        if not await self._can_manage(ctx):
            return await ctx.send(f"{Emojis.CROSS} You don't have permission to manage embeds.")
        normalized_name = normalize_name(name)
        if not normalized_name:
            return await ctx.send(f"{Emojis.CROSS} Invalid embed name.")
        try:
            embed_id = await self.create_embed(ctx.guild.id, normalized_name, ctx.author.id)
        except ValueError as exc:
            return await ctx.send(f"{Emojis.CROSS} {exc}")
        data = await self.get_embed_data(ctx.guild.id, normalized_name)
        view = embed_utils.EmbedEditorView(controller=self, guild_id=ctx.guild.id, embed_id=embed_id, embed_name=normalized_name, owner_id=ctx.author.id)
        await view.load_fields()
        preview = await self.render_embed_for_context(data or {}, author=ctx.author, guild=ctx.guild, channel=ctx.channel, bot_user=self.bot.user)
        message = await ctx.send(embed=preview, view=view)
        view.message = message

    @embed.command(name="edit")
    @commands.guild_only()
    async def embed_edit(self, ctx: commands.Context, name: str) -> None:
        if not await self._can_manage(ctx):
            return await ctx.send(f"{Emojis.CROSS} You don't have permission to manage embeds.")
        normalized_name = normalize_name(name)
        data = await self.get_embed_data(ctx.guild.id, normalized_name)
        if not data:
            return await ctx.send(f"{Emojis.CROSS} Embed not found.")
        view = embed_utils.EmbedEditorView(controller=self, guild_id=ctx.guild.id, embed_id=data["id"], embed_name=normalized_name, owner_id=ctx.author.id)
        await view.load_fields()
        preview = await self.render_embed_for_context(data, author=ctx.author, guild=ctx.guild, channel=ctx.channel, bot_user=self.bot.user)
        message = await ctx.send(embed=preview, view=view)
        view.message = message

    @embed.command(name="preview")
    @commands.guild_only()
    async def embed_preview(self, ctx: commands.Context, name: str) -> None:
        data = await self.get_embed_data(ctx.guild.id, normalize_name(name))
        if not data:
            return await ctx.send(f"{Emojis.CROSS} Embed not found.")
        try:
            preview = await self.render_embed_for_context(data, author=ctx.author, guild=ctx.guild, channel=ctx.channel, bot_user=self.bot.user)
            await ctx.send(embed=preview)
        except ValueError as exc:
            await ctx.send(f"{Emojis.CROSS} {exc}")

    @embed.command(name="send")
    @commands.guild_only()
    async def embed_send(self, ctx: commands.Context, name: str, channel: Optional[discord.TextChannel] = None) -> None:
        if not await self._can_manage(ctx):
            return await ctx.send(f"{Emojis.CROSS} You don't have permission to manage embeds.")
        target = channel or ctx.channel
        if not isinstance(target, discord.TextChannel):
            return await ctx.send(f"{Emojis.CROSS} Channel not found.")
        perms = target.permissions_for(ctx.guild.me)
        if not (perms.view_channel and perms.send_messages and perms.embed_links):
            return await ctx.send(f"{Emojis.CROSS} I need View Channel, Send Messages, and Embed Links in that channel.")
        data = await self.get_embed_data(ctx.guild.id, normalize_name(name))
        if not data:
            return await ctx.send(f"{Emojis.CROSS} Embed not found.")
        try:
            embed = await self.render_embed_for_context(data, author=ctx.author, guild=ctx.guild, channel=target, bot_user=self.bot.user)
            await target.send(embed=embed)
            await ctx.send(f"{Emojis.TICK} Embed sent to {target.mention}.")
        except ValueError as exc:
            await ctx.send(f"{Emojis.CROSS} {exc}")
        except discord.Forbidden:
            await ctx.send(f"{Emojis.CROSS} I cannot send embeds to that channel.")
        except discord.HTTPException:
            await ctx.send(f"{Emojis.CROSS} Failed to send the embed. Please try again.")

    @embed.command(name="delete")
    @commands.guild_only()
    async def embed_delete(self, ctx: commands.Context, name: str) -> None:
        if not await self._can_manage(ctx):
            return await ctx.send(f"{Emojis.CROSS} You don't have permission to manage embeds.")
        data = await self.get_embed_data(ctx.guild.id, normalize_name(name))
        if not data:
            return await ctx.send(f"{Emojis.CROSS} Embed not found.")
        view = embed_utils.ConfirmView(owner_id=ctx.author.id)
        message = await ctx.send(f"Delete embed \"{normalize_name(name)}\"?", view=view)
        await view.wait()
        if view.value is True:
            await self.delete_embed(ctx.guild.id, normalize_name(name))
            await message.edit(content=f"{Emojis.TICK} Deleted.", view=None)
        else:
            await message.edit(content=f"{Emojis.CROSS} Cancelled.", view=None)

    @embed.command(name="list")
    @commands.guild_only()
    async def embed_list(self, ctx: commands.Context) -> None:
        items = await self.list_embeds(ctx.guild.id)
        if not items:
            return await ctx.send("No saved embeds.")
        view = embed_utils.EmbedListView(names=items, owner_id=ctx.author.id)
        message = await ctx.send(embed=view.build_embed(), view=view)
        view.message = message

    @embed.command(name="clone")
    @commands.guild_only()
    async def embed_clone(self, ctx: commands.Context, existing_name: str, new_name: str) -> None:
        if not await self._can_manage(ctx):
            return await ctx.send(f"{Emojis.CROSS} You don't have permission to manage embeds.")
        try:
            await self.clone_embed(ctx.guild.id, existing_name, new_name, ctx.author.id)
            await ctx.send(f"{Emojis.TICK} Cloned.")
        except KeyError:
            await ctx.send(f"{Emojis.CROSS} Source embed not found.")
        except ValueError as exc:
            await ctx.send(f"{Emojis.CROSS} {exc}")

    @embed.command(name="rename")
    @commands.guild_only()
    async def embed_rename(self, ctx: commands.Context, old_name: str, new_name: str) -> None:
        if not await self._can_manage(ctx):
            return await ctx.send(f"{Emojis.CROSS} You don't have permission to manage embeds.")
        try:
            await self.rename_embed(ctx.guild.id, old_name, new_name)
            await ctx.send(f"{Emojis.TICK} Renamed.")
        except KeyError:
            await ctx.send(f"{Emojis.CROSS} Embed not found.")
        except ValueError as exc:
            await ctx.send(f"{Emojis.CROSS} {exc}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(EmbedCog(bot))
