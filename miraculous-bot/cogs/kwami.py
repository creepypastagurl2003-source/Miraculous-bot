import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import random
from typing import Optional

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "kwamis.json")

KWAMIS = {
    "Tikki": {
        "miraculous": "Ladybug Miraculous",
        "holder": "Marinette / Ladybug",
        "power": "Lucky Charm",
        "element": "Creation",
        "emoji": "🐞",
        "color": 0xFF0000,
        "description": "Kwami of Creation. Grants the power of good luck and creation.",
        "food": "Macarons",
        "ability": "Lucky Charm — summons a random object to help solve a problem!",
    },
    "Plagg": {
        "miraculous": "Cat Miraculous",
        "holder": "Adrien / Cat Noir",
        "power": "Cataclysm",
        "element": "Destruction",
        "emoji": "🐱",
        "color": 0x1A1A2E,
        "description": "Kwami of Destruction. Grants the power of bad luck and destruction.",
        "food": "Camembert cheese",
        "ability": "Cataclysm — destroys anything with a single touch!",
    },
    "Nooroo": {
        "miraculous": "Butterfly Miraculous",
        "holder": "Gabriel / Shadow Moth",
        "power": "Akumatization",
        "element": "Transmission",
        "emoji": "🦋",
        "color": 0x6A0DAD,
        "description": "Kwami of Transmission. Grants the power to give others superpowers.",
        "food": "Pollen & flower nectar",
        "ability": "Akumatization — transforms victims into supervillains!",
    },
    "Duusu": {
        "miraculous": "Peacock Miraculous",
        "holder": "Natalie / Mayura",
        "power": "Amokization",
        "element": "Emotion",
        "emoji": "🦚",
        "color": 0x005F73,
        "description": "Kwami of Emotion. Grants the power to create sentimonsters.",
        "food": "Emotions and feelings",
        "ability": "Amokization — creates sentimonsters from charged objects!",
    },
    "Wayzz": {
        "miraculous": "Turtle Miraculous",
        "holder": "Master Fu / Shell-ter",
        "power": "Shell-ter",
        "element": "Protection",
        "emoji": "🐢",
        "color": 0x2D6A4F,
        "description": "Kwami of Protection. Grants the power of protection.",
        "food": "Spinach",
        "ability": "Shell-ter — creates an indestructible force field!",
    },
    "Trixx": {
        "miraculous": "Fox Miraculous",
        "holder": "Alya / Rena Rouge",
        "power": "Mirage",
        "element": "Illusion",
        "emoji": "🦊",
        "color": 0xFF6B00,
        "description": "Kwami of Illusion. Grants the power to create perfect illusions.",
        "food": "Cheese",
        "ability": "Mirage — creates realistic illusions to trick enemies!",
    },
    "Pollen": {
        "miraculous": "Bee Miraculous",
        "holder": "Chloe / Queen Bee",
        "power": "Venom",
        "element": "Subjection",
        "emoji": "🐝",
        "color": 0xFFD700,
        "description": "Kwami of Subjection. Grants the power to paralyze.",
        "food": "Royal jelly",
        "ability": "Venom — paralyzes any target with a single sting!",
    },
    "Longg": {
        "miraculous": "Dragon Miraculous",
        "holder": "Luka / Viperion",
        "power": "Second Chance",
        "element": "Power",
        "emoji": "🐉",
        "color": 0x00838F,
        "description": "Kwami of Power. Grants elemental powers of water, lightning, and wind.",
        "food": "Dumplings",
        "ability": "Second Chance — rewinds time by 5 minutes!",
    },
    "Fluff": {
        "miraculous": "Rabbit Miraculous",
        "holder": "Alix / Bunnyx",
        "power": "Burrow",
        "element": "Time",
        "emoji": "🐰",
        "color": 0xC8A2C8,
        "description": "Kwami of Time. Grants the power of time travel.",
        "food": "Carrots",
        "ability": "Burrow — opens portals through time!",
    },
    "Kaalki": {
        "miraculous": "Horse Miraculous",
        "holder": "Max / Pegasus",
        "power": "Voyage",
        "element": "Teleportation",
        "emoji": "🐴",
        "color": 0x8B4513,
        "description": "Kwami of Teleportation. Grants the power of instant travel.",
        "food": "Sugar cubes",
        "ability": "Voyage — creates portals to travel anywhere instantly!",
    },
    "Xuppu": {
        "miraculous": "Monkey Miraculous",
        "holder": "Lê Chiến Kim / King Monkey",
        "power": "Uproar",
        "element": "Jubilation",
        "emoji": "🐒",
        "color": 0xFFAA00,
        "description": "Kwami of Jubilation. Grants the power to make powers malfunction.",
        "food": "Bananas",
        "ability": "Uproar — makes any superpower go haywire!",
    },
    "Ziggy": {
        "miraculous": "Goat Miraculous",
        "holder": "Unnamed",
        "power": "Unknown",
        "element": "Jubilation",
        "emoji": "🐐",
        "color": 0x90EE90,
        "description": "Kwami of the Goat Miraculous.",
        "food": "Grass",
        "ability": "Power yet to be fully revealed!",
    },
    "Roaar": {
        "miraculous": "Tiger Miraculous",
        "holder": "Unnamed",
        "power": "Unknown",
        "element": "Strength",
        "emoji": "🐯",
        "color": 0xFF8C00,
        "description": "Kwami of the Tiger Miraculous. Grants immense strength.",
        "food": "Meat",
        "ability": "Power yet to be fully revealed!",
    },
    "Stompp": {
        "miraculous": "Ox Miraculous",
        "holder": "Unnamed",
        "power": "Unknown",
        "element": "Resilience",
        "emoji": "🐂",
        "color": 0x8B0000,
        "description": "Kwami of the Ox Miraculous.",
        "food": "Grass",
        "ability": "Power yet to be fully revealed!",
    },
    "Barkk": {
        "miraculous": "Dog Miraculous",
        "holder": "Unnamed",
        "power": "Unknown",
        "element": "Loyalty",
        "emoji": "🐕",
        "color": 0xA0522D,
        "description": "Kwami of the Dog Miraculous. Grants loyalty-based powers.",
        "food": "Bones",
        "ability": "Power yet to be fully revealed!",
    },
}


