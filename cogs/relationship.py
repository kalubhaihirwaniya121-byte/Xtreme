import random
import discord
import random

from discord.ext import commands

from utils.storage import load_json, save_json
from utils.emojis import Emojis
from utils.relationship_views import (
    MarriageView,
    ProposalView,
    AdoptView,
    DivorceConfirmView
)
from utils.ship_view import ShipView

class Relationship(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.data = load_json("relationships.json")

        if "engagements" not in self.data:
            self.data["engagements"] = {}

        if "marriages" not in self.data:
            self.data["marriages"] = {}

        if "parents" not in self.data:
            self.data["parents"] = {}

        self.save()
    # ------------------------------
    # STORAGE
    # ------------------------------

    def save(self):

        save_json(
            "relationships.json",
            self.data
        )
      
    def reload(self):

        self.data = load_json(
            "relationships.json"
        )

    # ------------------------------
    # EMBEDS
    # ------------------------------

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

    # ------------------------------
    # HELPERS
    # ------------------------------

    def married(
        self,
        user_id: int
    ):

        return str(user_id) in self.data["marriages"]

    def engaged(
        self,
        user_id: int
    ):

        return str(user_id) in self.data["engagements"]
        
    # ------------------------------
    # PROPOSE
    # ------------------------------

    @commands.hybrid_command(
        name="propose",
        description="Propose to someone."
    )
    async def propose(
        self,
        ctx,
        member: discord.Member
    ):

        self.reload()
        
        if member.bot:

            return await self.error(
                ctx,
                "You can't propose to a bot."
            )

        if member == ctx.author:

            return await self.error(
                ctx,
                "You can't propose to yourself."
            )

        if self.married(ctx.author.id):

            return await self.error(
                ctx,
                "You are already married."
            )

        if self.married(member.id):

            return await self.error(
                ctx,
                "That user is already married."
            )

        if self.engaged(ctx.author.id):

            return await self.error(
                ctx,
                "You are already engaged."
            )

        if self.engaged(member.id):

            return await self.error(
                ctx,
                "That user is already engaged."
            )

        embed = discord.Embed(

            title="🌹 Marriage Proposal",

            description=(
                f"{ctx.author.mention} has proposed to "
                f"{member.mention}!\n\n"
                "Click a button below to respond."
            ),

            color=0xFF69B4

        )

        embed.set_footer(
            text="Proposal expires in 2 minutes."
        )

        await ctx.send(

            content=member.mention,

            embed=embed,

            view=ProposalView(
                ctx.author,
                member
            )

        )
        
    # ------------------------------
    # MARRY
    # ------------------------------

    @commands.hybrid_command(
        name="marry",
        description="Marry your fiancé."
    )
    async def marry(
        self,
        ctx,
        member: discord.Member
    ):

        self.reload()
        
        if member.bot:

            return await self.error(
                ctx,
                "You can't marry a bot."
            )

        if member == ctx.author:

            return await self.error(
                ctx,
                "You can't marry yourself."
            )

        if self.married(ctx.author.id):

            return await self.error(
                ctx,
                "You are already married."
            )

        if self.married(member.id):

            return await self.error(
                ctx,
                "That user is already married."
            )

        if not self.engaged(ctx.author.id):

            return await self.error(
                ctx,
                "You must propose first."
            )

        engaged_partner = self.data[
            "engagements"
        ].get(
            str(ctx.author.id)
        )

        if engaged_partner != member.id:

            return await self.error(
                ctx,
                "You can only marry the person you're engaged to."
            )

        embed = discord.Embed(

            title="💍 Marriage Request",

            description=(
                f"{ctx.author.mention} wants to marry "
                f"{member.mention}.\n\n"
                "Click a button below to respond."
            ),

            color=0xF1C40F

        )

        embed.set_footer(
            text="Request expires in 2 minutes."
        )

        await ctx.send(

            content=member.mention,

            embed=embed,

            view=MarriageView(
                ctx.author,
                member
            )

        )
        
    # ------------------------------
    # PARTNER
    # ------------------------------

    @commands.hybrid_command(
        name="partner",
        description="View your partner."
    )
    async def partner(
        self,
        ctx,
        member: discord.Member = None
    ):

        self.reload()
        
        member = member or ctx.author

        if not self.married(member.id):

            return await self.error(
                ctx,
                f"{member.display_name} is not married."
            )

        data = self.data["marriages"][
            str(member.id)
        ]

        partner = self.bot.get_user(
            data["partner"]
        )

        if partner is None:
            try:
                partner = await self.bot.fetch_user(data["partner"])
            except Exception:
                partner = None

        embed = discord.Embed(

            title="❤️ Partner",

            color=0xFF4D6D

        )

        embed.add_field(
            name="User",
            value=member.mention,
            inline=True
        )

        embed.add_field(
            name="Partner",
            value=(
                partner.mention
                if partner
                else "Unknown User"
            ),
            inline=True
        )

        embed.add_field(
            name="Married Since",
            value=data["since"],
            inline=False
        )

        embed.set_footer(
            text="Thanks for using Xtreme"
        )

        await ctx.send(
            embed=embed
        )

    # ------------------------------
    # RELATIONSHIP
    # ------------------------------

    @commands.hybrid_command(
        name="relationship",
        description="View relationship profile."
    )
    async def relationship(
        self,
        ctx,
        member: discord.Member = None
    ):

        self.reload()
        
        member = member or ctx.author

        if not self.married(member.id):

            return await self.error(
                ctx,
                f"{member.display_name} is not married."
            )

        data = self.data["marriages"][
            str(member.id)
        ]

        partner = self.bot.get_user(
            data["partner"]
        )

        if partner is None:
            try:
                partner = await self.bot.fetch_user(data["partner"])
            except Exception:
                partner = None

        embed = discord.Embed(

            title="💕 Relationship Profile",

            color=0xFF69B4

        )

        embed.add_field(
            name="Partner",
            value=(
                partner.mention
                if partner
                else "Unknown User"
            ),
            inline=False
        )

        embed.add_field(
            name="Since",
            value=data["since"],
            inline=True
        )

        embed.add_field(
            name="Children",
            value=len(
                data["children"]
            ),
            inline=True
        )

        embed.add_field(
            name="😘 Kisses",
            value=data["kiss"],
            inline=True
        )

        embed.add_field(
            name="🤗 Hugs",
            value=data["hug"],
            inline=True
        )

        embed.set_footer(
            text="Thanks for using Xtreme"
        )

        await ctx.send(
            embed=embed
        )
        
    # ------------------------------
    # DIVORCE
    # ------------------------------

    @commands.hybrid_command(
        name="divorce",
        description="Divorce your partner."
    )
    async def divorce(
        self,
        ctx
    ):

        self.reload()
        
        if not self.married(
            ctx.author.id
        ):

            return await self.error(
                ctx,
                "You are not married."
            )

        partner_id = self.data[
            "marriages"
        ][
            str(ctx.author.id)
        ][
            "partner"
        ]

        partner = self.bot.get_user(
            partner_id
        )

        if partner is None:
            try:
                partner = await self.bot.fetch_user(partner_id)
            except Exception:
                partner = None

        embed = discord.Embed(

            title="💔 Divorce",

            description=(
                f"Are you sure you want to divorce "
                f"{partner.mention if partner else 'your partner'}?\n\n"
                "This action cannot be undone."
            ),

            color=0xE74C3C

        )

        embed.set_footer(
            text="Click a button below."
        )

        await ctx.send(

            embed=embed,

            view=DivorceConfirmView(
                ctx.author
            )

        )
        
    # ------------------------------
    # CRUSH
    # ------------------------------

    @commands.hybrid_command(
        name="crush",
        description="See your crush compatibility."
    )
    async def crush(
        self,
        ctx,
        member: discord.Member
    ):

        self.reload()
        
        if member.bot:

            return await self.error(
                ctx,
                "Bots can't be your crush."
            )

        if member == ctx.author:

            return await self.error(
                ctx,
                "You can't crush on yourself."
            )

        percent = random.randint(
            1,
            100
        )

        if percent >= 90:
            text = "A perfect match! ❤️"
        elif percent >= 70:
            text = "Looks very promising! 💕"
        elif percent >= 50:
            text = "Not bad at all! 😊"
        elif percent >= 25:
            text = "Maybe... 🤔"
        else:
            text = "Better stay friends. 😅"

        embed = discord.Embed(

            title="💖 Crush Calculator",

            description=(
                f"{ctx.author.mention} ❤️ {member.mention}\n\n"
                f"Compatibility: **{percent}%**\n\n"
                f"{text}"
            ),

            color=0xFF69B4

        )

        await ctx.send(
            embed=embed
        )

    # ------------------------------
    # SHIP
    # ------------------------------

    @commands.hybrid_command(
        name="ship",
        description="Ship two users."
    )
    async def ship(
        self,
        ctx,
        user1: discord.Member,
        user2: discord.Member
    ):

        self.reload()
        
        if user1.bot or user2.bot:

            return await self.error(
                ctx,
                "Bots can't be shipped."
            )

        percent = random.randint(
            1,
            100
        )

        ship_name = (
            user1.display_name[:len(user1.display_name)//2]
            +
            user2.display_name[len(user2.display_name)//2:]
        )

        embed = discord.Embed(

            title="💘 Ship",

            description=(
                f"{user1.mention} ❤️ {user2.mention}\n\n"
                f"Compatibility: **{percent}%**\n"
                f"Ship Name: **{ship_name}**"
            ),

            color=0xE91E63

        )

        embed.set_footer(
            text="Love is in the air ❤️"
        )

        view = ShipView(
            self.bot,
            user1,
            user2,
            self.ship_callback
        )

        await ctx.send(
            embed=embed,
            view=view
        )
       
    async def ship_callback(
        self,
        interaction: discord.Interaction,
        user1: discord.Member,
        user2: discord.Member,
        view,
        mode: str = "random"
    ):

        if mode == "random":
            percentage = random.randint(1, 100)

        elif mode == "love":
            current = random.randint(1, 100)
            percentage = min(100, current + random.randint(5, 15))

        elif mode == "hate":
            current = random.randint(1, 100)
            percentage = max(1, current - random.randint(5, 15))
        # Ensure we have proper User/User-like objects for mentions
        user1_obj = user1
        user2_obj = user2

        user1_id = getattr(user1, "id", None)
        if user1_id:
            user1_obj = self.bot.get_user(user1_id) or None
            if user1_obj is None:
                try:
                    user1_obj = await self.bot.fetch_user(user1_id)
                except Exception:
                    user1_obj = user1

        user2_id = getattr(user2, "id", None)
        if user2_id:
            user2_obj = self.bot.get_user(user2_id) or None
            if user2_obj is None:
                try:
                    user2_obj = await self.bot.fetch_user(user2_id)
                except Exception:
                    user2_obj = user2

        view.user1 = user1_obj
        view.user2 = user2_obj

        name1 = getattr(user1_obj, "display_name", None) or getattr(user1_obj, "name", str(user1_obj))
        name2 = getattr(user2_obj, "display_name", None) or getattr(user2_obj, "name", str(user2_obj))

        ship_name = (
            name1[: len(name1) // 2] + name2[len(name2) // 2 :]
        )

        embed = discord.Embed(
            title="💘 Ship",
            description=(
                f"{getattr(user1_obj, 'mention', str(user1_obj))} ❤️ {getattr(user2_obj, 'mention', str(user2_obj))}\n\n"
                f"Compatibility: **{percentage}%**\n"
                f"Ship Name: **{ship_name}**"
            ),
            color=discord.Color.random(),
        )

        embed.set_footer(text="Love is in the air ❤️")

        await interaction.response.send_message(
            embed=embed,
            view=view
        )

    # ------------------------------
    # ADOPT
    # ------------------------------

    @commands.hybrid_command(
        name="adopt",
        description="Adopt a child."
    )
    async def adopt(
        self,
        ctx,
        member: discord.Member
    ):

        self.reload()
        
        if member.bot:

            return await self.error(
                ctx,
                "You can't adopt a bot."
            )

        if member == ctx.author:

            return await self.error(
                ctx,
                "You can't adopt yourself."
            )

        if not self.married(ctx.author.id):

            return await self.error(
                ctx,
                "You must be married before adopting."
            )

        if str(member.id) in self.data["parents"]:

            return await self.error(
                ctx,
                "This user has already been adopted."
            )

        partner = self.bot.get_user(

            self.data["marriages"][
                str(ctx.author.id)
            ]["partner"]

        )

        embed = discord.Embed(

            title="👶 Adoption Request",

            description=(
                f"{ctx.author.mention} ❤️ {partner.mention}\n\n"
                f"want to adopt {member.mention}.\n\n"
                "Do you accept?"
            ),

            color=0x3498DB

        )

        await ctx.send(

            content=member.mention,

            embed=embed,

            view=AdoptView(

                ctx.author,
                partner,
                member

            )

        )

    # ------------------------------
    # FAMILY
    # ------------------------------

    @commands.hybrid_command(
        name="family",
        description="View your family."
    )
    async def family(
        self,
        ctx,
        member: discord.Member = None
    ):

        self.reload()
        
        member = member or ctx.author

        if not self.married(member.id):

            return await self.error(
                ctx,
                "This user is not married."
            )

        data = self.data["marriages"][
            str(member.id)
        ]

        partner = self.bot.get_user(
            data["partner"]
        )

        if partner is None:
            try:
                partner = await self.bot.fetch_user(data["partner"])
            except Exception:
                partner = None

        children = []

        for child_id in data["children"]:

            user = self.bot.get_user(
                child_id
            )

            if user:

                children.append(
                    f"• {user.mention}"
                )

        embed = discord.Embed(

            title="👨‍👩‍👧 Family",

            color=0x5865F2

        )

        embed.add_field(

            name="❤️ Partner",

            value=partner.mention,

            inline=False

        )

        embed.add_field(

            name="👶 Children",

            value="\n".join(children)
            if children
            else "No children",

            inline=False

        )

        await ctx.send(
            embed=embed
        )


async def setup(bot):

    await bot.add_cog(
        Relationship(bot)
    )
