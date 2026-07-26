import discord
from discord.ext import commands, tasks
from utils.emojis import Emojis

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status_index = 0
        self.rotate_status.start()

    def cog_unload(self):
        self.rotate_status.cancel()

    @tasks.loop(seconds=30)
    async def rotate_status(self):

        statuses = [

            discord.Streaming(
                name="Xtreme Music & Moderation",
                url="https://twitch.tv/discord"
            ),

            discord.Game(
                name="Jane vo kese log the jinko....."
            ),

            discord.Game(
                name=f"Lambi hai judaiya"
            ),

            discord.Activity(
                type=discord.ActivityType.watching,
                name=f"Protecting {len(self.bot.guilds)} Servers"
            ),

            discord.Activity(
                type=discord.ActivityType.watching,
                name="Mere hi isharo pe chle hai vaqt bhi"
            ),

            discord.Activity(
                type=discord.ActivityType.watching,
                name="A Premium bot"
            ),

            discord.Activity(
                type=discord.ActivityType.watching,
                name="Let's play Truth or Dare"
            ),

            discord.Activity(
                type=discord.ActivityType.watching,
                name="time to propose your crush!"
            ),

            discord.Activity(
                type=discord.ActivityType.listening,
                name="Raid Attempts 👀"
            ),

            discord.Activity(
                type=discord.ActivityType.listening,
                name=".help | Xtreme sequrity"
            ),

            discord.Activity(
                type=discord.ActivityType.listening,
                name="Lost in my world"
            ),

            discord.Activity(
                type=discord.ActivityType.listening,
                name="Kiska Rasta Dekhe"
            ),

            discord.Game(
                name="Play Xtreme Games"
            ),

            discord.Game(
                name=f" Hosting Nitro Giveway "
            ),

            discord.Streaming(
                name="Xtreme Premium Features",
                url="https://twitch.tv/discord"
            )
        ]

        await self.bot.change_presence(
            status=discord.Status.online,
            activity=statuses[self.status_index]
        )

        self.status_index = (
            self.status_index + 1
        ) % len(statuses)

    @rotate_status.before_loop
    async def before_rotate(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Status(bot))