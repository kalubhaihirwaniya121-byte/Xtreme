
from utils.emojis import Emojis

HELP_CATEGORIES = {
    "Moderation": {
        "emoji": f"{Emojis.MOD}",
        "components": [
            {
                "type": "text",
                "content": """### Moderation\n
                `ban`, `kick`, `mute`, `unmute`, `warn`\n"""
            },
            {
                "type": "separator"
            },
            {
                "type": "text",
                "content": """### Automod\n
                `automod`, `automod enable`, `automod disable`, `automod punishment`,`automod antilinks enable`, `automod antilinks disable`, `automod spam enable`, `automod spam disable`,`automod invites enable/disable`,`automod maxmentions`,`automod bypass`,`automod bypass add`,`automod bypass remove`,`automod bypass list`,`badwords`,`badwords add`,`badwords remove`,`badwords list`\n"""
            },
            {
                "type": "separator"
            },
            {
                "type": "text",
                "content": """### Antinuke\n
                `antinuke`, `antinuke on/off`,`antinuke status`,`antinuke log #channel`,`antinukewhitelist add/remove/list`\n"""
            },
            {
                "type": "separator"
            },
            {
                "type": "text",
                "content": """### Logging\n
                `logging`, `logging setup`,`logging status`,`logging remove`,`logging reset`\n"""
            }
        ]
    },

    "UTILITY" : {
        "emoji": f"{Emojis.TOOLS}",
        "components": [
            {
                "type": "text",
                "content": """### General\n
                `setprefix <new_prefix>`, `noprefix on/off`, `userinfo`,`serverinfo`,`afk`,`warn`\n"""
            },
            {
                "type": "separator"
            },
            {
                "type": "text",
                "content": """### Giveways\n
                `gstart`,`gend`,`greroll`,`glist`\n"""
            }, 
            {
                "type": "separator"
            },
            {
                "type": "text",
                "content": """### Setuprole\n
                `setuprole`,`setuprole add`,`setuprole remove`,`setuprole list`,`setuprole reset`\n"""
            }
        ]
    },  

    "EXTRA" : {
        "emoji": f"{Emojis.STAR}",
        "components": [
            {
                "type": "text",
                "content": """### Autoresponder\n
                `autoresponder`,`autoresponder add <trigger> | <response>`, `autoresponder remove <trigger>`, `autoresponder list`\n"""
            },
            {
                "type": "separator"
            },
            {
                "type": "text",
                "content": """### Botcleaner\n
                `bot <no of msg>`,`botc set #channel <second>`, `botc off #channel`,`botc status`,`botc bypass add <bot_id>`,`botc bypass remove <bot_id>`,`botc bypass list`\n"""
            }, 
            {
                "type": "separator"
            },
            {
                "type": "text",
                "content": """### Ticket\n
                `ticket`,`ticket setup`,`ticket category add/remove/list`,`ticket supportrole @role`,`ticket logs #channel`\n"""
            },
            {
                "type": "separator"
            },
            {
                "type": "text",
                "content": """### Media System\n
                `media on`,`media off`,`media status`,`mediachannel add/remove #channel`,`mediachannel list`,`mediabypass add/remove @role`,`mediabypass list`\n"""
            }
        ]
    },  
    "MINIGAMES" : {
        "emoji" : f"{Emojis.GAME}",
        "components" : [
            {   
                "type" : "text",
                "content" : """### Counting\n
                `counting`,`counting set #channel`,`counting remove`,`counting reset`,`counting leaderboard`,`counting stats`\n"""
            },
            {
                "type" : "separator"
            },
            {
                "type" : "text",
                "content" : """### Truth or Dare\n
                `tod`,`truth`,`dare`\n"""
            }
        ]    
    },
    "Loveyapa" : {
        "emoji" : f"{Emojis.HEART}",
        "components" : [
            {
                "type" : "text",
                "content" : """### Relationship\n
                `relationship`,`propose`,`marry`,`partner`,`divorce`,`family`,`adopt`,`crush`,`ship`,`loveletter`\n"""
            },
            {
                "type" : "separator"
            },
            {
                "type" : "text",
                "content" : """### Actions\n
                `kiss`,`hug`,`cuddle`,`slap`,`pat`,`poke`,`gift`,`wave`,`holdhand`\n"""
            }
        ]
    },
    "Channel Management" : {
        "emoji" : f"{Emojis.UTILITY}",
        "components" : [
            {
                "type" : "text",
                "content" : """### Channel Management\n
                `lock`,`unlock`,`slowmode`,`hide`,`unhide`,`rename`,`topic`,`channelcreate`,`channeldelete`,`vccreate`,`vcdelete`,`nsfw`,`nuke`,`categorycreate`,`categrydelete`,`clone`,`stckymsg #channel <msg>`,`unsticky #channel`,`stickylist`,`snipe`,`editsnipe`,`purge`\n"""
            },
            {
                "type" : "separator"
            },
            {
                "type" : "text",
                "content" : """### Welcomer\n
                `welcomer enable/disable`,`welcomestatus`,`welcomechannel #channel`,`welcomemessage <text>`,`welcomedm on/off`,`welcometest`,`autorole add/remove/list`"""
            }
        ]
    },
    "Bot Setting" : {
        "emoji" : f"{Emojis.SETTING}",
        "components" : [
            {
                "type" : "text",
                "content" : """### Bot Settings\n
                `customize`\n
                `customize avatar <url/attachment>`\n
                `customize banner <url/attachment>`\n
                `customize nick <name>`\n
                `customize bio <text>`\n"""
            },
            {
                "type" : "separator"
            },
            {
                "type" : "text",
                "content" : """### Important\n
                To customize bot in your server, you need to have permission from bot developer team.
                here is the [link](https://discord.gg/JudaEhQ48U) to join the support server and get permission from the bot developer team."""
            }
        ]
    }
}