import json
import re
from pathlib import Path

import aiohttp
import discord

ACTION_GIFS = {}

TENOR_REGEX = re.compile(r"https?://(?:www\.)?(?:tenor\.com|media\.tenor\.com)\S+")
GIF_REGEX = re.compile(r"https?://\S+\.(?:gif|webp|mp4)", re.IGNORECASE)
TENOR_PAGE_REGEX = re.compile(
    r"https?://(?:www\.)?tenor\.com/view/[\w-]+-(\d+)"
)

DATA_FILE = Path("data/action_owner.json")

# Get one free from:
# https://developers.google.com/tenor
TENOR_API_KEY = "YOUR_TENOR_API_KEY"


async def resolve_tenor_url(url: str, session: aiohttp.ClientSession) -> str:
    """Convert a Tenor page URL into a direct media.tenor.com URL."""

    if "media.tenor.com" in url:
        return url

    match = TENOR_PAGE_REGEX.search(url)
    if not match:
        return url

    gif_id = match.group(1)

    api = (
        f"https://tenor.googleapis.com/v2/posts"
        f"?ids={gif_id}"
        f"&key={TENOR_API_KEY}"
    )

    try:
        async with session.get(api) as resp:
            if resp.status != 200:
                return url

            data = await resp.json()

            if not data.get("results"):
                return url

            media = data["results"][0]["media_formats"]

            for fmt in (
                "gif",
                "mediumgif",
                "tinygif",
                "mp4",
            ):
                if fmt in media:
                    return media[fmt]["url"]

    except Exception:
        pass

    return url


async def load_action_gifs(bot: discord.Client):
    """Load all action GIFs from the configured Discord channels."""

    global ACTION_GIFS
    ACTION_GIFS.clear()

    if not DATA_FILE.exists():
        print("[Action Loader] action_owner.json not found.")
        return

    with DATA_FILE.open("r", encoding="utf-8") as f:
        channels = json.load(f)

    print("\n========== Loading Action GIFs ==========")

    total = 0

    async with aiohttp.ClientSession() as session:

        for action, channel_id in channels.items():

            ACTION_GIFS[action] = []

            channel = bot.get_channel(channel_id)

            if channel is None:
                try:
                    channel = await bot.fetch_channel(channel_id)
                except Exception:
                    print(f"✗ {action:<10} Channel not found.")
                    continue

            async for message in channel.history(
                limit=None,
                oldest_first=True,
            ):

                # Attachments
                for attachment in message.attachments:

                    if (
                        attachment.content_type
                        and attachment.content_type.startswith("image")
                    ):
                        ACTION_GIFS[action].append(attachment.url)

                    elif attachment.filename.lower().endswith(
                        (".gif", ".webp", ".mp4")
                    ):
                        ACTION_GIFS[action].append(attachment.url)

                # URLs inside message
                urls = TENOR_REGEX.findall(message.content)
                urls += GIF_REGEX.findall(message.content)

                for url in urls:
                    if (
                        "tenor.com" in url
                        and "media.tenor.com" not in url
                    ):
                        url = await resolve_tenor_url(url, session)

                    ACTION_GIFS[action].append(url)

                # Embeds
                for embed in message.embeds:

                    if embed.image and embed.image.url:
                        ACTION_GIFS[action].append(embed.image.url)

                    if embed.thumbnail and embed.thumbnail.url:
                        ACTION_GIFS[action].append(embed.thumbnail.url)

                    if embed.url and (
                        "tenor.com" in embed.url
                        or "media.tenor.com" in embed.url
                    ):
                        resolved = await resolve_tenor_url(
                            embed.url,
                            session,
                        )
                        ACTION_GIFS[action].append(resolved)

                # Remove duplicates
                ACTION_GIFS[action] = list(
                    dict.fromkeys(ACTION_GIFS[action])
                )

            count = len(ACTION_GIFS[action])
            total += count

            print(f"✓ {action.title():<10} {count} GIFs")

    print("-----------------------------------------")
    print(f"Loaded {total} GIFs successfully.")
    print("=========================================\n")