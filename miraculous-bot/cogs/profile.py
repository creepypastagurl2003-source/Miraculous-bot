import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import logging
from typing import Optional

from .collection import (
    COLLECTIBLE_CHARACTERS,
    RARITY,
    TOTAL_CHARACTERS,
    load_profiles,
    save_profiles,
    get_user_profile,
)

logger = logging.getLogger("bot.profile")

ECONOMY_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "economy.json")

PRESET_COLORS = {
    "red":      0xFF0000,
    "black":    0x1A1A2E,
    "purple":   0x6A0DAD,
    "pink":     0xFF88CC,
    "blue":     0x4488FF,
    "green":    0x2D6A4F,
    "gold":     0xFFD700,
    "cyan":     0x00CCFF,
    "orange":   0xFF6B00,
    "white":    0xFFFFFF,
}

# Hero accent colors used for themed decorative lines in embeds
HERO_ACCENT = {
    "ladybug":      "🐞 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 🐞",
    "catnoir":      "🐱 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 🐱",
    "hawkmoth":     "🦋 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 🦋",
    "tikki":        "🍪 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 🍪",
    "plagg":        "🧀 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 🧀",
}


def load_economy(user_id: str) -> Optional[int]:
    if not os.path.exists(ECONOMY_FILE):
        return None
    with open(ECONOMY_FILE, "r") as f:
        data = json.load(f)
    return data.get(user_id, {}).get("balance")


def build_profile_embed(
    target: discord.Member,
    profile: dict,
    balance: Optional[int],
) -> discord.Embed:
    active_key = profile.get("active_character")
    hero = COLLECTIBLE_CHARACTERS.get(active_key) if active_key else None
    collection = profile.get("collection", [])

    # ── Choose embed color ────────────────────────────────────────────────────
    if hero:
        color = hero["color"]
    elif profile.get("color"):
        color = profile["color"]
    else:
        color = 0xFF0000  # default Ladybug red

    # ── Title line ────────────────────────────────────────────────────────────
    if hero:
        rarity_cfg = RARITY[hero["rarity"]]
        title = (
            f"{hero['emoji']}  {target.display_name}  {rarity_cfg['badge']}"
        )
    else:
        title = f"🃏  {target.display_name}'s  Miraculous Profile"

    embed = discord.Embed(title=title, color=color)

    # ── Author: user avatar ───────────────────────────────────────────────────
    embed.set_author(
        name=f"{target.display_name}  •  Miraculous Profile",
        icon_url=target.display_avatar.url,
    )

    # ── Active hero section ───────────────────────────────────────────────────
    if hero:
        rarity_cfg = RARITY[hero["rarity"]]
        embed.add_field(
            name=f"⚡ Active Hero",
            value=(
                f"{hero['emoji']} **{hero['name']}**  {rarity_cfg['emoji']} *{hero['rarity']}*\n"
                f"**Power:** {hero['power']}\n"
                f"**Miraculous:** {hero['miraculous']}"
            ),
            inline=False,
        )
        embed.set_thumbnail(url=hero["image"])
    else:
        embed.add_field(
            name="⚡ Active Hero",
            value="*No hero set — use `/setcharacter` after catching one!*",
            inline=False,
        )
        embed.set_thumbnail(url=target.display_avatar.url)

    # ── Divider ───────────────────────────────────────────────────────────────
    divider = HERO_ACCENT.get(active_key, "✨ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ✨")
    embed.add_field(name="\u200b", value=divider, inline=False)

    # ── Bio ───────────────────────────────────────────────────────────────────
    bio = profile.get("bio")
    embed.add_field(
        name="💬 Bio",
        value=bio if bio else "*No bio set — use `/setbio` to add one!*",
        inline=False,
    )

    # ── Quote ─────────────────────────────────────────────────────────────────
    quote = profile.get("quote")
    if quote:
        embed.add_field(
            name="✨ Quote",
            value=f'*"{quote}"*',
            inline=False,
        )

    # ── Stats row ─────────────────────────────────────────────────────────────
    if balance is not None:
        embed.add_field(
            name="💰 Miraculons",
            value=f"**{balance:,}** 🌟",
            inline=True,
        )

    owned_count = len([k for k in collection if k in COLLECTIBLE_CHARACTERS])
    embed.add_field(
        name="🗃️ Collection",
        value=f"**{owned_count}/{TOTAL_CHARACTERS}** caught",
        inline=True,
    )

    # ── Footer ────────────────────────────────────────────────────────────────
    footer_parts = ["/setbio  /setquote  /setcharacter  /setcolor"]
    embed.set_footer(
        text="  •  ".join(footer_parts),
        icon_url=target.display_avatar.url,
    )

    return embed


class ProfileCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── /profile ──────────────────────────────────────────────────────────────

    @app_commands.command(name="profile", description="View a Miraculous-themed hero profile card!")
    @app_commands.describe(user="Whose profile to view (leave blank for your own)")
    async def profile(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        await interaction.response.defer()
        target = user or interaction.user
        uid = str(target.id)

        data = load_profiles()
        profile = get_user_profile(data, uid)
        balance = load_economy(uid)

        embed = build_profile_embed(target, profile, balance)
        await interaction.followup.send(embed=embed)

    # ── /setbio ───────────────────────────────────────────────────────────────

    @app_commands.command(name="setbio", description="Set your bio for your Miraculous profile card.")
    @app_commands.describe(text="Your bio (max 200 characters)")
    async def set_bio(self, interaction: discord.Interaction, text: str):
        await interaction.response.defer()
        if len(text) > 200:
            await interaction.followup.send(
                f"❌ Bio is too long ({len(text)}/200 characters). Please shorten it.",
                ephemeral=True,
            )
            return

        data = load_profiles()
        uid = str(interaction.user.id)
        profile = get_user_profile(data, uid)
        profile["bio"] = text
        save_profiles(data)

        await interaction.followup.send(
            f"✅ Bio updated!\n> {text}\n\nView your card with `/profile`.",
            ephemeral=True,
        )

    # ── /setquote ─────────────────────────────────────────────────────────────

    @app_commands.command(name="setquote", description="Set a personal quote for your Miraculous profile.")
    @app_commands.describe(text="Your quote (max 150 characters)")
    async def set_quote(self, interaction: discord.Interaction, text: str):
        await interaction.response.defer()
        if len(text) > 150:
            await interaction.followup.send(
                f"❌ Quote is too long ({len(text)}/150 characters). Please shorten it.",
                ephemeral=True,
            )
            return

        data = load_profiles()
        uid = str(interaction.user.id)
        profile = get_user_profile(data, uid)
        profile["quote"] = text
        save_profiles(data)

        await interaction.followup.send(
            f'✅ Quote set!\n> *"{text}"*\n\nView your card with `/profile`.',
            ephemeral=True,
        )

    # ── /setcolor ─────────────────────────────────────────────────────────────

    @app_commands.command(name="setcolor", description="Set your profile card embed color (overridden by active hero).")
    @app_commands.describe(color="Choose a color name or hex code like #FF0000")
    @app_commands.choices(color=[
        app_commands.Choice(name="🔴 Red",    value="red"),
        app_commands.Choice(name="⚫ Black",  value="black"),
        app_commands.Choice(name="🟣 Purple", value="purple"),
        app_commands.Choice(name="🩷 Pink",   value="pink"),
        app_commands.Choice(name="🔵 Blue",   value="blue"),
        app_commands.Choice(name="🟢 Green",  value="green"),
        app_commands.Choice(name="🟡 Gold",   value="gold"),
        app_commands.Choice(name="🩵 Cyan",   value="cyan"),
        app_commands.Choice(name="🟠 Orange", value="orange"),
        app_commands.Choice(name="⚪ White",  value="white"),
    ])
    async def set_color(self, interaction: discord.Interaction, color: str):
        await interaction.response.defer()
        hex_value = PRESET_COLORS.get(color.lower())
        if not hex_value:
            await interaction.followup.send(
                f"❌ Unknown color `{color}`. Pick from the dropdown options.",
                ephemeral=True,
            )
            return

        data = load_profiles()
        uid = str(interaction.user.id)
        profile = get_user_profile(data, uid)
        profile["color"] = hex_value
        save_profiles(data)

        embed = discord.Embed(
            description=f"✅ Profile color set to **{color.capitalize()}**!\n*(Your active hero's color takes priority when set)*",
            color=hex_value,
        )
        embed.set_footer(text="View your card with /profile")
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(ProfileCog(bot))
