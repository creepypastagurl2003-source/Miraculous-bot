import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import logging
import random
from typing import Optional

logger = logging.getLogger("bot.collection")

PROFILES_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "profiles.json")

# ── Rarity config ────────────────────────────────────────────────────────────

RARITY = {
    "Common":    {"emoji": "⚪", "color": 0xAAAAAA, "cost": 0,    "badge": "[ C ]"},
    "Rare":      {"emoji": "🔵", "color": 0x4488FF, "cost": 100,  "badge": "[ R ]"},
    "Epic":      {"emoji": "🟣", "color": 0xAA44FF, "cost": 500,  "badge": "[ E ]"},
    "Legendary": {"emoji": "🟡", "color": 0xFFD700, "cost": 2000, "badge": "[★L★]"},
}

# ── Card drop system ──────────────────────────────────────────────────────────

# Weighted drop pool — (rarity, weight). Total weight = 100.
DROP_WEIGHTS = {
    "Common":    60,
    "Rare":      25,
    "Epic":      12,
    "Legendary":  3,
}

# Miraculons awarded when a user drops a card they already own
DUPLICATE_COINS = {
    "Common":     15,
    "Rare":       60,
    "Epic":      200,
    "Legendary": 800,
}

# Cooldown (seconds) per user between /dropcard uses
DROPCARD_COOLDOWN = 3600  # 1 hour

# Animated card-flip lines — cosmetic progressbar shown in the drop embed
CARD_FLIP_LINES = [
    "✨ The Miracle Box glows…",
    "🌟 A card materialises from the magic…",
    "🃏 Miraculous powers swirl around it…",
]

# ── Full collectible character roster ─────────────────────────────────────────

WIKI = "https://miraculous.fandom.com/wiki/Special:FilePath"

