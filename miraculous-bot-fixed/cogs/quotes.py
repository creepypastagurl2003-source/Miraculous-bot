import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import random
import time
from typing import Optional

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "quotes.json")
MAX_QUOTE_LENGTH = 500


def load_data() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"quotes": [], "next_id": 1}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def format_quote(q: dict, show_id: bool = True) -> discord.Embed:
    embed = discord.Embed(
        description=f'*"{q["text"]}"*',
        color=discord.Color.blurple(),
    )
    author_str = q.get("attributed_to") or q.get("added_by_name", "Unknown")
    embed.add_field(name="— Author", value=author_str, inline=True)
    embed.add_field(name="📅 Added", value=q.get("added_by_name", "Unknown"), inline=True)
    if show_id:
        embed.set_footer(text=f"Quote #{q['id']}")
    return embed


def format_timestamp(ts: float) -> str:
    import datetime
    dt = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
    return dt.strftime("%B %d, %Y")


class QuoteCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    quote_group = app_commands.Group(name="quote", description="Quote system commands")

    @quote_group.command(name="add", description="Add a quote to the server's quote book.")
    @app_commands.describe(
        text="The quote text",
        author="Who said it (optional, defaults to 'Anonymous')",
    )
    async def add(
        self,
        interaction: discord.Interaction,
        text: str,
        author: Optional[str] = None,
    ):
        await interaction.response.defer()
        if len(text) > MAX_QUOTE_LENGTH:
            await interaction.followup.send(
                f"❌ Quote is too long! Max {MAX_QUOTE_LENGTH} characters.", ephemeral=True
            )
            return

        data = load_data()
        quote_id = data["next_id"]
        quote = {
            "id": quote_id,
            "text": text,
            "attributed_to": author or "Anonymous",
            "added_by": str(interaction.user.id),
            "added_by_name": interaction.user.display_name,
            "guild_id": str(interaction.guild_id) if interaction.guild_id else None,
            "timestamp": time.time(),
        }
        data["quotes"].append(quote)
        data["next_id"] += 1
        save_data(data)

        embed = discord.Embed(
            title="📖 Quote Added!",
            description=f'*"{text}"*',
            color=discord.Color.green(),
        )
        embed.add_field(name="— Author", value=author or "Anonymous", inline=True)
        embed.set_footer(text=f"Quote #{quote_id} added by {interaction.user.display_name}")
        await interaction.followup.send(embed=embed)

    @quote_group.command(name="get", description="Get a specific quote by its ID.")
    @app_commands.describe(id="The quote ID number")
    async def get(self, interaction: discord.Interaction, id: int):
        await interaction.response.defer()
        data = load_data()
        guild_id = str(interaction.guild_id) if interaction.guild_id else None
        quotes = [
            q for q in data["quotes"]
            if q["id"] == id and (q.get("guild_id") == guild_id or guild_id is None)
        ]

        if not quotes:
            await interaction.followup.send(
                f"❌ No quote found with ID #{id}.", ephemeral=True
            )
            return

        q = quotes[0]
        embed = discord.Embed(
            description=f'*"{q["text"]}"*',
            color=discord.Color.blurple(),
        )
        embed.add_field(name="— Author", value=q.get("attributed_to", "Anonymous"), inline=True)
        embed.add_field(name="Added by", value=q.get("added_by_name", "Unknown"), inline=True)
        embed.add_field(name="Date", value=format_timestamp(q.get("timestamp", 0)), inline=True)
        embed.set_footer(text=f"Quote #{q['id']}")
        await interaction.followup.send(embed=embed)

    @quote_group.command(name="random", description="Get a random quote from the quote book.")
    async def random_quote(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        guild_id = str(interaction.guild_id) if interaction.guild_id else None
        quotes = [
            q for q in data["quotes"]
            if q.get("guild_id") == guild_id or guild_id is None
        ]

        if not quotes:
            await interaction.followup.send(
                "❌ No quotes yet! Use `/quote add` to add some.", ephemeral=True
            )
            return

        q = random.choice(quotes)
        embed = discord.Embed(
            description=f'*"{q["text"]}"*',
            color=discord.Color.blurple(),
        )
        embed.add_field(name="— Author", value=q.get("attributed_to", "Anonymous"), inline=True)
        embed.add_field(name="Added by", value=q.get("added_by_name", "Unknown"), inline=True)
        embed.set_footer(text=f"Quote #{q['id']} • {len(quotes)} quote(s) total")
        await interaction.followup.send(embed=embed)

    @quote_group.command(name="list", description="List the most recent quotes.")
    @app_commands.describe(page="Page number (default: 1)")
    async def list_quotes(self, interaction: discord.Interaction, page: int = 1):
        await interaction.response.defer()
        data = load_data()
        guild_id = str(interaction.guild_id) if interaction.guild_id else None
        quotes = [
            q for q in data["quotes"]
            if q.get("guild_id") == guild_id or guild_id is None
        ]

        if not quotes:
            await interaction.followup.send(
                "❌ No quotes yet! Use `/quote add` to add some.", ephemeral=True
            )
            return

        per_page = 5
        total_pages = max(1, (len(quotes) + per_page - 1) // per_page)
        page = max(1, min(page, total_pages))
        start = (page - 1) * per_page
        page_quotes = list(reversed(quotes))[start : start + per_page]

        embed = discord.Embed(
            title="📚 Quote Book",
            color=discord.Color.blurple(),
        )
        for q in page_quotes:
            text = q["text"]
            if len(text) > 80:
                text = text[:77] + "..."
            embed.add_field(
                name=f"#{q['id']} — {q.get('attributed_to', 'Anonymous')}",
                value=f'*"{text}"*',
                inline=False,
            )
        embed.set_footer(text=f"Page {page}/{total_pages} • {len(quotes)} quotes total")
        await interaction.followup.send(embed=embed)

    @quote_group.command(name="search", description="Search for quotes by keyword or author.")
    @app_commands.describe(query="Text or author name to search for")
    async def search(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        data = load_data()
        guild_id = str(interaction.guild_id) if interaction.guild_id else None
        q_lower = query.lower()
        matches = [
            q for q in data["quotes"]
            if (q.get("guild_id") == guild_id or guild_id is None)
            and (
                q_lower in q["text"].lower()
                or q_lower in q.get("attributed_to", "").lower()
                or q_lower in q.get("added_by_name", "").lower()
            )
        ]

        if not matches:
            await interaction.followup.send(
                f"❌ No quotes found matching **{query}**.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"🔍 Search: \"{query}\"",
            description=f"Found {len(matches)} result(s):",
            color=discord.Color.blurple(),
        )
        for q in matches[:10]:
            text = q["text"]
            if len(text) > 80:
                text = text[:77] + "..."
            embed.add_field(
                name=f"#{q['id']} — {q.get('attributed_to', 'Anonymous')}",
                value=f'*"{text}"*',
                inline=False,
            )
        if len(matches) > 10:
            embed.set_footer(text=f"Showing first 10 of {len(matches)} results")
        await interaction.followup.send(embed=embed)

    @quote_group.command(name="delete", description="Delete a quote (server admins only).")
    @app_commands.describe(id="The quote ID to delete")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def delete(self, interaction: discord.Interaction, id: int):
        await interaction.response.defer()
        data = load_data()
        guild_id = str(interaction.guild_id) if interaction.guild_id else None
        original_count = len(data["quotes"])
        data["quotes"] = [
            q for q in data["quotes"]
            if not (q["id"] == id and (q.get("guild_id") == guild_id or guild_id is None))
        ]

        if len(data["quotes"]) == original_count:
            await interaction.followup.send(
                f"❌ No quote found with ID #{id}.", ephemeral=True
            )
            return

        save_data(data)
        await interaction.followup.send(
            f"✅ Quote #{id} has been deleted.", ephemeral=True
        )

    @delete.error
    async def delete_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.followup.send(
                "❌ You need the **Manage Messages** permission to delete quotes.", ephemeral=True
            )

    @quote_group.command(name="stats", description="View quote statistics for this server.")
    async def stats(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        guild_id = str(interaction.guild_id) if interaction.guild_id else None
        quotes = [
            q for q in data["quotes"]
            if q.get("guild_id") == guild_id or guild_id is None
        ]

        if not quotes:
            await interaction.followup.send(
                "❌ No quotes yet!", ephemeral=True
            )
            return

        contributor_counts: dict[str, int] = {}
        for q in quotes:
            name = q.get("added_by_name", "Unknown")
            contributor_counts[name] = contributor_counts.get(name, 0) + 1

        top = sorted(contributor_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        embed = discord.Embed(
            title="📊 Quote Stats",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Total Quotes", value=str(len(quotes)), inline=True)
        embed.add_field(name="Latest ID", value=f"#{data['next_id'] - 1}", inline=True)
        top_str = "\n".join(f"{i+1}. **{name}** — {count}" for i, (name, count) in enumerate(top))
        embed.add_field(name="🏆 Top Contributors", value=top_str or "None", inline=False)
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(QuoteCog(bot))
