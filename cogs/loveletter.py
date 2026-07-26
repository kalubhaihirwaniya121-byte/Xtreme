import discord
import aiohttp
import json

from discord.ext import commands

from utils.storage import load_json, save_json
from utils.emojis import Emojis
from utils.loveletter_views import LoveLetterView

import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


class LoveLetter(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        self.data = load_json(
            "loveletter.json"
        )

        if "blocked" not in self.data:

            self.data["blocked"] = {}

        if "cooldowns" not in self.data:

            self.data["cooldowns"] = {}

        self.save()

    # ------------------------------
    # STORAGE
    # ------------------------------

    def save(self):

        save_json(
            "loveletter.json",
            self.data
        )

    def reload(self):

        self.data = load_json(
            "loveletter.json"
        )

    # ------------------------------
    # EMBEDS
    # ------------------------------

    async def error(
        self,
        ctx,
        message
    ):

        embed = discord.Embed(

            description=f"{Emojis.CROSS} {message}",

            color=0xE74C3C

        )

        embed.set_footer(
            text="Thanks for using Xtreme"
        )

        await ctx.send(
            embed=embed
        )

    async def success(
        self,
        ctx,
        message
    ):

        embed = discord.Embed(

            description=f"{Emojis.TICK} {message}",

            color=0x2ECC71

        )

        embed.set_footer(
            text="Thanks for using Xtreme"
        )

        await ctx.send(
            embed=embed
        )
        
    # ------------------------------
    # AI GENERATOR
    # ------------------------------

    async def generate_letter(
        self,
        sender,
        receiver,
        message=None
    ):

        self.reload()

        prompt = ""

        if message:

            prompt += (
                f"Include this message naturally "
                f"in the love letter:\n\n"
                f"{message}\n\n"
            )

        relationship = load_json(
            "relationships.json"
        )

        partner = False

        if (
            "marriages" in relationship
            and
            str(sender.id) in relationship["marriages"]
        ):

            if (
                relationship["marriages"][
                    str(sender.id)
                ]["partner"]
                ==
                receiver.id
            ):

                partner = True

        if partner:

            prompt += (
                f"Write a heartfelt romantic love "
                f"letter from {sender.display_name} "
                f"to {receiver.display_name}. "
                f"Keep it wholesome, emotional, "
                f"around 150 words and completely unique."
            )

        else:

            prompt += (
                f"Write a cute and respectful crush "
                f"letter from {sender.display_name} "
                f"to {receiver.display_name}. "
                f"Keep it wholesome, friendly, "
                f"around 120 words and completely unique."
            )

        headers = {

            "Authorization":
            f"Bearer {GROQ_API_KEY}",

            "Content-Type":
            "application/json"

        }

        payload = {

            "model":
            "llama-3.3-70b-versatile",

            "messages": [

                {
                    "role": "user",
                    "content": prompt
                }

            ]

        }

        async with aiohttp.ClientSession() as session:

            async with session.post(

                "https://api.groq.com/openai/v1/chat/completions",

                headers=headers,

                json=payload

            ) as response:

                if response.status != 200:

                    return None

                data = await response.json()

                return data[
                    "choices"
                ][0][
                    "message"
                ][
                    "content"
                ]
                
    # ------------------------------
    # LOVE LETTER
    # ------------------------------

    @commands.hybrid_command(
        name="loveletter",
        description="Generate an AI love letter."
    )
    async def loveletter(
        self,
        ctx,
        member: discord.Member,
        *,
        message: str = None
    ):

        self.reload()

        if member.bot:

            return await self.error(
                ctx,
                "You can't send a love letter to a bot."
            )

        if member == ctx.author:

            return await self.error(
                ctx,
                "You can't send a love letter to yourself."
            )

        blocked = self.data["blocked"].get(
            str(member.id),
            []
        )

        if ctx.author.id in blocked:

            return await self.error(
                ctx,
                "This user isn't accepting your love letters."
            )

        waiting = discord.Embed(

            description=(
                "💌 Generating your love letter...\n"
                "Please wait a moment."
            ),

            color=0xFF69B4

        )

        msg = await ctx.send(
            embed=waiting
        )

        letter = await self.generate_letter(

            ctx.author,
            member,
            message

        )

        if letter is None:

            return await msg.edit(

                embed=discord.Embed(

                    description=(
                        f"{Emojis.CROSS} Failed to generate the love letter."
                    ),

                    color=0xE74C3C

                )

            )

        preview = discord.Embed(

            title="💌 Love Letter Preview",

            description=letter,

            color=0xFF69B4

        )

        preview.add_field(

            name="To",

            value=member.mention,

            inline=False

        )

        preview.set_footer(

            text="This letter has not been sent yet."

        )

        await msg.edit(

            embed=preview,

            view=LoveLetterView(

                self.bot,

                ctx.author,

                member,

                letter,

                self.regenerate_letter

            )

        )
        
    # ------------------------------
    # REGENERATE
    # ------------------------------

    async def regenerate_letter(
        self,
        interaction: discord.Interaction
    ):

        view = interaction.message.view

        letter = await self.generate_letter(

            view.sender,

            view.receiver

        )

        if letter is None:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} Failed to regenerate the letter.",
                ephemeral=True
            )

        view.letter = letter

        embed = discord.Embed(

            title="💌 Love Letter Preview",

            description=letter,

            color=0xFF69B4

        )

        embed.add_field(

            name="To",

            value=view.receiver.mention,

            inline=False

        )

        embed.set_footer(

            text="This letter has not been sent yet."

        )

        await interaction.response.edit_message(

            embed=embed,

            view=view

        )
        
    # ------------------------------
    # SETUP
    # ------------------------------


async def setup(
    bot
):

    await bot.add_cog(

        LoveLetter(bot)

    )