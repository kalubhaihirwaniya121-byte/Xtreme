# ==================================================

# XTREME BOT — CONFIG FILE

# ==================================================

# -------------------------------

# BASIC BOT SETTINGS

# -------------------------------

BOT_NAME = "Xtreme"

DEFAULT_PREFIX = "."

# Put your Discord user IDs here (bot owners)

# Example: OWNER_IDS = [123456789012345678]

OWNER_IDS = []

# -------------------------------

# EMBED SETTINGS

# -------------------------------

EMBED_COLOR = 0x2f3136

SUCCESS_COLOR = 0x2ecc71

ERROR_COLOR = 0xe74c3c

INFO_COLOR = 0x3498db

FOOTER_TEXT = "Thanks for using Xtreme"

# -------------------------------

# DATABASE

# -------------------------------

DATABASE_NAME = "xtreme.db"

# -------------------------------

# AUTOMOD DEFAULTS

# -------------------------------

AUTOMOD_DEFAULTS = {

    "enabled": False,

    "antispam": True,

    "antilink": False,

    "antiinvite": True,

    "spam_limit": 5,        # messages

    "spam_time": 5,         # seconds

    "timeout_seconds": 30,  # spam punishment

}

# -------------------------------

# ANTINUKE DEFAULTS

# -------------------------------

ANTINUKE_DEFAULTS = {

    "enabled": False,

    "threshold": 3,     # actions

    "timeframe": 10,    # seconds

}

# -------------------------------

# MEDIA SYSTEM DEFAULTS

# -------------------------------

MEDIA_DEFAULTS = {

    "enabled": False

}

# -------------------------------

# WELCOMER DEFAULTS

# -------------------------------

WELCOME_DEFAULT_MESSAGE = "Welcome to the server, {user}!"

# -------------------------------

# MUSIC SETTINGS

# -------------------------------

# FFmpeg is assumed to be installed on the system

MUSIC_VOLUME = 0.5

MUSIC_QUEUE_LIMIT = 50

# -------------------------------

# HELP MENU

# -------------------------------

HELP_TIMEOUT = 120  # seconds

# ==================================================

# END OF CONFIG

# ==================================================