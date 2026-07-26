from discord.ext import commands

import discord

# --------------------------------------------------

# BOT OWNER CHECK

# --------------------------------------------------

def is_owner():

    async def predicate(ctx: commands.Context):

        if await ctx.bot.is_owner(ctx.author):

            return True

        raise commands.CheckFailure("You must be the bot owner to use this command.")

    return commands.check(predicate)

# --------------------------------------------------

# ADMIN CHECK

# --------------------------------------------------

def is_admin():

    async def predicate(ctx: commands.Context):

        if ctx.author.guild_permissions.administrator:

            return True

        raise commands.MissingPermissions(["administrator"])

    return commands.check(predicate)

# --------------------------------------------------

# MODERATOR CHECK

# --------------------------------------------------

def is_moderator():

    async def predicate(ctx: commands.Context):

        perms = ctx.author.guild_permissions

        if perms.kick_members or perms.ban_members or perms.moderate_members:

            return True

        raise commands.MissingPermissions(

            ["kick_members / ban_members / moderate_members"]

        )

    return commands.check(predicate)

# --------------------------------------------------

# MANAGE GUILD CHECK

# --------------------------------------------------

def can_manage_guild():

    async def predicate(ctx: commands.Context):

        if ctx.author.guild_permissions.manage_guild:

            return True

        raise commands.MissingPermissions(["manage_guild"])

    return commands.check(predicate)

# --------------------------------------------------

# BOT PERMISSION CHECK

# --------------------------------------------------

def bot_has_perms(**perms):

    async def predicate(ctx: commands.Context):

        missing = [

            perm.replace("_", " ")

            for perm, value in perms.items()

            if value and not getattr(ctx.guild.me.guild_permissions, perm)

        ]

        if missing:

            raise commands.BotMissingPermissions(missing)

        return True

    return commands.check(predicate)

# --------------------------------------------------

# VOICE CHECK (for music)

# --------------------------------------------------

def in_voice_channel():

    async def predicate(ctx: commands.Context):

        if ctx.author.voice and ctx.author.voice.channel:

            return True

        raise commands.CheckFailure("You must be connected to a voice channel.")

    return commands.check(predicate)