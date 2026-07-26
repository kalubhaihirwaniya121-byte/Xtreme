import discord

DEFAULT_COLOR = 0x2f3136

FOOTER_TEXT = "Thanks for using Xtreme"

def basic_embed(

    title: str,

    description: str,

    color: int = DEFAULT_COLOR

) -> discord.Embed:

    """

    Create a standard embed used across the bot

    """

    embed = discord.Embed(

        title=title,

        description=description,

        color=color

    )

    embed.set_footer(text=FOOTER_TEXT)

    return embed

def error_embed(description: str) -> discord.Embed:

    """

    Red error embed

    """

    return basic_embed(

        title="Error",

        description=description,

        color=0xe74c3c

    )

def success_embed(description: str) -> discord.Embed:

    """

    Green success embed

    """

    return basic_embed(

        title="Success",

        description=description,

        color=0x2ecc71

    )

def info_embed(title: str, description: str) -> discord.Embed:

    """

    Info embed with custom title

    """

    return basic_embed(

        title=title,

        description=description,

        color=0x3498db

    )