COLLECTIBLE_CHARACTERS: dict[str, dict] = {
    # ── Legendary ─────────────────────────────────────────────────────────────
    "ladybug": {
        "name": "Ladybug", "full_name": "Marinette Dupain-Cheng",
        "rarity": "Legendary", "emoji": "🐞", "color": 0xFF0000,
        "description": "Guardian of Paris and wielder of the Ladybug Miraculous. Lucky Charm! ✨",
        "power": "Lucky Charm & Miraculous Ladybug", "miraculous": "Earrings",
        "image": f"{WIKI}/Ladybug_Square.png",
    },
    "catnoir": {
        "name": "Cat Noir", "full_name": "Adrien Agreste",
        "rarity": "Legendary", "emoji": "🐱", "color": 0x1A1A2E,
        "description": "The purr-fect partner with the power of Cataclysm. He never gives up! 🌑",
        "power": "Cataclysm", "miraculous": "Ring",
        "image": f"{WIKI}/Cat_Noir_Square.png",
    },
    "hawkmoth": {
        "name": "Hawk Moth", "full_name": "Gabriel Agreste",
        "rarity": "Legendary", "emoji": "🦋", "color": 0x6A0DAD,
        "description": "The villain who akumatizes Parisians to steal Miraculous. His identity is Gabriel Agreste.",
        "power": "Akumatization", "miraculous": "Brooch",
        "image": f"{WIKI}/Hawk_Moth_Square.png",
    },
    "tikki": {
        "name": "Tikki", "full_name": "Tikki",
        "rarity": "Legendary", "emoji": "🍪", "color": 0xFF3333,
        "description": "The ancient Kwami of Creation and Marinette's adorable companion. She LOVES cookies! 🍪",
        "power": "Creation", "miraculous": "Ladybug Earrings",
        "image": f"{WIKI}/Tikki_Square.png",
    },
    "plagg": {
        "name": "Plagg", "full_name": "Plagg",
        "rarity": "Legendary", "emoji": "🧀", "color": 0x222244,
        "description": "The Kwami of Destruction and Adrien's lazy but powerful companion. Camembert is life. 🧀",
        "power": "Destruction", "miraculous": "Cat Ring",
        "image": f"{WIKI}/Plagg_Square.png",
    },
    "shadowmoth": {
        "name": "Shadow Moth", "full_name": "Gabriel Agreste",
        "rarity": "Legendary", "emoji": "🌑", "color": 0x2C003E,
        "description": "After merging both Miraculouses, Gabriel became Shadow Moth — twice as dangerous.",
        "power": "Akumatization & Amokization", "miraculous": "Brooch + Peacock Brooch",
        "image": f"{WIKI}/Shadow_Moth_Square.png",
    },
    # ── Epic ──────────────────────────────────────────────────────────────────
    "renarouge": {
        "name": "Rena Rouge", "full_name": "Alya Césaire",
        "rarity": "Epic", "emoji": "🦊", "color": 0xFF6B00,
        "description": "Wielder of the Fox Miraculous and master of illusions. Mirage! 🦊",
        "power": "Mirage", "miraculous": "Necklace",
        "image": f"{WIKI}/Rena_Rouge_Square.png",
    },
    "carapace": {
        "name": "Carapace", "full_name": "Nino Lahiffe",
        "rarity": "Epic", "emoji": "🐢", "color": 0x2D6A4F,
        "description": "Wielder of the Turtle Miraculous. Shell-ter protects everyone! 🐢",
        "power": "Shell-ter", "miraculous": "Bracelet",
        "image": f"{WIKI}/Carapace_Square.png",
    },
    "viperion": {
        "name": "Viperion", "full_name": "Luka Couffaine",
        "rarity": "Epic", "emoji": "🐍", "color": 0x00838F,
        "description": "Wielder of the Snake Miraculous. Second Chance rewinds time by 5 minutes. 🐍",
        "power": "Second Chance", "miraculous": "Bracelet",
        "image": f"{WIKI}/Viperion_Square.png",
    },
    "ryuko": {
        "name": "Ryuko", "full_name": "Kagami Tsurugi",
        "rarity": "Epic", "emoji": "🐉", "color": 0x003366,
        "description": "Wielder of the Dragon Miraculous. Commands water, lightning, and wind. Kameiko! 🐉",
        "power": "Kameiko", "miraculous": "Bracelet",
        "image": f"{WIKI}/Ryuko_Square.png",
    },
    "queenbee": {
        "name": "Queen Bee", "full_name": "Chloé Bourgeois",
        "rarity": "Epic", "emoji": "🐝", "color": 0xFFD700,
        "description": "Wielder of the Bee Miraculous. Venom freezes anyone in their tracks! 🐝",
        "power": "Venom", "miraculous": "Comb",
        "image": f"{WIKI}/Queen_Bee_Square.png",
    },
    "vesperia": {
        "name": "Vesperia", "full_name": "Zoé Lee",
        "rarity": "Epic", "emoji": "🪲", "color": 0xADD8E6,
        "description": "Wielder of the Bee Miraculous after Chloé. Heroic, brave, and selfless. 🪲",
        "power": "Venom", "miraculous": "Comb",
        "image": f"{WIKI}/Vesperia_Square.png",
    },
    "mayura": {
        "name": "Mayura", "full_name": "Nathalie Sancoeur",
        "rarity": "Epic", "emoji": "🦚", "color": 0x005F73,
        "description": "Wielder of the Peacock Miraculous. Creates amoks from emotional objects. 🦚",
        "power": "Amokization", "miraculous": "Peacock Brooch",
        "image": f"{WIKI}/Mayura_Square.png",
    },
    "purpletigress": {
        "name": "Purple Tigress", "full_name": "Juleka Couffaine",
        "rarity": "Epic", "emoji": "🐯", "color": 0x800080,
        "description": "Wielder of the Tiger Miraculous. Her Clout unleashes powerful sonic blasts. 🐯",
        "power": "Clout", "miraculous": "Bracelet",
        "image": f"{WIKI}/Purple_Tigress_Square.png",
    },
    "pigella": {
        "name": "Pigella", "full_name": "Rose Lavillant",
        "rarity": "Epic", "emoji": "🐷", "color": 0xFF69B4,
        "description": "Wielder of the Pig Miraculous. Gift reveals the deepest wish of any heart. 🐷",
        "power": "Gift", "miraculous": "Bracelet",
        "image": f"{WIKI}/Pigella_Square.png",
    },
    "minotaurox": {
        "name": "Minotaurox", "full_name": "Ivan Bruel",
        "rarity": "Epic", "emoji": "🐂", "color": 0x8B0000,
        "description": "Wielder of the Ox Miraculous. Resistance makes him an immovable fortress. 🐂",
        "power": "Resistance", "miraculous": "Nose ring",
        "image": f"{WIKI}/Minotaurox_Square.png",
    },
    # ── Rare ──────────────────────────────────────────────────────────────────
    "marinette": {
        "name": "Marinette", "full_name": "Marinette Dupain-Cheng",
        "rarity": "Rare", "emoji": "🎀", "color": 0xFF88AA,
        "description": "Kind, creative, and clumsy. She secretly loves Adrien and is Ladybug! 🎀",
        "power": "Fashion Design & Luck", "miraculous": "Guardian",
        "image": f"{WIKI}/Marinette_Dupain-Cheng_Square.png",
    },
    "adrien": {
        "name": "Adrien", "full_name": "Adrien Agreste",
        "rarity": "Rare", "emoji": "🌟", "color": 0xF4E04D,
        "description": "Famous model and fencing champion secretly living as Cat Noir! 🌟",
        "power": "Fencing & Charm", "miraculous": "None (civilian)",
        "image": f"{WIKI}/Adrien_Agreste_Square.png",
    },
    "alya": {
        "name": "Alya", "full_name": "Alya Césaire",
        "rarity": "Rare", "emoji": "📱", "color": 0xFF6B00,
        "description": "Marinette's best friend and creator of the Ladyblog — always chasing a scoop! 📱",
        "power": "Journalism", "miraculous": "None (civilian)",
        "image": f"{WIKI}/Alya_Cesaire_Square.png",
    },
    "luka": {
        "name": "Luka", "full_name": "Luka Couffaine",
        "rarity": "Rare", "emoji": "🎸", "color": 0x00838F,
        "description": "A gentle guitarist on the Liberty houseboat who can always read emotions. 🎸",
        "power": "Music & Empathy", "miraculous": "None (civilian)",
        "image": f"{WIKI}/Luka_Couffaine_Square.png",
    },
    "kagami": {
        "name": "Kagami", "full_name": "Kagami Tsurugi",
        "rarity": "Rare", "emoji": "⚔️", "color": 0x003366,
        "description": "A skilled fencer and Adrien's rival. Straightforward, determined, and precise. ⚔️",
        "power": "Fencing", "miraculous": "None (civilian)",
        "image": f"{WIKI}/Kagami_Tsurugi_Square.png",
    },
    "felix": {
        "name": "Félix", "full_name": "Félix Graham de Vanily",
        "rarity": "Rare", "emoji": "🎭", "color": 0x2C2C54,
        "description": "Adrien's mysterious cousin with a complicated relationship with the Miraculouses. 🎭",
        "power": "Unknown", "miraculous": "Stolen Ring",
        "image": f"{WIKI}/Felix_Graham_de_Vanily_Square.png",
    },
    "masterfu": {
        "name": "Master Fu", "full_name": "Wang Fu",
        "rarity": "Rare", "emoji": "🏮", "color": 0xCC8800,
        "description": "The last Miracle Box Guardian — ancient, wise, and entrusted Marinette. 🏮",
        "power": "Miraculous Guardian Arts", "miraculous": "Turtle Miraculous",
        "image": f"{WIKI}/Master_Fu_Square.png",
    },
    # ── Common ────────────────────────────────────────────────────────────────
    "nino": {
        "name": "Nino", "full_name": "Nino Lahiffe",
        "rarity": "Common", "emoji": "🎧", "color": 0x2D6A4F,
        "description": "Adrien's best friend and aspiring DJ. Always wearing his cap backwards. 🎧",
        "power": "DJ Skills", "miraculous": "None (civilian)",
        "image": f"{WIKI}/Nino_Lahiffe_Square.png",
    },
    "chloe": {
        "name": "Chloé", "full_name": "Chloé Bourgeois",
        "rarity": "Common", "emoji": "👑", "color": 0xFFD700,
        "description": "The mayor's entitled daughter and notorious mean girl of Collège Françoise Dupont. 👑",
        "power": "Entitlement", "miraculous": "None (civilian)",
        "image": f"{WIKI}/Chloe_Bourgeois_Square.png",
    },
    "rose": {
        "name": "Rose", "full_name": "Rose Lavillant",
        "rarity": "Common", "emoji": "🌸", "color": 0xFF69B4,
        "description": "The sweetest girl in class — always optimistic and full of love. 🌸",
        "power": "Positivity", "miraculous": "None (civilian)",
        "image": f"{WIKI}/Rose_Lavillant_Square.png",
    },
    "juleka": {
        "name": "Juleka", "full_name": "Juleka Couffaine",
        "rarity": "Common", "emoji": "🌙", "color": 0x800080,
        "description": "Rose's best friend and Luka's sister. Quiet and gothic with a soft heart. 🌙",
        "power": "Gothic Aesthetic", "miraculous": "None (civilian)",
        "image": f"{WIKI}/Juleka_Couffaine_Square.png",
    },
    "ivan": {
        "name": "Ivan", "full_name": "Ivan Bruel",
        "rarity": "Common", "emoji": "💪", "color": 0x8B0000,
        "description": "A large but gentle soul. He's dating Mylène and loves metal music. 💪",
        "power": "Gentle Giant", "miraculous": "None (civilian)",
        "image": f"{WIKI}/Ivan_Bruel_Square.png",
    },
    "zoe": {
        "name": "Zoé", "full_name": "Zoé Lee",
        "rarity": "Common", "emoji": "🌼", "color": 0xFFD700,
        "description": "Chloé's American half-sister. Warm and kind — practically the opposite of her sibling. 🌼",
        "power": "Kindness", "miraculous": "None (civilian)",
        "image": f"{WIKI}/Zoe_Lee_Square.png",
    },
    "lila": {
        "name": "Lila", "full_name": "Lila Rossi",
        "rarity": "Common", "emoji": "🤥", "color": 0xB22222,
        "description": "A compulsive liar and master manipulator. She has it out for Marinette. 🤥",
        "power": "Manipulation", "miraculous": "None (civilian)",
        "image": f"{WIKI}/Lila_Rossi_Square.png",
    },
    "gabriel": {
        "name": "Gabriel", "full_name": "Gabriel Agreste",
        "rarity": "Common", "emoji": "👔", "color": 0x444444,
        "description": "Adrien's strict and mysterious father. Famous fashion designer... and something more.",
        "power": "Fashion Design", "miraculous": "None (civilian)",
        "image": f"{WIKI}/Gabriel_Agreste_Square.png",
    },
}

