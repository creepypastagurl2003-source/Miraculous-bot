import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

# ── Category data ─────────────────────────────────────────────────────────────
# Each category: name, emoji, color, list of (usage, description) tuples

CATEGORIES = [
    {
        "label":   "Profile & Collection",
        "emoji":   "🃏",
        "value":   "profile",
        "color":   0xFF88AA,
        "desc":    "Build your Miraculous identity — hero card, bio, and character collection.",
        "commands": [
            ("`/profile [user]`",          "View your (or someone's) Miraculous hero profile card"),
            ("`/setbio <text>`",           "Set your profile bio (up to 200 characters)"),
            ("`/setquote <text>`",         "Set a personal quote shown on your card"),
            ("`/setcolor <color>`",        "Choose your profile embed colour"),
            ("`/dropcard`",               "✨ Open the Miracle Box — draw a random character card!"),
            ("`/collection [user]`",       "View all your collected Miraculous characters"),
            ("`/setcharacter <name>`",     "Set your active hero shown on your profile"),
            ("`/character list [rarity]`", "Browse every collectible character by rarity"),
            ("`/character catch <name>`",  "Catch a specific character (costs Miraculons for rare+)"),
        ],
    },
    {
        "label":   "Economy",
        "emoji":   "💰",
        "value":   "economy",
        "color":   0xFFD700,
        "desc":    "Earn, spend, and manage your Miraculons — the server currency.",
        "commands": [
            ("`/economy balance [user]`",         "Check your or someone's Miraculons balance"),
            ("`/economy daily`",                  "Claim your daily Miraculons reward"),
            ("`/economy weekly`",                 "Claim your weekly bonus Miraculons"),
            ("`/economy work`",                   "Do some work and earn Miraculons"),
            ("`/economy crime`",                  "Risk a crime for a big payout — or a fine!"),
            ("`/economy gamble <amount>`",         "Double or nothing on your Miraculons"),
            ("`/economy rob <user>`",             "Try to rob another member's wallet"),
            ("`/economy pay <user> <amount>`",    "Send Miraculons to another member"),
            ("`/economy leaderboard`",            "See the richest members in the server"),
            ("`/economy shop`",                   "Browse the Miraculous item shop"),
            ("`/economy buy <item>`",             "Buy an item from the shop"),
            ("`/economy inventory`",              "View the items in your inventory"),
            ("`/economy give <user> <amount>`",   "⚙️ Admin: give Miraculons to a user"),
            ("`/economy take <user> <amount>`",   "⚙️ Admin: take Miraculons from a user"),
            ("`/economy reset <user>`",           "⚙️ Admin: reset a user's economy data"),
        ],
    },
    {
        "label":   "Marriage & Shipping",
        "emoji":   "💑",
        "value":   "marriage",
        "color":   0xFF0044,
        "desc":    "Propose, marry, ship, and rank your romantic connections.",
        "commands": [
            ("`/propose <user>`",                     "Propose marriage to another user"),
            ("`/marry <user>`",                       "Alias for /propose"),
            ("`/accept`",                             "Accept a pending marriage proposal"),
            ("`/reject`",                             "Reject a pending proposal"),
            ("`/divorce`",                            "Divorce your current spouse"),
            ("`/spouse [user]`",                      "View your (or someone's) spouse"),
            ("`/ship <user1> <user2>`",               "Check the compatibility % of two users"),
            ("`/shipmyself <user>`",                  "Ship yourself with another user"),
            ("`/shipfamily [user]`",                  "Ship a user with all their family members"),
            ("`/shiprank <u1> <u2> [u3] [u4] [u5]`", "Rank up to 5 users' compatibility with you"),
        ],
    },
    {
        "label":   "Family Tree",
        "emoji":   "👨‍👩‍👧",
        "value":   "family",
        "color":   0x2D6A4F,
        "desc":    "Build a family — adopt members, manage relationships, and view your tree.",
        "commands": [
            ("`/family adopt <user>`",    "Send an adoption request to a user"),
            ("`/family accept`",          "Accept a pending adoption request"),
            ("`/family decline`",         "Decline a pending adoption request"),
            ("`/family disown <user>`",   "Remove a child from your family"),
            ("`/family emancipate`",      "Leave your parent's family"),
            ("`/family tree [user]`",     "View someone's full family tree"),
            ("`/family parent [user]`",   "View your parent (or someone else's)"),
        ],
    },
    {
        "label":   "Kwami System",
        "emoji":   "✨",
        "value":   "kwami",
        "color":   0xAA44FF,
        "desc":    "Discover and bond with a magical Kwami companion.",
        "commands": [
            ("`/kwami discover`",      "Bond with a random Kwami!"),
            ("`/kwami info [user]`",   "View your (or someone's) bonded Kwami"),
            ("`/kwami list`",          "See all available Kwamis"),
            ("`/kwami transform`",     "Use your Kwami's special power"),
            ("`/kwami release`",       "Release your Kwami and search for a new one"),
        ],
    },
    {
        "label":   "Miraculous Info",
        "emoji":   "📖",
        "value":   "miraculous",
        "color":   0xFF0000,
        "desc":    "Look up Miraculous Ladybug characters, powers, and lore.",
        "commands": [
            ("`/miraculous character <name>`",         "Look up a Miraculous character"),
            ("`/miraculous list`",                     "List all available characters"),
            ("`/miraculous random`",                   "Get info on a random character"),
            ("`/miraculous kwami <kwami>`",            "Find a character by their Kwami"),
            ("`/miraculous compare <char1> <char2>`",  "Compare two characters side by side"),
        ],
    },
    {
        "label":   "Quote Book",
        "emoji":   "📝",
        "value":   "quotes",
        "color":   0x4488FF,
        "desc":    "Save and recall memorable quotes from your server.",
        "commands": [
            ("`/quote add <quote> [author]`",  "Add a quote to the server's quote book"),
            ("`/quote get <id>`",              "Retrieve a specific quote by ID"),
            ("`/quote random`",               "Get a random quote from the book"),
            ("`/quote list`",                 "See the most recent quotes"),
            ("`/quote search <keyword>`",      "Search quotes by keyword or author"),
            ("`/quote delete <id>`",           "⚙️ Admin: delete a quote"),
            ("`/quote stats`",                "View quote statistics for this server"),
        ],
    },
    {
        "label":   "AI Chat",
        "emoji":   "🤖",
        "value":   "ai",
        "color":   0x00CCFF,
        "desc":    "Chat with Miraculous Bot's built-in AI personality.",
        "commands": [
            ("`/ai chat <message>`",         "Chat with Miraculous Bot AI"),
            ("`/ai reset`",                  "Clear the AI conversation history for this channel"),
            ("`/ai setchannel <channel>`",   "⚙️ Admin: set a channel for auto AI responses"),
            ("`/ai personality`",            "Learn about the AI's personality"),
        ],
    },
    {
        "label":   "Games",
        "emoji":   "🎮",
        "value":   "games",
        "color":   0xFF6B00,
        "desc":    "Fun mini-games, dice, slots, and interactive activities.",
        "commands": [
            ("`/8ball <question>`",          "Ask the Miracle Box a yes/no question"),
            ("`/coinflip`",                  "Flip a coin"),
            ("`/roll [dice]`",               "Roll dice — supports notation like `2d6`, `1d20`"),
            ("`/slots`",                     "Spin the slot machine 🎰"),
            ("`/rps <choice>`",              "Play Rock Paper Scissors against the bot"),
            ("`/trivia`",                    "Answer a random trivia question"),
            ("`/wyr`",                       "Would you rather...? A random dilemma"),
            ("`/truth`",                     "Get a random truth question"),
            ("`/dare`",                      "Get a random dare"),
            ("`/choose <options>`",          "Can't decide? Let the bot pick for you"),
            ("`/rate <thing>`",              "Let the bot rate absolutely anything"),
            ("`/hug <user>`",                "Give someone a warm Miraculous hug 🤗"),
        ],
    },
    {
        "label":   "Miraculous Fun",
        "emoji":   "🌸",
        "value":   "fun",
        "color":   0xFF88CC,
        "desc":    "Spammable fun commands — quotes, roasts, moods, and more.",
        "commands": [
            ("`/kwamiquote`",   "Random quote from a Kwami (Tikki, Plagg, Wayzz…)"),
            ("`/heroquote`",    "Inspiring quote from a Miraculous hero"),
            ("`/villainquote`", "Dramatic monologue from a villain"),
            ("`/funfact`",      "Random Miraculous fun fact"),
            ("`/compliment`",   "Receive a wholesome Miraculous-themed compliment"),
            ("`/roast`",        "Get a light, Miraculous-themed roast"),
            ("`/mood`",         "Get your random Miraculous mood of the moment"),
        ],
    },
    {
        "label":   "Notifications",
        "emoji":   "🔔",
        "value":   "notifications",
        "color":   0xFF0000,
        "desc":    "Get notified when your favourite YouTube channels or Twitch streamers go live.",
        "commands": [
            ("`/youtube_notify add <channel_id> <#channel>`",    "Subscribe to a YouTube channel's uploads"),
            ("`/youtube_notify remove <channel_id>`",            "Remove a YouTube notification"),
            ("`/youtube_notify list`",                           "List YouTube subscriptions in this server"),
            ("`/youtube_notify test <channel_id>`",              "Send a test YouTube notification"),
            ("`/twitch_notify add <streamer> <#channel>`",       "Subscribe to a Twitch streamer"),
            ("`/twitch_notify remove <streamer>`",               "Remove a Twitch notification"),
            ("`/twitch_notify list`",                            "List Twitch subscriptions in this server"),
            ("`/twitch_notify test <streamer>`",                 "Send a test Twitch notification"),
        ],
    },
    {
        "label":   "Reaction Roles",
        "emoji":   "🎭",
        "value":   "reactionroles",
        "color":   0x8844FF,
        "desc":    "Let members assign themselves roles by reacting to a panel.",
        "commands": [
            ("`/reactionrole create`",                         "Create a reaction role panel"),
            ("`/reactionrole add <panel_id> <emoji> <role>`",  "Add an emoji → role mapping"),
            ("`/reactionrole remove <panel_id> <emoji>`",      "Remove an emoji → role mapping"),
            ("`/reactionrole list`",                           "List all panels in this server"),
            ("`/reactionrole delete <panel_id>`",              "Delete an entire panel"),
            ("`/reactionrole edit <panel_id>`",                "Edit a panel's title or description"),
            ("`!rr create`",                                   "Prefix alias for reaction role setup"),
        ],
    },
    {
        "label":   "Moderation",
        "emoji":   "🛡️",
        "value":   "mod",
        "color":   0xAAAAAA,
        "desc":    "Server moderation tools for admins and moderators.",
        "commands": [
            ("`/clear <amount>`", "Delete a number of messages from this channel"),
        ],
    },
]

