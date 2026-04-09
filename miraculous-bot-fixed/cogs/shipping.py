import discord
from discord import app_commands
from discord.ext import commands
import hashlib
import json
import os
import random
from typing import Optional

FAMILY_DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "family.json")
MARRIAGE_DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "marriages.json")

SHIP_NAMES = [
    ("🌹", "a passionate romance"),
    ("🌸", "a gentle love story"),
    ("⚡", "an electric connection"),
    ("🌊", "a deep, flowing bond"),
    ("🔥", "a fiery affair"),
    ("🌙", "a dreamy relationship"),
    ("🦋", "a transformative pairing"),
    ("🌺", "a blossoming friendship turning into love"),
    ("💫", "a destined encounter"),
    ("🎭", "an intriguing, complex relationship"),
]

RATING_TIERS = [
    (0, 10, "💀", [
        "Absolute disaster. RUN. Do not look back.",
        "The stars said no. The moon said no. Even the clouds said no.",
        "This ship has sunk before it left the dock.",
        "They would argue over the direction to breathe.",
        "Not even in another universe.",
        "The compatibility test crashed trying to process this.",
        "Two magnets — except both are the same pole. Forever repelling.",
        "Scientists have classified this pairing as a natural hazard.",
        "The ship sailed. It immediately hit an iceberg. Then a second one.",
        "Even the Kwamis refuse to comment on this one.",
        "Tikki and Plagg looked at this score and flew away.",
        "This duo would cause an akumatization just by being in the same room.",
    ]),
    (11, 20, "💔", [
        "Not looking great... maybe try again in another lifetime.",
        "There's potential — if you ignore all the red flags.",
        "The vibe is off. Very off. Like, astronomically off.",
        "I've seen better chemistry in a bag of air.",
        "Possible, but deeply unlikely.",
        "The universe tried to make this work. It gave up after 20 seconds.",
        "Like oil and water, but with more eye-rolling.",
        "They'd need couples therapy before they even start dating.",
        "Someone's going to end up akumatized by the end of this.",
        "Hawk Moth has already sensed the negativity from this pairing.",
        "The Miracle Box shuddered when it processed this result.",
        "There's a spark — but it's the kind that starts a fire in a bad way.",
    ]),
    (21, 35, "😬", [
        "It's... complicated. Like a math problem nobody asked for.",
        "They could work — if one of them changes everything about themselves.",
        "50% disaster, 50% chaotic fun. Jury's still out.",
        "Friends? Maybe. Romance? Tread carefully.",
        "There's a tiny spark. It's very, very tiny.",
        "This ship is the definition of 'it's complicated' on social media.",
        "Equal parts chemistry and chaos. Mostly chaos.",
        "They'd be a great team — in a crisis, and only in a crisis.",
        "Mutual vibes of 'I tolerate you' with occasional 'you're kind of cute'.",
        "The fanfic writers would have a field day. That's about all though.",
        "They'd orbit each other for years without ever actually committing.",
        "Slow burn — emphasis on the burn. Possibly literal.",
    ]),
    (36, 50, "🤷", [
        "Could go either way — like a coin flip but with feelings.",
        "Not terrible, not great. Solidly mid in the best way.",
        "There's something here, but it's hiding and won't come out.",
        "The vibe is: chaotic neutral love story.",
        "They'd have to try really hard. But it *could* work.",
        "The algorithm shrugs. Feelings unclear. Please consult the Miracle Box.",
        "Somewhere between 'just friends' and 'what are we doing'.",
        "They'd make a great team if someone would just say something already.",
        "The fortune cookie said: 'Maybe.' That's the whole reading.",
        "Not enemies. Not lovers. Just two people in an unresolved subplot.",
        "The stars are on the fence. They've been on the fence for a while.",
        "Could be a slow burn. Could be nothing. Only one way to find out.",
    ]),
    (51, 65, "😊", [
        "There's definitely something there! Don't ignore it!",
        "Good energy! The universe is rooting for them, softly.",
        "More than just friends? The signs say yes!",
        "Solid foundation. A slow burn with a very cute ending.",
        "Chemistry detected! Please proceed with butterflies.",
        "Comfortable, warm, easy — the best kind of love story start.",
        "The Ladyblog would post a full article about this ship.",
        "They light up around each other. Just saying.",
        "Someone is definitely catching feelings. The algorithm knows.",
        "This has 'accidentally confesses at the worst possible moment' energy.",
        "Marinette could relate. This is giving very Adrienette vibes.",
        "A good pairing. The kind that sneaks up on everyone, including them.",
    ]),
    (66, 75, "💛", [
        "Pretty good chemistry! They bring out the best in each other.",
        "This is the 'holding hands on a walk' level of adorable.",
        "Warm, fuzzy vibes all around. This one's wholesome.",
        "The kind of ship that makes others go 'aww' involuntarily.",
        "Great compatibility — someone confess already!",
        "Sunny energy. The good kind of butterflies. All the time.",
        "They make each other better just by being around each other.",
        "This has 'writing songs about each other but playing it cool' energy.",
        "Alya has already shipped them and is planning the wedding.",
        "The kind of pairing that feels like coming home.",
        "Their friends already know. Everyone knows. Except them.",
        "A lovely connection. Whoever confesses first wins — and they both do.",
    ]),
    (76, 85, "💕", [
        "Strong connection! These two are genuinely good for each other.",
        "The stars are practically screaming. Can they hear it?",
        "This ship has smooth sailing written all over it. 🌊",
        "Main character energy — this is the love story people write fanfic about.",
        "Undeniable chemistry. Even the bot is blushing.",
        "The Miracle Box glowed pink when it computed this result.",
        "These two complete each other's sentences — and they haven't noticed yet.",
        "A Miraculous-level connection. The kwamis approve wholeheartedly.",
        "This is the ship the show would dedicate an episode arc to.",
        "Rare chemistry. The kind that doesn't come around often.",
        "Luka would write a whole album about this pairing. It'd be beautiful.",
        "They make the people around them root for them. Loudly.",
    ]),
    (86, 95, "💖", [
        "Amazing compatibility! This is a top-tier pairing.",
        "Rare. Beautiful. Someone needs to write a novel about this.",
        "The universe went out of its way to connect these two.",
        "If this were an anime, they'd be the fan-favourite ship.",
        "Extraordinary bond. Like they were literally written for each other.",
        "The Miracle Box is glowing. All the kwamis are cheering.",
        "This is the kind of bond that survives akumatizations and secrets.",
        "Destined. There is no other word.",
        "The algorithm has never been more confident in a reading. This is it.",
        "Love like this gets referenced in future seasons.",
        "They'd fight side by side and fall in love doing it. Classic.",
        "Alya is LOSING IT. The Ladyblog has three drafts ready. This is canon.",
    ]),
    (96, 99, "💞", [
        "Nearly perfect match! Just one tiny missing puzzle piece.",
        "So close to destiny it's almost unfair.",
        "Basically soulmates — they just haven't fully accepted it yet.",
        "The compatibility is almost suspicious. Did the stars have a meeting?",
        "This is the ship everyone saw coming. No surprises. Just love.",
        "One honest conversation away from something extraordinary.",
        "The Miracle Box rated this 'fated'. The kwamis are emotional.",
        "Almost flawless. The one missing piece is probably courage.",
        "This is the slowburn that pays off in the season finale.",
        "The kind of love story that makes people believe in love again.",
        "Every sign points to yes. They just need to look at the signs.",
        "The algorithm is emotional. This is rare. This is almost perfect.",
    ]),
    (100, 100, "💘", [
        "A match made in heaven! This is literally fate.",
        "Perfect score. PERFECT. The algorithm is crying tears of joy.",
        "100%! The universe planned this from the very beginning.",
        "Soulmates. Confirmed. No further questions.",
        "There are no words. Only hearts. 💘💘💘",
        "The Miracle Box burst into confetti when it saw this result.",
        "Tikki and Plagg are holding hands. That's how good this is.",
        "Even Hawk Moth stopped his evil plan to acknowledge this pairing.",
        "Master Fu himself could not have planned this better.",
        "The Ladyblog is crashing from the amount of posts being made.",
        "Miraculous-level love. The kwamis wept. The universe smiled.",
        "Lucky Charm says: true love. No further input required.",
    ]),
]


