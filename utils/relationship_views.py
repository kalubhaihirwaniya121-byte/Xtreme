import discord

from discord.ui import View, Button

from datetime import datetime

from utils.storage import load_json, save_json
from utils.emojis import Emojis


class MarriageView(View):

    def __init__(
        self,
        proposer,
        target
    ):

        super().__init__(timeout=120)

        self.proposer = proposer

        self.target = target

        self.data = load_json(
            "relationships.json"
        )

    def save(self):

        save_json(
            "relationships.json",
            self.data
        )
      
    @discord.ui.button(
      label="Accept",
      emoji=f"{Emojis.TICK}",
      style=discord.ButtonStyle.success
    )
    async def accept(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if interaction.user.id != self.target.id:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} This proposal isn't for you.",
                ephemeral=True
            )

        proposer = str(self.proposer.id)
        target = str(self.target.id)

        if proposer in self.data["marriages"]:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} {self.proposer.mention} is already married.",
                ephemeral=True
            )

        if target in self.data["marriages"]:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} You are already married.",
                ephemeral=True
            )

        today = datetime.utcnow().strftime(
            "%d %B %Y"
        )

        self.data["marriages"][proposer] = {
            "partner": self.target.id,
            "since": today,
            "children": [],
            "kiss": 0,
            "hug": 0
        }

        self.data["marriages"][target] = {
            "partner": self.proposer.id,
            "since": today,
            "children": [],
            "kiss": 0,
            "hug": 0
        }

        self.data["engagements"].pop(
            proposer,
            None
        )

        self.data["engagements"].pop(
            target,
            None
        )

        self.save()

        embed = discord.Embed(
            title="💍 Marriage Successful",
            description=(
                f"{self.proposer.mention} ❤️ {self.target.mention}\n\n"
                "Congratulations on your marriage!"
            ),
            color=0x2ECC71
        )

        embed.set_footer(
            text="Thanks for using Xtreme"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None
        )

    @discord.ui.button(
        label="Decline",
        emoji=f"{Emojis.CROSS}",
        style=discord.ButtonStyle.danger
    )
    async def decline(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if interaction.user.id != self.target.id:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} This proposal isn't for you.",
                ephemeral=True
            )

        embed = discord.Embed(
            description=(
                f"{Emojis.CROSS} "
                f"{self.target.mention} declined the marriage proposal."
            ),
            color=0xE74C3C
        )

        embed.set_footer(
            text="Thanks for using Xtreme"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None
        )
        
class ProposalView(View):

    def __init__(
        self,
        proposer,
        target
    ):

        super().__init__(timeout=120)

        self.proposer = proposer

        self.target = target
        
        self.data = load_json(
            "relationships.json"
        )

        if "engagements" not in self.data:
          self.data["engagements"] = {}
    def save(self):

        save_json(
            "relationships.json",
            self.data
        )
        
    @discord.ui.button(
        label="Accept",
        emoji=f"{Emojis.TICK}",
        style=discord.ButtonStyle.success
    )
    async def accept(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if interaction.user.id != self.target.id:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} This proposal isn't for you.",
                ephemeral=True
            )

        proposer = str(self.proposer.id)
        target = str(self.target.id)

        if proposer in self.data["engagements"]:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} You are already engaged.",
                ephemeral=True
            )

        if target in self.data["engagements"]:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} That user is already engaged.",
                ephemeral=True
            )

        self.data["engagements"][proposer] = self.target.id
        self.data["engagements"][target] = self.proposer.id

        self.save()
        
        embed = discord.Embed(

            title="💖 Proposal Accepted",
            
            description=(
    f"{self.target.mention} accepted "
    f"{self.proposer.mention}'s proposal!\n\n"
    "💖 You are now engaged!\n\n"
    "Use **.marry** to complete your marriage."
),

            color=0x2ECC71

        )

        embed.set_footer(
            text="Thanks for using Xtreme"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None
        )

    @discord.ui.button(
        label="Decline",
        emoji=f"{Emojis.CROSS}",
        style=discord.ButtonStyle.danger
    )
    async def decline(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if interaction.user.id != self.target.id:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} This proposal isn't for you.",
                ephemeral=True
            )

        embed = discord.Embed(

            description=(
                f"{Emojis.CROSS} "
                f"{self.target.mention} declined the proposal."
            ),

            color=0xE74C3C

        )

        embed.set_footer(
            text="Thanks for using Xtreme"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None
        )
        