# Quick lookup by value
CAT_BY_VALUE = {c["value"]: c for c in CATEGORIES}


# ── Overview embed ────────────────────────────────────────────────────────────

def build_overview_embed(bot_user: discord.ClientUser) -> discord.Embed:
    embed = discord.Embed(
        title="✨  Miraculous Bot  —  Help",
        description=(
            "Welcome to **Miraculous Bot ✨**!\n"
            "Use the dropdown below to browse commands by category.\n\n"
            f"**{sum(len(c['commands']) for c in CATEGORIES)} commands** across **{len(CATEGORIES)} categories**"
        ),
        color=0xFF0000,
    )

    for cat in CATEGORIES:
        count = len(cat["commands"])
        embed.add_field(
            name=f"{cat['emoji']} {cat['label']}",
            value=f"`{count}` command{'s' if count != 1 else ''}",
            inline=True,
        )

    embed.set_thumbnail(url=bot_user.display_avatar.url)
    embed.set_footer(text="✨ Miraculous Bot  •  Select a category to see its commands")
    return embed


# ── Category embed ────────────────────────────────────────────────────────────

def build_category_embed(cat: dict, bot_user: discord.ClientUser) -> discord.Embed:
    embed = discord.Embed(
        title=f"{cat['emoji']}  {cat['label']}",
        description=cat["desc"],
        color=cat["color"],
    )

    lines = []
    for usage, desc in cat["commands"]:
        lines.append(f"{usage}\n╰ {desc}")

    # Split into at most two fields to stay within Discord limits
    mid = (len(lines) + 1) // 2
    embed.add_field(name="\u200b", value="\n\n".join(lines[:mid]), inline=True)
    if lines[mid:]:
        embed.add_field(name="\u200b", value="\n\n".join(lines[mid:]), inline=True)

    embed.set_thumbnail(url=bot_user.display_avatar.url)
    embed.set_footer(
        text=f"✨ Miraculous Bot  •  {len(cat['commands'])} command{'s' if len(cat['commands']) != 1 else ''}  •  ⚙️ = admin only"
    )
    return embed


