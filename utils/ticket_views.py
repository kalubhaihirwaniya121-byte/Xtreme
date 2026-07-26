import discord
import json
from discord.ui import Button, View

SETTINGS_FILE = "data/ticket_settings.json"
COUNTER_FILE = "data/ticket_counter.json"
OPEN_FILE = "data/open_tickets.json"


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="General Support",
                emoji="📞",
                value="general"
            ),
            discord.SelectOption(
                label="Bug Report",
                emoji="🐛",
                value="bug"
            ),
            discord.SelectOption(
                label="Billing",
                emoji="💰",
                value="billing"
            ),
            discord.SelectOption(
                label="Partnership",
                emoji="🤝",
                value="partnership"
            ),
            discord.SelectOption(
                label="Other",
                emoji="📝",
                value="other"
            )
        ]

        super().__init__(
            placeholder="Select ticket category...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_dropdown"
        )

    async def callback(self, interaction: discord.Interaction):

        settings = load_json(SETTINGS_FILE)
        guild_id = str(interaction.guild.id)

        if guild_id not in settings:
            return await interaction.response.send_message(
                "❌ Ticket system is not configured.",
                ephemeral=True
            )

        open_tickets = load_json(OPEN_FILE)

        if str(interaction.user.id) in open_tickets:
            return await interaction.response.send_message(
                "❌ You already have an open ticket.",
                ephemeral=True
            )

        counter = load_json(COUNTER_FILE)
        counter["counter"] = counter.get("counter", 0) + 1
        save_json(COUNTER_FILE, counter)

        category_name = self.values[0]

        channel_name = (
            f"{category_name}-{interaction.user.name}"
        ).lower().replace(" ", "-")

        category = interaction.guild.get_channel(
            settings[guild_id]["category"]
        )

        support_role = interaction.guild.get_role(
            settings[guild_id]["support_role"]
        )

        overwrites = {
            interaction.guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            interaction.user:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                ),

            interaction.guild.me:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True
                )
        }

        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )

        channel = await interaction.guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        open_tickets[str(interaction.user.id)] = channel.id
        save_json(OPEN_FILE, open_tickets)

        await interaction.response.send_message(
            f"✅ Ticket created: {channel.mention}",
            ephemeral=True
        )

        embed = discord.Embed(
            title="🎫 Ticket Created",
            description=(
                f"{interaction.user.mention}, "
                "please explain your issue."
            ),
            color=0x5865F2
        )

        await channel.send(
    content=(
        f"{interaction.user.mention} "
        f"{support_role.mention if support_role else ''}"
    ),
    embed=embed,
    view=TicketControls()
)


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(TicketDropdown())
        
        
class TicketControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close",
        emoji="🔒",
        style=discord.ButtonStyle.secondary,
        custom_id="ticket_close"
    )
    async def close_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "🔒 Ticket closed.",
            ephemeral=True
        )

    @discord.ui.button(
        label="Delete",
        emoji="🗑️",
        style=discord.ButtonStyle.danger,
        custom_id="ticket_delete"
    )
    async def delete_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        open_tickets = load_json(OPEN_FILE)

        for uid, channel_id in list(open_tickets.items()):
            if channel_id == interaction.channel.id:
                del open_tickets[uid]
                break

        save_json(OPEN_FILE, open_tickets)

        await interaction.response.send_message(
            "🗑️ Deleting ticket...",
            ephemeral=True
        )

        await interaction.channel.delete()

    @discord.ui.button(
        label="Transcript",
        emoji="📄",
        style=discord.ButtonStyle.primary,
        custom_id="ticket_transcript"
    )
    async def transcript(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_message(
            "⚠️ Transcript system coming soon.",
            ephemeral=True
        )