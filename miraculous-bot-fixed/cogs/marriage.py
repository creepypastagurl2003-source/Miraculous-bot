import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import time
from typing import Optional

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "marriages.json")


def load_data() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"marriages": {}, "proposals": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_spouse_id(data: dict, user_id: str) -> Optional[str]:
    return data["marriages"].get(user_id)


def format_timestamp(ts: float) -> str:
    import datetime
    dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
    return dt.strftime("%B %d, %Y")


class MarriageCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="propose", description="Propose to another user!")
    @app_commands.describe(user="The user you want to propose to")
    async def propose(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer()
        data = load_data()
        proposer_id = str(interaction.user.id)
        target_id = str(user.id)

        if user.id == interaction.user.id:
            await interaction.followup.send(
                "❌ You can't propose to yourself!", ephemeral=True
            )
            return

        if user.bot:
            await interaction.followup.send(
                "❌ You can't propose to a bot!", ephemeral=True
            )
            return

        if get_spouse_id(data, proposer_id):
            await interaction.followup.send(
                "❌ You're already married! Use `/divorce` first.", ephemeral=True
            )
            return

        if get_spouse_id(data, target_id):
            await interaction.followup.send(
                f"❌ {user.display_name} is already married!", ephemeral=True
            )
            return

        if proposer_id in data["proposals"]:
            await interaction.followup.send(
                "❌ You already have a pending proposal! Wait for a response.", ephemeral=True
            )
            return

        if target_id in data["proposals"] and data["proposals"][target_id]["from"] == proposer_id:
            await interaction.followup.send(
                f"❌ You already proposed to {user.display_name}!", ephemeral=True
            )
            return

        data["proposals"][proposer_id] = {
            "to": target_id,
            "from": proposer_id,
            "timestamp": time.time(),
        }
        save_data(data)

        embed = discord.Embed(
            title="💍 Marriage Proposal!",
            description=(
                f"**{interaction.user.display_name}** has proposed to **{user.display_name}**!\n\n"
                f"{user.mention}, do you accept?\n\n"
                f"Use `/accept` to say yes, or `/reject` to decline."
            ),
            color=discord.Color.pink(),
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/💍" if False else discord.utils.MISSING)
        embed.set_footer(text="This proposal will expire after 24 hours.")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="accept", description="Accept a marriage proposal!")
    async def accept(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        target_id = str(interaction.user.id)

        proposer_id = None
        for pid, proposal in data["proposals"].items():
            if proposal["to"] == target_id:
                proposer_id = pid
                break

        if not proposer_id:
            await interaction.followup.send(
                "❌ You don't have any pending proposals!", ephemeral=True
            )
            return

        if get_spouse_id(data, target_id):
            await interaction.followup.send(
                "❌ You're already married!", ephemeral=True
            )
            return

        if get_spouse_id(data, proposer_id):
            del data["proposals"][proposer_id]
            save_data(data)
            await interaction.followup.send(
                "❌ The person who proposed to you is now married to someone else. Proposal cancelled.",
                ephemeral=True,
            )
            return

        data["marriages"][target_id] = proposer_id
        data["marriages"][proposer_id] = target_id
        data["marriages"][f"{target_id}_since"] = time.time()
        data["marriages"][f"{proposer_id}_since"] = time.time()
        del data["proposals"][proposer_id]
        save_data(data)

        proposer = self.bot.get_user(int(proposer_id))
        proposer_name = proposer.display_name if proposer else f"<@{proposer_id}>"

        embed = discord.Embed(
            title="💒 Just Married!",
            description=(
                f"🎉 **{proposer_name}** and **{interaction.user.display_name}** are now married!\n\n"
                f"May your journey together be filled with joy and happiness! 🥂"
            ),
            color=discord.Color.gold(),
        )
        embed.set_footer(text=f"Married on {format_timestamp(time.time())}")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="reject", description="Reject a marriage proposal.")
    async def reject(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        target_id = str(interaction.user.id)

        proposer_id = None
        for pid, proposal in data["proposals"].items():
            if proposal["to"] == target_id:
                proposer_id = pid
                break

        if not proposer_id:
            await interaction.followup.send(
                "❌ You don't have any pending proposals!", ephemeral=True
            )
            return

        del data["proposals"][proposer_id]
        save_data(data)

        proposer = self.bot.get_user(int(proposer_id))
        proposer_name = proposer.display_name if proposer else f"User"

        embed = discord.Embed(
            title="💔 Proposal Rejected",
            description=f"**{interaction.user.display_name}** rejected **{proposer_name}**'s proposal.",
            color=discord.Color.red(),
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="divorce", description="Divorce your current spouse.")
    async def divorce(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        user_id = str(interaction.user.id)
        spouse_id = get_spouse_id(data, user_id)

        if not spouse_id:
            await interaction.followup.send(
                "❌ You're not married!", ephemeral=True
            )
            return

        spouse = self.bot.get_user(int(spouse_id))
        spouse_name = spouse.display_name if spouse else f"<@{spouse_id}>"

        del data["marriages"][user_id]
        del data["marriages"][spouse_id]
        data["marriages"].pop(f"{user_id}_since", None)
        data["marriages"].pop(f"{spouse_id}_since", None)
        save_data(data)

        embed = discord.Embed(
            title="💔 Divorce",
            description=f"**{interaction.user.display_name}** and **{spouse_name}** are now divorced.",
            color=discord.Color.dark_gray(),
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="spouse", description="View your spouse or someone else's spouse.")
    @app_commands.describe(user="The user to check (leave empty to check yourself)")
    async def spouse(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        await interaction.response.defer()
        data = load_data()
        target = user or interaction.user
        target_id = str(target.id)
        spouse_id = get_spouse_id(data, target_id)

        if not spouse_id:
            name = "You are" if not user else f"{target.display_name} is"
            await interaction.followup.send(
                f"💔 {name} not currently married.", ephemeral=True
            )
            return

        spouse = self.bot.get_user(int(spouse_id))
        spouse_name = spouse.display_name if spouse else f"<@{spouse_id}>"
        since_ts = data["marriages"].get(f"{target_id}_since")
        since_str = format_timestamp(since_ts) if since_ts else "Unknown"

        embed = discord.Embed(
            title="💑 Marriage Info",
            color=discord.Color.pink(),
        )
        embed.add_field(name="💍 Married to", value=spouse_name, inline=True)
        embed.add_field(name="📅 Since", value=since_str, inline=True)
        embed.set_author(name=target.display_name, icon_url=target.display_avatar.url)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="marry", description="Alias for /propose — propose to another user!")
    @app_commands.describe(user="The user you want to marry")
    async def marry(self, interaction: discord.Interaction, user: discord.Member):
        await self.propose.callback(self, interaction, user)


async def setup(bot: commands.Bot):
    await bot.add_cog(MarriageCog(bot))