# ── Select menu ───────────────────────────────────────────────────────────────

class CategorySelect(discord.ui.Select):
    def __init__(self, bot_user: discord.ClientUser):
        self.bot_user = bot_user
        options = [
            discord.SelectOption(
                label=cat["label"],
                value=cat["value"],
                emoji=cat["emoji"],
                description=cat["desc"][:100],
            )
            for cat in CATEGORIES
        ]
        super().__init__(
            placeholder="📂  Choose a category…",
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction: discord.Interaction):
        cat = CAT_BY_VALUE[self.values[0]]
        embed = build_category_embed(cat, self.bot_user)
        await interaction.response.edit_message(embed=embed, view=self.view)


class OverviewButton(discord.ui.Button):
    def __init__(self, bot_user: discord.ClientUser):
        self.bot_user = bot_user
        super().__init__(label="🏠 Overview", style=discord.ButtonStyle.secondary, row=1)

    async def callback(self, interaction: discord.Interaction):
        embed = build_overview_embed(self.bot_user)
        await interaction.response.edit_message(embed=embed, view=self.view)


class HelpView(discord.ui.View):
    def __init__(self, bot_user: discord.ClientUser, author_id: int):
        super().__init__(timeout=120)
        self.author_id = author_id
        self.add_item(CategorySelect(bot_user))
        self.add_item(OverviewButton(bot_user))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.followup.send(
                "❌ Only the person who ran `/help` can navigate this menu.",
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


# ── Cog ───────────────────────────────────────────────────────────────────────

class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Browse all Miraculous Bot commands by category! ✨")
    @app_commands.describe(category="Jump straight to a category (optional)")
    @app_commands.choices(category=[
        app_commands.Choice(name=f"{c['emoji']} {c['label']}", value=c["value"])
        for c in CATEGORIES
    ])
    async def help_command(self, interaction: discord.Interaction, category: Optional[str] = None):
        await interaction.response.defer()
        bot_user = self.bot.user

        if category:
            cat = CAT_BY_VALUE.get(category)
            if cat:
                embed = build_category_embed(cat, bot_user)
            else:
                embed = build_overview_embed(bot_user)
        else:
            embed = build_overview_embed(bot_user)

        view = HelpView(bot_user=bot_user, author_id=interaction.user.id)
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
