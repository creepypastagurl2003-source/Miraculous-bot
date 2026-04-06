import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import time
from typing import Optional

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "family.json")

MAX_CHILDREN = 20
MAX_TREE_DEPTH = 5


def load_data() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"relationships": {}, "pending_adoptions": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_user_data(data: dict, user_id: str) -> dict:
    if user_id not in data["relationships"]:
        data["relationships"][user_id] = {"parent": None, "children": []}
    return data["relationships"][user_id]


def is_ancestor(data: dict, ancestor_id: str, descendant_id: str) -> bool:
    """Check if ancestor_id is an ancestor of descendant_id (prevents circular trees)."""
    visited = set()
    current = descendant_id
    while current:
        if current in visited:
            break
        visited.add(current)
        ud = data["relationships"].get(current, {})
        parent = ud.get("parent")
        if parent == ancestor_id:
            return True
        current = parent
    return False


def build_tree_lines(data: dict, user_id: str, bot, depth: int = 0, max_depth: int = MAX_TREE_DEPTH) -> list[str]:
    """Recursively build tree display lines."""
    if depth > max_depth:
        return []
    ud = data["relationships"].get(user_id, {})
    children = ud.get("children", [])
    lines = []
    for i, child_id in enumerate(children):
        is_last = i == len(children) - 1
        connector = "└─" if is_last else "├─"
        prefix = "│  " * depth
        child_name = f"<@{child_id}>"
        lines.append(f"{prefix}{connector} 👶 {child_name}")
        sub_children = data["relationships"].get(child_id, {}).get("children", [])
        if sub_children and depth < max_depth:
            child_prefix = "│  " * depth + ("   " if is_last else "│  ")
            sub_lines = build_tree_lines(data, child_id, bot, depth + 1, max_depth)
            lines.extend(sub_lines)
    return lines


class FamilyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    family_group = app_commands.Group(name="family", description="Family tree commands")

    @family_group.command(name="adopt", description="Send an adoption request to a user.")
    @app_commands.describe(user="The user you want to adopt as your child")
    async def adopt(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer()
        data = load_data()
        parent_id = str(interaction.user.id)
        child_id = str(user.id)

        if user.id == interaction.user.id:
            await interaction.followup.send("❌ You can't adopt yourself!", ephemeral=True)
            return

        if user.bot:
            await interaction.followup.send("❌ You can't adopt a bot!", ephemeral=True)
            return

        parent_data = get_user_data(data, parent_id)
        child_data = get_user_data(data, child_id)

        if child_data.get("parent"):
            await interaction.followup.send(
                f"❌ {user.display_name} already has a parent! They need to use `/family emancipate` first.",
                ephemeral=True,
            )
            return

        if len(parent_data.get("children", [])) >= MAX_CHILDREN:
            await interaction.followup.send(
                f"❌ You already have {MAX_CHILDREN} children! That's the limit.", ephemeral=True
            )
            return

        if child_id in parent_data.get("children", []):
            await interaction.followup.send(
                f"❌ {user.display_name} is already your child!", ephemeral=True
            )
            return

        if is_ancestor(data, child_id, parent_id):
            await interaction.followup.send(
                "❌ You can't adopt someone who is already your ancestor — that would create a loop!",
                ephemeral=True,
            )
            return

        if is_ancestor(data, parent_id, child_id):
            pass

        if child_id in data["pending_adoptions"]:
            existing = data["pending_adoptions"][child_id]
            if existing["parent_id"] == parent_id:
                await interaction.followup.send(
                    f"❌ You already have a pending adoption request for {user.display_name}!",
                    ephemeral=True,
                )
                return

        data["pending_adoptions"][child_id] = {
            "parent_id": parent_id,
            "parent_name": interaction.user.display_name,
            "timestamp": time.time(),
        }
        save_data(data)

        embed = discord.Embed(
            title="👨‍👧 Adoption Request!",
            description=(
                f"**{interaction.user.display_name}** wants to adopt **{user.display_name}**!\n\n"
                f"{user.mention}, do you want to join their family?\n\n"
                f"Use `/family accept` to say yes, or `/family decline` to decline."
            ),
            color=discord.Color.blue(),
        )
        embed.set_footer(text="This request will stay open until accepted or declined.")
        await interaction.followup.send(embed=embed)

    @family_group.command(name="accept", description="Accept a pending adoption request.")
    async def accept(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        child_id = str(interaction.user.id)

        if child_id not in data["pending_adoptions"]:
            await interaction.followup.send(
                "❌ You don't have any pending adoption requests!", ephemeral=True
            )
            return

        pending = data["pending_adoptions"][child_id]
        parent_id = pending["parent_id"]

        child_data = get_user_data(data, child_id)
        parent_data = get_user_data(data, parent_id)

        if child_data.get("parent"):
            del data["pending_adoptions"][child_id]
            save_data(data)
            await interaction.followup.send(
                "❌ You already have a parent! Use `/family emancipate` first.", ephemeral=True
            )
            return

        if len(parent_data.get("children", [])) >= MAX_CHILDREN:
            del data["pending_adoptions"][child_id]
            save_data(data)
            await interaction.followup.send(
                "❌ Your adopter already has too many children! Request cancelled.", ephemeral=True
            )
            return

        child_data["parent"] = parent_id
        if child_id not in parent_data["children"]:
            parent_data["children"].append(child_id)

        del data["pending_adoptions"][child_id]
        save_data(data)

        parent = self.bot.get_user(int(parent_id))
        parent_name = parent.display_name if parent else pending.get("parent_name", f"<@{parent_id}>")

        embed = discord.Embed(
            title="👨‍👧 Family Grows!",
            description=(
                f"🎉 **{interaction.user.display_name}** has been adopted by **{parent_name}**!\n\n"
                f"Welcome to the family! 🏠"
            ),
            color=discord.Color.green(),
        )
        await interaction.followup.send(embed=embed)

    @family_group.command(name="decline", description="Decline a pending adoption request.")
    async def decline(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        child_id = str(interaction.user.id)

        if child_id not in data["pending_adoptions"]:
            await interaction.followup.send(
                "❌ You don't have any pending adoption requests!", ephemeral=True
            )
            return

        pending = data["pending_adoptions"][child_id]
        del data["pending_adoptions"][child_id]
        save_data(data)

        embed = discord.Embed(
            title="🚫 Adoption Declined",
            description=f"**{interaction.user.display_name}** declined the adoption request from **{pending.get('parent_name', 'Unknown')}**.",
            color=discord.Color.red(),
        )
        await interaction.followup.send(embed=embed)

    @family_group.command(name="disown", description="Remove a child from your family.")
    @app_commands.describe(user="The child you want to disown")
    async def disown(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer()
        data = load_data()
        parent_id = str(interaction.user.id)
        child_id = str(user.id)

        parent_data = get_user_data(data, parent_id)

        if child_id not in parent_data.get("children", []):
            await interaction.followup.send(
                f"❌ {user.display_name} is not your child!", ephemeral=True
            )
            return

        parent_data["children"].remove(child_id)

        child_data = get_user_data(data, child_id)
        if child_data.get("parent") == parent_id:
            child_data["parent"] = None

        save_data(data)

        embed = discord.Embed(
            title="💔 Disowned",
            description=f"**{interaction.user.display_name}** has disowned **{user.display_name}**.",
            color=discord.Color.dark_gray(),
        )
        await interaction.followup.send(embed=embed)

    @family_group.command(name="emancipate", description="Leave your parent's family.")
    async def emancipate(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        child_id = str(interaction.user.id)
        child_data = get_user_data(data, child_id)

        parent_id = child_data.get("parent")
        if not parent_id:
            await interaction.followup.send(
                "❌ You don't have a parent to leave!", ephemeral=True
            )
            return

        parent_data = get_user_data(data, parent_id)
        if child_id in parent_data.get("children", []):
            parent_data["children"].remove(child_id)

        child_data["parent"] = None
        save_data(data)

        parent = self.bot.get_user(int(parent_id))
        parent_name = parent.display_name if parent else f"<@{parent_id}>"

        embed = discord.Embed(
            title="🏠 Emancipated",
            description=f"**{interaction.user.display_name}** has left **{parent_name}**'s family.",
            color=discord.Color.orange(),
        )
        await interaction.followup.send(embed=embed)

    @family_group.command(name="tree", description="View someone's family tree.")
    @app_commands.describe(user="Whose family tree to view (default: yourself)")
    async def tree(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        await interaction.response.defer()
        data = load_data()
        target = user or interaction.user
        target_id = str(target.id)

        target_data = get_user_data(data, target_id)
        parent_id = target_data.get("parent")
        children = target_data.get("children", [])

        lines = []

        if parent_id:
            parent = self.bot.get_user(int(parent_id))
            parent_name = parent.display_name if parent else f"<@{parent_id}>"
            grandparent_id = data["relationships"].get(parent_id, {}).get("parent")
            if grandparent_id:
                gp = self.bot.get_user(int(grandparent_id))
                gp_name = gp.display_name if gp else f"<@{grandparent_id}>"
                lines.append(f"👴 **{gp_name}** *(grandparent)*")
                lines.append(f"└─ 👨 **{parent_name}** *(parent)*")
                lines.append(f"   └─ 👤 **{target.display_name}** *(you)*")
            else:
                lines.append(f"👨 **{parent_name}** *(parent)*")
                lines.append(f"└─ 👤 **{target.display_name}** *(you)*")

            siblings = [
                c for c in data["relationships"].get(parent_id, {}).get("children", [])
                if c != target_id
            ]
            if siblings:
                for sib_id in siblings[:5]:
                    sib = self.bot.get_user(int(sib_id))
                    sib_name = sib.display_name if sib else f"<@{sib_id}>"
                    lines.append(f"   ├─ 👥 **{sib_name}** *(sibling)*")
                if len(siblings) > 5:
                    lines.append(f"   └─ *...and {len(siblings) - 5} more siblings*")
        else:
            lines.append(f"👤 **{target.display_name}** *(you)*")

        if children:
            child_indent = "   " if parent_id else ""
            for i, child_id in enumerate(children[:10]):
                is_last = i == len(children) - 1
                connector = "└─" if is_last else "├─"
                child = self.bot.get_user(int(child_id))
                child_name = child.display_name if child else f"<@{child_id}>"
                lines.append(f"{child_indent}{connector} 👶 **{child_name}** *(child)*")

                grandchildren = data["relationships"].get(child_id, {}).get("children", [])
                if grandchildren:
                    gc_indent = child_indent + ("   " if is_last else "│  ")
                    for j, gc_id in enumerate(grandchildren[:3]):
                        gc = self.bot.get_user(int(gc_id))
                        gc_name = gc.display_name if gc else f"<@{gc_id}>"
                        gc_conn = "└─" if j == len(grandchildren[:3]) - 1 else "├─"
                        lines.append(f"{gc_indent}{gc_conn} 👼 **{gc_name}** *(grandchild)*")
                    if len(grandchildren) > 3:
                        lines.append(f"{gc_indent}   *...and {len(grandchildren) - 3} more*")

            if len(children) > 10:
                lines.append(f"{child_indent}   *...and {len(children) - 10} more children*")

        if not parent_id and not children:
            lines.append("\n*No family connections yet.*")

        tree_text = "\n".join(lines) if lines else "*No family connections yet.*"

        embed = discord.Embed(
            title=f"🌳 {target.display_name}'s Family Tree",
            description=tree_text,
            color=discord.Color.from_rgb(101, 196, 102),
        )
        embed.set_thumbnail(url=target.display_avatar.url)

        stats = []
        if parent_id:
            stats.append("👨 1 parent")
        siblings_list = []
        if parent_id:
            siblings_list = [
                c for c in data["relationships"].get(parent_id, {}).get("children", [])
                if c != target_id
            ]
        if siblings_list:
            stats.append(f"👥 {len(siblings_list)} sibling(s)")
        if children:
            stats.append(f"👶 {len(children)} child(ren)")

        if stats:
            embed.set_footer(text=" • ".join(stats))

        await interaction.followup.send(embed=embed)

    @family_group.command(name="parent", description="View your parent (or someone else's).")
    @app_commands.describe(user="Whose parent to look up (default: yourself)")
    async def parent(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        await interaction.response.defer()
        data = load_data()
        target = user or interaction.user
        target_id = str(target.id)
        ud = get_user_data(data, target_id)
        parent_id = ud.get("parent")

        if not parent_id:
            name = "You don't" if not user else f"{target.display_name} doesn't"
            await interaction.followup.send(
                f"❌ {name} have a parent.", ephemeral=True
            )
            return

        parent = self.bot.get_user(int(parent_id))
        parent_name = parent.display_name if parent else f"<@{parent_id}>"
        embed = discord.Embed(
            title="👨 Parent Info",
            description=f"**{target.display_name}**'s parent is **{parent_name}**",
            color=discord.Color.blue(),
        )
        if parent:
            embed.set_thumbnail(url=parent.display_avatar.url)
        await interaction.followup.send(embed=embed)

    @family_group.command(name="children", description="View your children (or someone else's).")
    @app_commands.describe(user="Whose children to look up (default: yourself)")
    async def children(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        await interaction.response.defer()
        data = load_data()
        target = user or interaction.user
        target_id = str(target.id)
        ud = get_user_data(data, target_id)
        child_ids = ud.get("children", [])

        if not child_ids:
            name = "You don't" if not user else f"{target.display_name} doesn't"
            await interaction.followup.send(
                f"❌ {name} have any children.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"👶 {target.display_name}'s Children",
            color=discord.Color.blue(),
        )
        child_list = []
        for cid in child_ids:
            c = self.bot.get_user(int(cid))
            child_list.append(c.display_name if c else f"<@{cid}>")
        embed.description = "\n".join(f"• **{n}**" for n in child_list)
        embed.set_footer(text=f"{len(child_ids)} child(ren) total")
        await interaction.followup.send(embed=embed)

    @family_group.command(name="siblings", description="View your siblings (or someone else's).")
    @app_commands.describe(user="Whose siblings to look up (default: yourself)")
    async def siblings(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        await interaction.response.defer()
        data = load_data()
        target = user or interaction.user
        target_id = str(target.id)
        ud = get_user_data(data, target_id)
        parent_id = ud.get("parent")

        if not parent_id:
            name = "You don't" if not user else f"{target.display_name} doesn't"
            await interaction.followup.send(
                f"❌ {name} have a parent, so no siblings either.", ephemeral=True
            )
            return

        sibling_ids = [
            c for c in data["relationships"].get(parent_id, {}).get("children", [])
            if c != target_id
        ]

        if not sibling_ids:
            await interaction.followup.send(
                f"❌ {'You have' if not user else f'{target.display_name} has'} no siblings.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"👥 {target.display_name}'s Siblings",
            color=discord.Color.purple(),
        )
        sib_list = []
        for sid in sibling_ids:
            s = self.bot.get_user(int(sid))
            sib_list.append(s.display_name if s else f"<@{sid}>")
        embed.description = "\n".join(f"• **{n}**" for n in sib_list)
        embed.set_footer(text=f"{len(sibling_ids)} sibling(s)")
        await interaction.followup.send(embed=embed)

    @family_group.command(name="pending", description="Check if you have a pending adoption request.")
    async def pending(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        child_id = str(interaction.user.id)

        if child_id not in data["pending_adoptions"]:
            await interaction.followup.send(
                "❌ You have no pending adoption requests.", ephemeral=True
            )
            return

        p = data["pending_adoptions"][child_id]
        parent = self.bot.get_user(int(p["parent_id"]))
        parent_name = parent.display_name if parent else p.get("parent_name", f"<@{p['parent_id']}>")

        embed = discord.Embed(
            title="📬 Pending Adoption Request",
            description=(
                f"**{parent_name}** wants to adopt you!\n\n"
                f"Use `/family accept` to join their family, or `/family decline` to decline."
            ),
            color=discord.Color.gold(),
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(FamilyCog(bot))