def load_data() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"user_kwamis": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def kwami_embed(kwami_name: str, kwami: dict) -> discord.Embed:
    embed = discord.Embed(
        title=f"{kwami['emoji']} {kwami_name}",
        description=kwami["description"],
        color=kwami["color"],
    )
    embed.add_field(name="Miraculous", value=kwami["miraculous"], inline=True)
    embed.add_field(name="Element", value=kwami["element"], inline=True)
    embed.add_field(name="Known Holder", value=kwami["holder"], inline=True)
    embed.add_field(name="⚡ Special Ability", value=kwami["ability"], inline=False)
    embed.add_field(name="🍽️ Favorite Food", value=kwami["food"], inline=True)
    return embed


class KwamiCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    kwami_group = app_commands.Group(name="kwami", description="Kwami system commands")

    @kwami_group.command(name="discover", description="Discover a random kwami to bond with!")
    async def discover(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        user_id = str(interaction.user.id)

        if user_id in data["user_kwamis"]:
            existing = data["user_kwamis"][user_id]
            k = KWAMIS[existing]
            embed = discord.Embed(
                title=f"You already have {k['emoji']} {existing}!",
                description=(
                    f"You're already bonded with **{existing}**, the kwami of {k['element']}.\n"
                    f"Use `/kwami info` to see your kwami's details, or `/kwami release` to release them."
                ),
                color=discord.Color.orange(),
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        kwami_name = random.choice(list(KWAMIS.keys()))
        kwami = KWAMIS[kwami_name]

        data["user_kwamis"][user_id] = kwami_name
        save_data(data)

        embed = kwami_embed(kwami_name, kwami)
        embed.title = f"✨ A Kwami has chosen you! {kwami['emoji']} {kwami_name}"
        embed.set_footer(text=f"{interaction.user.display_name} has bonded with {kwami_name}!")
        await interaction.followup.send(embed=embed)

    @kwami_group.command(name="info", description="View your kwami or someone else's kwami.")
    @app_commands.describe(user="The user whose kwami to view (leave empty for yourself)")
    async def info(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        await interaction.response.defer()
        data = load_data()
        target = user or interaction.user
        target_id = str(target.id)

        kwami_name = data["user_kwamis"].get(target_id)
        if not kwami_name:
            name = "You don't" if not user else f"{target.display_name} doesn't"
            await interaction.followup.send(
                f"❌ {name} have a kwami yet! Use `/kwami discover` to find one.",
                ephemeral=True,
            )
            return

        kwami = KWAMIS.get(kwami_name)
        if not kwami:
            await interaction.followup.send("❌ Kwami data not found.", ephemeral=True)
            return

        embed = kwami_embed(kwami_name, kwami)
        embed.set_author(
            name=f"{target.display_name}'s Kwami",
            icon_url=target.display_avatar.url,
        )
        await interaction.followup.send(embed=embed)

    @kwami_group.command(name="list", description="View all available kwamis.")
    async def list_kwamis(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = discord.Embed(
            title="✨ All Kwamis",
            description="Here are all the kwamis you might bond with:",
            color=discord.Color.purple(),
        )
        for name, k in KWAMIS.items():
            embed.add_field(
                name=f"{k['emoji']} {name}",
                value=f"*{k['element']}* — {k['miraculous']}",
                inline=True,
            )
        embed.set_footer(text="Use /kwami discover to bond with a kwami!")
        await interaction.followup.send(embed=embed)

    @kwami_group.command(name="transform", description="Use your kwami's power!")
    async def transform(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        user_id = str(interaction.user.id)
        kwami_name = data["user_kwamis"].get(user_id)

        if not kwami_name:
            await interaction.followup.send(
                "❌ You don't have a kwami! Use `/kwami discover` first.", ephemeral=True
            )
            return

        kwami = KWAMIS[kwami_name]
        embed = discord.Embed(
            title=f"{kwami['emoji']} Transformation!",
            description=(
                f"**{interaction.user.display_name}** calls upon **{kwami_name}**!\n\n"
                f"*\"{kwami_name}, {kwami['power']}!\"*\n\n"
                f"⚡ **{kwami['ability']}**"
            ),
            color=kwami["color"],
        )
        embed.set_footer(text=f"Wielder of the {kwami['miraculous']}")
        await interaction.followup.send(embed=embed)

    @kwami_group.command(name="release", description="Release your kwami and find a new one.")
    async def release(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        user_id = str(interaction.user.id)
        kwami_name = data["user_kwamis"].get(user_id)

        if not kwami_name:
            await interaction.followup.send(
                "❌ You don't have a kwami to release!", ephemeral=True
            )
            return

        kwami = KWAMIS[kwami_name]
        del data["user_kwamis"][user_id]
        save_data(data)

        embed = discord.Embed(
            title=f"Goodbye, {kwami_name}! {kwami['emoji']}",
            description=(
                f"**{interaction.user.display_name}** has released **{kwami_name}**.\n"
                f"Use `/kwami discover` to bond with a new kwami."
            ),
            color=discord.Color.light_grey(),
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(KwamiCog(bot))