TOTAL_CHARACTERS = len(COLLECTIBLE_CHARACTERS)

# ── Data helpers ──────────────────────────────────────────────────────────────

def load_profiles() -> dict:
    if not os.path.exists(PROFILES_FILE):
        return {}
    with open(PROFILES_FILE, "r") as f:
        return json.load(f)

def save_profiles(data: dict):
    os.makedirs(os.path.dirname(PROFILES_FILE), exist_ok=True)
    with open(PROFILES_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_user_profile(data: dict, user_id: str) -> dict:
    if user_id not in data:
        data[user_id] = {
            "bio": None,
            "quote": None,
            "color": None,
            "active_character": None,
            "collection": [],
        }
    return data[user_id]

def rarity_sort_key(r: str) -> int:
    return {"Common": 0, "Rare": 1, "Epic": 2, "Legendary": 3}.get(r, 0)

# ── Autocomplete ──────────────────────────────────────────────────────────────

async def character_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=f"{c['emoji']} {c['name']} ({c['rarity']})", value=key)
        for key, c in COLLECTIBLE_CHARACTERS.items()
        if current.lower() in key or current.lower() in c["name"].lower()
    ][:25]

async def owned_character_autocomplete(interaction: discord.Interaction, current: str):
    data = load_profiles()
    uid = str(interaction.user.id)
    profile = get_user_profile(data, uid)
    owned = profile.get("collection", [])
    return [
        app_commands.Choice(
            name=f"{COLLECTIBLE_CHARACTERS[k]['emoji']} {COLLECTIBLE_CHARACTERS[k]['name']} ({COLLECTIBLE_CHARACTERS[k]['rarity']})",
            value=k,
        )
        for k in owned
        if k in COLLECTIBLE_CHARACTERS and (current.lower() in k or current.lower() in COLLECTIBLE_CHARACTERS[k]["name"].lower())
    ][:25]