class AdoptView(View):

    def __init__(
        self,
        parent,
        partner,
        child
    ):

        super().__init__(timeout=120)

        self.parent = parent

        self.partner = partner

        self.child = child

        self.data = load_json(
            "relationships.json"
        )

    def save(self):

        save_json(
            "relationships.json",
            self.data
        )

    @discord.ui.button(
        label="Accept",
        emoji=f"{Emojis.TICK}",
        style=discord.ButtonStyle.success
    )
    async def accept(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if interaction.user.id != self.child.id:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} This adoption request isn't for you.",
                ephemeral=True
            )

        parent = str(self.parent.id)
        partner = str(self.partner.id)
        child = str(self.child.id)

        if "parents" not in self.data:
            self.data["parents"] = {}

        if child in self.data["parents"]:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} You have already been adopted.",
                ephemeral=True
            )

        self.data["marriages"][parent]["children"].append(
            self.child.id
        )

        self.data["marriages"][partner]["children"].append(
            self.child.id
        )

        self.data["parents"][child] = [
            self.parent.id,
            self.partner.id
        ]

        self.save()

        embed = discord.Embed(

            title="👶 Adoption Successful",

            description=(
                f"{self.child.mention} has been adopted by\n"
                f"{self.parent.mention} ❤️ {self.partner.mention}"
            ),

            color=0x2ECC71

        )

        embed.set_footer(
            text="Thanks for using Xtreme"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None
        )

    @discord.ui.button(
        label="Decline",
        emoji=f"{Emojis.CROSS}",
        style=discord.ButtonStyle.danger
    )
    async def decline(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if interaction.user.id != self.child.id:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} This adoption request isn't for you.",
                ephemeral=True
            )

        embed = discord.Embed(

            description=(
                f"{Emojis.CROSS} "
                f"{self.child.mention} declined the adoption request."
            ),

            color=0xE74C3C

        )

        embed.set_footer(
            text="Thanks for using Xtreme"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None
        )
        
class DivorceConfirmView(View):

    def __init__(
        self,
        user
    ):

        super().__init__(timeout=120)

        self.user = user

        self.data = load_json(
            "relationships.json"
        )

    def save(self):

        save_json(
            "relationships.json",
            self.data
        )

    @discord.ui.button(
        label="Confirm",
        emoji=f"{Emojis.TICK}",
        style=discord.ButtonStyle.danger
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if interaction.user.id != self.user.id:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} This button isn't for you.",
                ephemeral=True
            )

        user = str(self.user.id)

        if user not in self.data["marriages"]:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} You are not married.",
                ephemeral=True
            )

        partner = str(
            self.data["marriages"][user]["partner"]
        )

        self.data["marriages"].pop(
            user,
            None
        )

        self.data["marriages"].pop(
            partner,
            None
        )
        
        self.data["engagements"].pop(
            user,
            None
        )

        self.data["engagements"].pop(
            partner,
            None
        )

        self.save()

        embed = discord.Embed(

            title="💔 Divorce Successful",

            description=(
                "Your marriage has been ended."
            ),

            color=0xE74C3C

        )

        embed.set_footer(
            text="Thanks for using Xtreme"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None
        )

    @discord.ui.button(
        label="Cancel",
        emoji=f"{Emojis.CROSS}",
        style=discord.ButtonStyle.secondary
    )
    async def cancel(
        self,
        interaction: discord.Interaction,
        button: Button
    ):

        if interaction.user.id != self.user.id:

            return await interaction.response.send_message(
                f"{Emojis.CROSS} This button isn't for you.",
                ephemeral=True
            )

        embed = discord.Embed(

            description=(
                f"{Emojis.CROSS} Divorce cancelled."
            ),

            color=0x5865F2

        )

        embed.set_footer(
            text="Thanks for using Xtreme"
        )

        await interaction.response.edit_message(
            embed=embed,
            view=None
        )