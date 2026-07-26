import random

import discord

from discord.ui import View


class TruthDareView(View):

    def __init__(
        self,
        bot,
        truths,
        dares
    ):
        super().__init__(timeout=None)

        self.bot = bot
        self.truths = truths
        self.dares = dares

    async def send_embed(
        self,
        target,
        mode: str
    ):
        if mode == "truth" and not self.truths:
            return

        if mode == "dare" and not self.dares:
            return

        if mode == "truth":

            title = "🤔 Truth"
            color = 0x57F287
            text = random.choice(
                self.truths
            )

        elif mode == "dare":

            title = "😈 Dare"
            color = 0xED4245
            text = random.choice(
                self.dares
            )

        else:

            if random.choice(
                (True, False)
            ):

                title = "🤔 Truth"
                color = 0x57F287
                text = random.choice(
                    self.truths
                )

                mode = "truth"

            else:

                title = "😈 Dare"
                color = 0xED4245
                text = random.choice(
                    self.dares
                )

                mode = "dare"

        if isinstance(
            target,
            discord.Interaction
        ):

            user = target.user

        else:

            user = target.author

        embed = discord.Embed(

            title=title,

            description=text,

            color=color

        )

        embed.set_author(

            name=f"Requested by {user.display_name}",

            icon_url=user.display_avatar.url

        )

        embed.set_footer(

            text=f"Type: {mode.title()} • Xtreme"

        )

        view = TruthDareView(

            self.bot,

            self.truths,

            self.dares

        )

        if isinstance(
            target,
            discord.Interaction
        ):

            await target.response.send_message(

                embed=embed,

                view=view

            )

        else:

            await target.send(

                embed=embed,

                view=view

            )

    @discord.ui.button(
        label="Truth",
        emoji="🤔",
        style=discord.ButtonStyle.success,
        custom_id="xtreme_truth_button"
    )
    async def truth_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await self.send_embed(
            interaction,
            "truth"
        )


    @discord.ui.button(
        label="Dare",
        emoji="😈",
        style=discord.ButtonStyle.danger,
        custom_id="xtreme_dare_button"
    )
    async def dare_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await self.send_embed(
            interaction,
            "dare"
        )


    @discord.ui.button(
        label="Random",
        emoji="🎲",
        style=discord.ButtonStyle.primary,
        custom_id="xtreme_random_button"
    )
    async def random_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await self.send_embed(
            interaction,
            "random"
        )