# ── Cog ───────────────────────────────────────────────────────────────────────

class CollectionCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    char_group = app_commands.Group(
        name="character",
        description="Browse and collect Miraculous characters!",
    )

    # ── /character list ───────────────────────────────────────────────────────

    @char_group.command(name="list", description="Show all available Miraculous characters to collect.")
    @app_commands.describe(rarity="Filter by rarity (leave blank for all)")
    @app_commands.choices(rarity=[
        app_commands.Choice(name="⚪ Common",    value="Common"),
        app_commands.Choice(name="🔵 Rare",      value="Rare"),
        app_commands.Choice(name="🟣 Epic",      value="Epic"),
        app_commands.Choice(name="🟡 Legendary", value="Legendary"),
    ])
    async def char_list(self, interaction: discord.Interaction, rarity: Optional[str] = None):
        await interaction.response.defer()
        data = load_profiles()
        uid = str(interaction.user.id)
        profile = get_user_profile(data, uid)
        owned = set(profile.get("collection", []))

        tiers = ["Legendary", "Epic", "Rare", "Common"] if not rarity else [rarity]

        embed = discord.Embed(
            title="📖 Miraculous Character Roster",
            description=(
                f"Collect characters using `/character catch <name>`!\n"
                f"You own **{len(owned)}/{TOTAL_CHARACTERS}** characters.\n"
                f"Use `/character catch` — costs vary by rarity:"
            ),
            color=0xFF0000,
        )

        for tier in tiers:
            cfg = RARITY[tier]
            chars_in_tier = [(k, c) for k, c in COLLECTIBLE_CHARACTERS.items() if c["rarity"] == tier]
            if not chars_in_tier:
                continue

            cost_str = f"Free" if cfg["cost"] == 0 else f"{cfg['cost']:,} 🌟"
            lines = []
            for key, c in chars_in_tier:
                status = "✅" if key in owned else "🔒"
                lines.append(f"{status} {c['emoji']} **{c['name']}** `!{key}`")

            embed.add_field(
                name=f"{cfg['emoji']} {tier}  {cfg['badge']}  •  Cost: {cost_str}",
                value="\n".join(lines),
                inline=False,
            )

        embed.set_footer(text=f"✅ = owned  🔒 = not yet caught  •  {TOTAL_CHARACTERS} characters total")
        await interaction.followup.send(embed=embed)

    # ── /character catch ──────────────────────────────────────────────────────

    @char_group.command(name="catch", description="Catch a Miraculous character and add them to your collection!")
    @app_commands.describe(name="The character to catch (use /character list to see all)")
    @app_commands.autocomplete(name=character_autocomplete)
    async def char_catch(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer()
        key = name.lower().strip().replace(" ", "").replace("-", "").replace("é", "e").replace("è", "e")

        character = COLLECTIBLE_CHARACTERS.get(key)
        if not character:
            close = [
                k for k, c in COLLECTIBLE_CHARACTERS.items()
                if name.lower() in c["name"].lower() or name.lower() in k
            ]
            if close:
                await interaction.followup.send(
                    f"❌ No character found for `{name}`.\n"
                    f"Did you mean: {', '.join(f'`{k}`' for k in close[:5])}?\n"
                    f"Use `/character list` to see all characters.",
                    ephemeral=True,
                )
            else:
                await interaction.followup.send(
                    f"❌ No character found for `{name}`. Use `/character list` to browse all characters.",
                    ephemeral=True,
                )
            return

        data = load_profiles()
        uid = str(interaction.user.id)
        profile = get_user_profile(data, uid)

        if key in profile["collection"]:
            await interaction.followup.send(
                f"✅ You already have **{character['name']}** {character['emoji']} in your collection!\n"
                f"Use `/collection` to view your characters.",
                ephemeral=True,
            )
            return

        rarity_cfg = RARITY[character["rarity"]]
        cost = rarity_cfg["cost"]

        if cost > 0:
            economy_file = os.path.join(os.path.dirname(__file__), "..", "data", "economy.json")
            if not os.path.exists(economy_file):
                await interaction.followup.send(
                    "❌ Economy system not found. Cannot pay for this character.",
                    ephemeral=True,
                )
                return
            with open(economy_file, "r") as f:
                econ_data = json.load(f)

            if uid not in econ_data:
                econ_data[uid] = {"balance": 500}
            balance = econ_data[uid].get("balance", 0)

            if balance < cost:
                await interaction.followup.send(
                    f"❌ **Not enough Miraculons!**\n"
                    f"**{character['name']}** costs **{cost:,} 🌟 Miraculons** ({character['rarity']}).\n"
                    f"Your balance: **{balance:,} 🌟**\n"
                    f"Earn more with `/daily`, `/work`, or `/weekly`!",
                    ephemeral=True,
                )
                return

            econ_data[uid]["balance"] = balance - cost
            with open(economy_file, "w") as f:
                json.dump(econ_data, f, indent=2)

        profile["collection"].append(key)
        save_profiles(data)

        color = character["color"]
        rarity_emoji = rarity_cfg["emoji"]
        badge = rarity_cfg["badge"]

        embed = discord.Embed(
            title=f"{character['emoji']}  Character Caught!",
            description=(
                f"**{character['name']}** has joined your Miraculous collection!\n\n"
                f"*{character['description']}*"
            ),
            color=color,
        )
        embed.add_field(name="⚡ Power", value=character["power"], inline=True)
        embed.add_field(name="💎 Miraculous", value=character["miraculous"], inline=True)
        embed.add_field(
            name=f"{rarity_emoji} Rarity",
            value=f"**{character['rarity']}**  {badge}",
            inline=True,
        )
        if cost > 0:
            embed.add_field(name="💸 Cost Paid", value=f"**{cost:,} 🌟 Miraculons**", inline=True)
        embed.add_field(
            name="📦 Collection",
            value=f"**{len(profile['collection'])}/{TOTAL_CHARACTERS}** characters",
            inline=True,
        )
        embed.set_image(url=character["image"])
        embed.set_footer(
            text="Use /setcharacter to set as your active hero  •  /collection to view all",
            icon_url=interaction.user.display_avatar.url,
        )
        await interaction.followup.send(embed=embed)

    # ── /collection ───────────────────────────────────────────────────────────

    @app_commands.command(name="collection", description="View your Miraculous character collection!")
    @app_commands.describe(user="Whose collection to view (leave blank for your own)")
    async def view_collection(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        await interaction.response.defer()
        target = user or interaction.user
        uid = str(target.id)
        data = load_profiles()
        profile = get_user_profile(data, uid)
        owned = profile.get("collection", [])
        active = profile.get("active_character")

        if not owned:
            msg = (
                "You haven't caught any characters yet! Use `/character catch <name>` to start."
                if not user else
                f"**{target.display_name}** hasn't caught any characters yet!"
            )
            await interaction.followup.send(msg, ephemeral=True)
            return

        owned_valid = [k for k in owned if k in COLLECTIBLE_CHARACTERS]
        owned_sorted = sorted(owned_valid, key=lambda k: -rarity_sort_key(COLLECTIBLE_CHARACTERS[k]["rarity"]))

        embed = discord.Embed(
            title=f"{'🃏' if not user else '📖'} {target.display_name}'s Collection",
            description=f"**{len(owned_valid)}/{TOTAL_CHARACTERS}** Miraculous characters collected",
            color=0xFF0000,
        )
        embed.set_thumbnail(url=target.display_avatar.url)

        tier_lines: dict[str, list[str]] = {"Legendary": [], "Epic": [], "Rare": [], "Common": []}
        for key in owned_sorted:
            c = COLLECTIBLE_CHARACTERS[key]
            is_active = key == active
            star = " ⭐" if is_active else ""
            tier_lines[c["rarity"]].append(f"{c['emoji']} **{c['name']}**{star}")

        for tier in ["Legendary", "Epic", "Rare", "Common"]:
            lines = tier_lines[tier]
            if not lines:
                continue
            cfg = RARITY[tier]
            embed.add_field(
                name=f"{cfg['emoji']} {tier}  {cfg['badge']}  ({len(lines)})",
                value="\n".join(lines),
                inline=True,
            )

        if active and active in COLLECTIBLE_CHARACTERS:
            hero = COLLECTIBLE_CHARACTERS[active]
            embed.set_image(url=hero["image"])

        embed.set_footer(text="⭐ = active character  •  /setcharacter <name> to change active hero")
        await interaction.followup.send(embed=embed)

    # ── /setcharacter ─────────────────────────────────────────────────────────

    @app_commands.command(name="setcharacter", description="Set your active Miraculous hero for your profile card.")
    @app_commands.describe(name="The character to set as active (must be in your collection)")
    @app_commands.autocomplete(name=owned_character_autocomplete)
    async def set_character(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer()
        key = name.lower().strip()
        data = load_profiles()
        uid = str(interaction.user.id)
        profile = get_user_profile(data, uid)

        if key not in COLLECTIBLE_CHARACTERS:
            await interaction.followup.send(
                f"❌ `{name}` is not a valid character. Use `/character list` to browse.",
                ephemeral=True,
            )
            return

        if key not in profile["collection"]:
            c = COLLECTIBLE_CHARACTERS[key]
            await interaction.followup.send(
                f"❌ You don't have **{c['name']}** {c['emoji']} in your collection yet!\n"
                f"Catch them first with `/character catch {key}`.",
                ephemeral=True,
            )
            return

        profile["active_character"] = key
        save_profiles(data)

        c = COLLECTIBLE_CHARACTERS[key]
        embed = discord.Embed(
            title=f"{c['emoji']} Active Hero Updated!",
            description=f"**{c['name']}** is now your active Miraculous hero!\nThey'll appear on your `/profile` card.",
            color=c["color"],
        )
        embed.set_thumbnail(url=c["image"])
        embed.set_footer(text="View your card with /profile")
        await interaction.followup.send(embed=embed, ephemeral=True)

    # ── /dropcard ─────────────────────────────────────────────────────────────

    @staticmethod
    def _pick_random_card() -> tuple[str, dict]:
        """Pick a random character key+data using weighted rarity odds."""
        tiers = list(DROP_WEIGHTS.keys())
        weights = [DROP_WEIGHTS[t] for t in tiers]
        chosen_rarity = random.choices(tiers, weights=weights, k=1)[0]

        pool = [
            (key, c)
            for key, c in COLLECTIBLE_CHARACTERS.items()
            if c["rarity"] == chosen_rarity
        ]
        return random.choice(pool)

    @staticmethod
    def _add_economy_coins(uid: str, amount: int) -> int:
        """Add coins to the user's economy balance. Returns new balance."""
        economy_file = os.path.join(os.path.dirname(__file__), "..", "data", "economy.json")
        if os.path.exists(economy_file):
            with open(economy_file, "r") as f:
                econ = json.load(f)
        else:
            econ = {}
        if uid not in econ:
            econ[uid] = {"balance": 500}
        econ[uid]["balance"] = econ[uid].get("balance", 0) + amount
        with open(economy_file, "w") as f:
            json.dump(econ, f, indent=2)
        return econ[uid]["balance"]

    @app_commands.command(
        name="dropcard",
        description="✨ Open the Miracle Box and draw a random Miraculous character card!",
    )
    @app_commands.checks.cooldown(1, DROPCARD_COOLDOWN, key=lambda i: i.user.id)
    async def drop_card(self, interaction: discord.Interaction):
        await interaction.response.defer()

        key, character = self._pick_random_card()
        rarity_cfg = RARITY[character["rarity"]]

        data = load_profiles()
        uid = str(interaction.user.id)
        profile = get_user_profile(data, uid)

        is_duplicate = key in profile["collection"]

        # ── Rarity display strings ────────────────────────────────────────────
        rarity_bar_map = {
            "Common":    "░░░░░░░░░░░░░░░  ⚪ Common",
            "Rare":      "████░░░░░░░░░░░  🔵 Rare",
            "Epic":      "██████████░░░░░  🟣 Epic",
            "Legendary": "███████████████  🟡 **LEGENDARY!**",
        }
        rarity_bar = rarity_bar_map[character["rarity"]]

        # ── Flavour opening text ──────────────────────────────────────────────
        opening = random.choice(CARD_FLIP_LINES)

        # ── Build the drop embed ──────────────────────────────────────────────
        embed = discord.Embed(
            title=f"🃏  Card Drop!  {character['emoji']}",
            description=(
                f"{opening}\n\n"
                f"# {character['emoji']}  {character['name']}\n"
                f"*{character['full_name']}*\n\n"
                f"{character['description']}"
            ),
            color=character["color"],
        )

        embed.add_field(name="⚡ Power", value=character["power"], inline=True)
        embed.add_field(name="💎 Miraculous", value=character["miraculous"], inline=True)
        embed.add_field(name="✦ Rarity", value=rarity_bar, inline=False)

        embed.set_image(url=character["image"])
        embed.set_author(
            name=f"{interaction.user.display_name} opens the Miracle Box…",
            icon_url=interaction.user.display_avatar.url,
        )

        if is_duplicate:
            # ── DUPLICATE path ────────────────────────────────────────────────
            coins = DUPLICATE_COINS[character["rarity"]]
            new_balance = self._add_economy_coins(uid, coins)

            embed.add_field(
                name="🔁 Duplicate Card!",
                value=(
                    f"You already own **{character['name']}**!\n"
                    f"Converted into **+{coins} 🌟 Miraculons**.\n"
                    f"New balance: **{new_balance:,} 🌟**"
                ),
                inline=False,
            )
            embed.set_footer(
                text=f"📦 Collection: {len(profile['collection'])}/{TOTAL_CHARACTERS}  •  /dropcard cooldown: 1 hour"
            )
            owned_count = len(profile["collection"])
        else:
            # ── NEW CARD path ─────────────────────────────────────────────────
            profile["collection"].append(key)
            save_profiles(data)
            owned_count = len(profile["collection"])

            embed.add_field(
                name="✅ New Card Claimed!",
                value=(
                    f"**{character['name']}** has been added to your collection!\n"
                    f"Use `/setcharacter {key}` to equip them on your profile."
                ),
                inline=False,
            )
            embed.set_footer(
                text=f"📦 Collection: {owned_count}/{TOTAL_CHARACTERS}  •  /dropcard cooldown: 1 hour"
            )

        await interaction.followup.send(embed=embed)

    @drop_card.error
    async def drop_card_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            minutes, seconds = divmod(int(error.retry_after), 60)
            time_str = f"{minutes}m {seconds}s" if minutes else f"{seconds}s"
            embed = discord.Embed(
                title="⏳ Miracle Box is Recharging…",
                description=(
                    f"The Miracle Box needs time to restore its magic!\n\n"
                    f"Try again in **{time_str}**.\n\n"
                    f"*In the meantime, check your `/collection` or `/profile`!*"
                ),
                color=0xFF0000,
            )
            embed.set_footer(text="One drop per hour — make it count! ✨")
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            raise error


async def setup(bot: commands.Bot):
    await bot.add_cog(CollectionCog(bot))