def compute_ship_score(id1: int, id2: int) -> int:
    combined = str(min(id1, id2)) + "x" + str(max(id1, id2))
    digest = hashlib.md5(combined.encode()).hexdigest()
    return int(digest[:4], 16) % 101


def make_progress_bar(score: int, length: int = 10) -> str:
    filled = round((score / 100) * length)
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {score}%"


def make_short_bar(score: int, length: int = 6) -> str:
    filled = round((score / 100) * length)
    return "█" * filled + "░" * (length - filled)


def get_tier(score: int):
    for low, high, emoji, messages in RATING_TIERS:
        if low <= score <= high:
            return emoji, random.choice(messages)
    return "❓", "Unknown"


def blend_names(name1: str, name2: str) -> str:
    half1 = name1[: max(1, len(name1) // 2)]
    half2 = name2[max(0, len(name2) // 2):]
    return half1 + half2


def load_family_data() -> dict:
    if not os.path.exists(FAMILY_DATA_FILE):
        return {"relationships": {}, "pending_adoptions": {}}
    with open(FAMILY_DATA_FILE, "r") as f:
        return json.load(f)


def load_marriage_data() -> dict:
    if not os.path.exists(MARRIAGE_DATA_FILE):
        return {"marriages": {}, "proposals": {}}
    with open(MARRIAGE_DATA_FILE, "r") as f:
        return json.load(f)


class ShippingCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ship", description="Ship two users and see their compatibility!")
    @app_commands.describe(
        user1="The first person to ship",
        user2="The second person to ship",
    )
    async def ship(
        self,
        interaction: discord.Interaction,
        user1: discord.Member,
        user2: discord.Member,
    ):
        await interaction.response.defer()
        if user1.id == user2.id:
            await interaction.followup.send(
                "❌ You can't ship someone with themselves!", ephemeral=True
            )
            return

        score = compute_ship_score(user1.id, user2.id)
        emoji, desc = get_tier(score)
        bar = make_progress_bar(score)

        digest = hashlib.md5(
            (str(min(user1.id, user2.id)) + str(max(user1.id, user2.id))).encode()
        ).hexdigest()
        ship_emoji, ship_vibe = SHIP_NAMES[int(digest[4:6], 16) % len(SHIP_NAMES)]

        ship_name = blend_names(user1.display_name, user2.display_name)

        marriage_data = load_marriage_data()
        already_married = marriage_data["marriages"].get(str(user1.id)) == str(user2.id)

        # Pick a color that scales with the score (cold → warm)
        r = min(255, 100 + int(score * 1.55))
        g = max(60, 180 - int(score * 1.2))
        b = max(100, 200 - int(score * 1.0))

        embed = discord.Embed(
            title=f"{ship_emoji}  {user1.display_name}  ×  {user2.display_name}",
            color=discord.Color.from_rgb(r, g, b),
        )

        # user1 in the author slot (icon top-left), user2 as thumbnail (top-right)
        embed.set_author(
            name=f"{user1.display_name}",
            icon_url=user1.display_avatar.url,
        )
        embed.set_thumbnail(url=user2.display_avatar.url)

        # Ship identity row
        embed.add_field(
            name="💌 Ship Name",
            value=f"**{ship_name}**",
            inline=True,
        )
        embed.add_field(
            name=f"{ship_emoji} Vibe",
            value=ship_vibe.capitalize(),
            inline=True,
        )

        # Compatibility bar
        embed.add_field(
            name=f"{emoji} Compatibility  —  **{score}%**",
            value=f"```{bar}```",
            inline=False,
        )

        # Random message for this tier
        embed.add_field(
            name="💬 Verdict",
            value=f"*{desc}*",
            inline=False,
        )

        if already_married:
            embed.add_field(
                name="💒 Already Married!",
                value="*These two are officially bound together. How sweet!*",
                inline=False,
            )

        # user1 avatar as big image at the bottom; user2 stays as thumbnail top-right
        embed.set_image(url=user1.display_avatar.url)

        embed.set_footer(
            text=f"Results are written in the stars ✨  •  {user1.display_name} & {user2.display_name}",
            icon_url=user2.display_avatar.url,
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="shipmyself", description="Ship yourself with another user!")
    @app_commands.describe(user="The user to ship yourself with")
    async def shipmyself(self, interaction: discord.Interaction, user: discord.Member):
        await self.ship.callback(self, interaction, interaction.user, user)

    @app_commands.command(name="shipfamily", description="Ship a user with all their family members!")
    @app_commands.describe(user="The user whose family to ship them with (default: yourself)")
    async def shipfamily(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.Member] = None,
    ):
        await interaction.response.defer()
        target = user or interaction.user
        target_id = str(target.id)

        family_data = load_family_data()
        rel = family_data["relationships"].get(target_id, {})
        parent_id = rel.get("parent")
        child_ids = rel.get("children", [])

        sibling_ids = []
        if parent_id:
            sibling_ids = [
                c for c in family_data["relationships"].get(parent_id, {}).get("children", [])
                if c != target_id
            ]

        marriage_data = load_marriage_data()
        spouse_id = marriage_data["marriages"].get(target_id)

        family_members: list[tuple[str, str]] = []
        if parent_id:
            family_members.append((parent_id, "Parent"))
        for sid in sibling_ids:
            family_members.append((sid, "Sibling"))
        for cid in child_ids:
            family_members.append((cid, "Child"))
        if spouse_id and not any(m[0] == spouse_id for m in family_members):
            family_members.append((spouse_id, "Spouse"))

        if not family_members:
            await interaction.followup.send(
                f"❌ {'You have' if not user else f'{target.display_name} has'} no family members to ship with yet!\n"
                f"Use `/family adopt` and `/propose` to build a family.",
                ephemeral=True,
            )
            return

        results = []
        for member_id, relation in family_members:
            if member_id == target_id:
                continue
            score = compute_ship_score(target.id, int(member_id))
            emoji, _ = get_tier(score)
            bar = make_short_bar(score)
            member = self.bot.get_user(int(member_id))
            member_name = member.display_name if member else f"<@{member_id}>"
            results.append((score, emoji, bar, member_name, relation))

        results.sort(key=lambda x: x[0], reverse=True)

        embed = discord.Embed(
            title=f"💞 {target.display_name}'s Family Ship Rankings",
            color=discord.Color.from_rgb(255, 105, 180),
        )

        lines = []
        medals = ["🥇", "🥈", "🥉"]
        for i, (score, emoji, bar, name, relation) in enumerate(results):
            medal = medals[i] if i < 3 else f"#{i+1}"
            lines.append(f"{medal} **{name}** *({relation})*\n`[{bar}]` {score}% {emoji}")

        embed.description = "\n\n".join(lines) if lines else "*No results*"
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text="Fun rankings — no feelings were harmed ✨")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="shiprank", description="Rank multiple users' compatibility with you!")
    @app_commands.describe(
        user1="First user",
        user2="Second user",
        user3="Third user (optional)",
        user4="Fourth user (optional)",
        user5="Fifth user (optional)",
    )
    async def shiprank(
        self,
        interaction: discord.Interaction,
        user1: discord.Member,
        user2: discord.Member,
        user3: Optional[discord.Member] = None,
        user4: Optional[discord.Member] = None,
        user5: Optional[discord.Member] = None,
    ):
        await interaction.response.defer()
        candidates = [u for u in [user1, user2, user3, user4, user5] if u is not None]
        candidates = [u for u in candidates if u.id != interaction.user.id]

        if len(candidates) < 2:
            await interaction.followup.send(
                "❌ Please provide at least 2 different users to rank!", ephemeral=True
            )
            return

        results = []
        for candidate in candidates:
            score = compute_ship_score(interaction.user.id, candidate.id)
            emoji, desc = get_tier(score)
            bar = make_short_bar(score)
            results.append((score, emoji, bar, candidate.display_name, desc))

        results.sort(key=lambda x: x[0], reverse=True)

        embed = discord.Embed(
            title=f"💘 Ship Rankings for {interaction.user.display_name}",
            color=discord.Color.from_rgb(255, 105, 180),
        )
        medals = ["🥇", "🥈", "🥉"]
        lines = []
        for i, (score, emoji, bar, name, desc) in enumerate(results):
            medal = medals[i] if i < 3 else f"#{i+1}"
            lines.append(f"{medal} **{name}** — `[{bar}]` {score}%\n*{desc}*")

        embed.description = "\n\n".join(lines)
        embed.set_footer(text="Purely for fun • Results are written in the stars ✨")
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(ShippingCog(bot))
