import asyncio
import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import logging
from typing import Optional

logger = logging.getLogger("bot.reaction_roles")

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "reaction_roles.json")

PANEL_COLORS = {
    "red": 0xFF4444,
    "blue": 0x4488FF,
    "green": 0x44CC88,
    "purple": 0xAA44FF,
    "gold": 0xFFCC00,
    "pink": 0xFF88CC,
    "cyan": 0x44CCFF,
    "orange": 0xFF8844,
}

COLOR_CHOICES = [
    app_commands.Choice(name=name.capitalize(), value=name)
    for name in PANEL_COLORS
]


def load_data() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def emoji_to_str(emoji: discord.PartialEmoji | str) -> str:
    if isinstance(emoji, str):
        return emoji
    if emoji.id:
        return f"<:{emoji.name}:{emoji.id}>"
    return emoji.name


def str_to_display(emoji_str: str) -> str:
    return emoji_str


def build_panel_embed(panel: dict, color: int) -> discord.Embed:
    embed = discord.Embed(
        title=panel["title"],
        description=panel.get("description", "React below to receive your roles!"),
        color=color,
    )
    roles = panel.get("roles", {})
    if roles:
        lines = []
        for emoji_str, role_id in roles.items():
            lines.append(f"{emoji_str} → <@&{role_id}>")
        embed.add_field(name="Available Roles", value="\n".join(lines), inline=False)
    else:
        embed.add_field(
            name="No Roles Yet",
            value="An admin will add roles to this panel soon.",
            inline=False,
        )
    embed.set_footer(text="Click a reaction below to get or remove a role!")
    return embed


class ReactionRolesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    rr_group = app_commands.Group(
        name="reactionrole",
        description="Reaction role panel management (Admin only)",
        default_permissions=discord.Permissions(manage_roles=True),
    )

    @rr_group.command(name="create", description="Create a new reaction role panel in this channel.")
    @app_commands.describe(
        title="Title for the reaction role panel",
        description="Subtitle / instructions shown under the title",
        color="Embed color (default: blue)",
    )
    @app_commands.choices(color=COLOR_CHOICES)
    async def create_panel(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str = "React below to receive your roles!",
        color: str = "blue",
    ):
        await interaction.response.defer(ephemeral=True)

        panel_color = PANEL_COLORS.get(color, 0x4488FF)
        panel = {
            "title": title,
            "description": description,
            "color": panel_color,
            "channel_id": str(interaction.channel_id),
            "guild_id": str(interaction.guild_id),
            "roles": {},
        }

        embed = build_panel_embed(panel, panel_color)
        msg = await interaction.channel.send(embed=embed)

        data = load_data()
        guild_id = str(interaction.guild_id)
        if guild_id not in data:
            data[guild_id] = {}
        data[guild_id][str(msg.id)] = panel
        save_data(data)

        await interaction.followup.send(
            f"✅ Reaction role panel created! Message ID: `{msg.id}`\n"
            f"Use `/reactionrole add {msg.id} [emoji] [role]` to add roles.",
            ephemeral=True,
        )

    @rr_group.command(name="add", description="Add an emoji → role mapping to a reaction role panel.")
    @app_commands.describe(
        message_id="The ID of the reaction role panel message",
        emoji="The emoji to react with",
        role="The role to assign for this emoji",
    )
    async def add_role(
        self,
        interaction: discord.Interaction,
        message_id: str,
        emoji: str,
        role: discord.Role,
    ):
        await interaction.response.defer(ephemeral=True)

        guild_id = str(interaction.guild_id)
        data = load_data()

        if guild_id not in data or message_id not in data[guild_id]:
            await interaction.followup.send(
                "❌ No reaction role panel found with that message ID.", ephemeral=True
            )
            return

        if role >= interaction.guild.me.top_role:
            await interaction.followup.send(
                f"❌ I can't assign **{role.name}** — it's higher than or equal to my highest role. "
                "Please move my role above it in Server Settings → Roles.",
                ephemeral=True,
            )
            return

        if role.managed:
            await interaction.followup.send(
                f"❌ **{role.name}** is managed by an integration and cannot be assigned.", ephemeral=True
            )
            return

        emoji_str = emoji.strip()
        panel = data[guild_id][message_id]

        if len(panel["roles"]) >= 20:
            await interaction.followup.send(
                "❌ A panel can have at most 20 emoji-role pairs.", ephemeral=True
            )
            return

        if emoji_str in panel["roles"]:
            await interaction.followup.send(
                f"❌ {emoji_str} is already mapped to a role on this panel. Remove it first.",
                ephemeral=True,
            )
            return

        panel["roles"][emoji_str] = str(role.id)
        save_data(data)

        channel = interaction.guild.get_channel(int(panel["channel_id"]))
        if channel:
            try:
                msg = await channel.fetch_message(int(message_id))
                updated_embed = build_panel_embed(panel, panel["color"])
                await msg.edit(embed=updated_embed)
                await msg.add_reaction(emoji_str)
            except (discord.NotFound, discord.HTTPException) as e:
                logger.warning(f"Could not update panel message: {e}")

        await interaction.followup.send(
            f"✅ Added: {emoji_str} → **{role.name}**\nMembers can now react with {emoji_str} to get the role!",
            ephemeral=True,
        )

    @rr_group.command(name="remove", description="Remove an emoji → role mapping from a panel.")
    @app_commands.describe(
        message_id="The ID of the reaction role panel message",
        emoji="The emoji mapping to remove",
    )
    async def remove_role(
        self,
        interaction: discord.Interaction,
        message_id: str,
        emoji: str,
    ):
        await interaction.response.defer(ephemeral=True)

        guild_id = str(interaction.guild_id)
        data = load_data()

        if guild_id not in data or message_id not in data[guild_id]:
            await interaction.followup.send("❌ Panel not found.", ephemeral=True)
            return

        panel = data[guild_id][message_id]
        emoji_str = emoji.strip()

        if emoji_str not in panel["roles"]:
            await interaction.followup.send(
                f"❌ {emoji_str} is not mapped on this panel.", ephemeral=True
            )
            return

        role_id = panel["roles"].pop(emoji_str)
        save_data(data)

        channel = interaction.guild.get_channel(int(panel["channel_id"]))
        if channel:
            try:
                msg = await channel.fetch_message(int(message_id))
                updated_embed = build_panel_embed(panel, panel["color"])
                await msg.edit(embed=updated_embed)
                await msg.clear_reaction(emoji_str)
            except (discord.NotFound, discord.HTTPException) as e:
                logger.warning(f"Could not update panel message: {e}")

        await interaction.followup.send(
            f"✅ Removed the {emoji_str} mapping (was <@&{role_id}>).", ephemeral=True
        )

    @rr_group.command(name="list", description="List all reaction role panels in this server.")
    async def list_panels(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        guild_id = str(interaction.guild_id)
        data = load_data()
        panels = data.get(guild_id, {})

        if not panels:
            await interaction.followup.send(
                "❌ No reaction role panels in this server. Use `/reactionrole create` to make one.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="📋 Reaction Role Panels",
            color=0x4488FF,
        )

        for msg_id, panel in panels.items():
            channel = interaction.guild.get_channel(int(panel["channel_id"]))
            channel_mention = channel.mention if channel else f"<#{panel['channel_id']}>"
            roles_text = "\n".join(
                f"{e} → <@&{r}>" for e, r in panel["roles"].items()
            ) or "*No roles added yet*"
            embed.add_field(
                name=f"📌 {panel['title']} (ID: `{msg_id}`)",
                value=f"**Channel:** {channel_mention}\n{roles_text}",
                inline=False,
            )

        embed.set_footer(text=f"{len(panels)} panel(s) total")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @rr_group.command(name="delete", description="Delete an entire reaction role panel.")
    @app_commands.describe(message_id="The ID of the panel message to delete")
    async def delete_panel(
        self,
        interaction: discord.Interaction,
        message_id: str,
    ):
        await interaction.response.defer(ephemeral=True)

        guild_id = str(interaction.guild_id)
        data = load_data()

        if guild_id not in data or message_id not in data[guild_id]:
            await interaction.followup.send("❌ Panel not found.", ephemeral=True)
            return

        panel = data[guild_id].pop(message_id)
        save_data(data)

        channel = interaction.guild.get_channel(int(panel["channel_id"]))
        if channel:
            try:
                msg = await channel.fetch_message(int(message_id))
                await msg.delete()
            except (discord.NotFound, discord.HTTPException):
                pass

        await interaction.followup.send(
            f"✅ Deleted the **{panel['title']}** reaction role panel.", ephemeral=True
        )

    @rr_group.command(name="edit", description="Edit the title or description of an existing panel.")
    @app_commands.describe(
        message_id="The ID of the panel message to edit",
        title="New title (leave blank to keep current)",
        description="New description (leave blank to keep current)",
        color="New color (leave blank to keep current)",
    )
    @app_commands.choices(color=COLOR_CHOICES)
    async def edit_panel(
        self,
        interaction: discord.Interaction,
        message_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
    ):
        await interaction.response.defer(ephemeral=True)

        guild_id = str(interaction.guild_id)
        data = load_data()

        if guild_id not in data or message_id not in data[guild_id]:
            await interaction.followup.send("❌ Panel not found.", ephemeral=True)
            return

        panel = data[guild_id][message_id]
        if title:
            panel["title"] = title
        if description:
            panel["description"] = description
        if color:
            panel["color"] = PANEL_COLORS.get(color, panel["color"])

        save_data(data)

        channel = interaction.guild.get_channel(int(panel["channel_id"]))
        if channel:
            try:
                msg = await channel.fetch_message(int(message_id))
                updated_embed = build_panel_embed(panel, panel["color"])
                await msg.edit(embed=updated_embed)
            except (discord.NotFound, discord.HTTPException) as e:
                logger.warning(f"Could not edit panel message: {e}")

        await interaction.followup.send("✅ Panel updated!", ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.member and payload.member.bot:
            return

        data = load_data()
        guild_id = str(payload.guild_id)
        message_id = str(payload.message_id)

        if guild_id not in data or message_id not in data[guild_id]:
            return

        panel = data[guild_id][message_id]
        emoji_str = emoji_to_str(payload.emoji)

        role_id = panel["roles"].get(emoji_str)
        if not role_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        role = guild.get_role(int(role_id))
        if not role:
            logger.warning(f"Role {role_id} not found in guild {guild_id}")
            return

        member = payload.member or guild.get_member(payload.user_id)
        if not member:
            return

        try:
            await member.add_roles(role, reason="Reaction role")
            logger.info(f"Added role {role.name} to {member.display_name} via reaction role")
        except discord.Forbidden:
            logger.warning(f"Missing permissions to add role {role.name}")
        except discord.HTTPException as e:
            logger.error(f"Failed to add role: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        data = load_data()
        guild_id = str(payload.guild_id)
        message_id = str(payload.message_id)

        if guild_id not in data or message_id not in data[guild_id]:
            return

        panel = data[guild_id][message_id]
        emoji_str = emoji_to_str(payload.emoji)

        role_id = panel["roles"].get(emoji_str)
        if not role_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        role = guild.get_role(int(role_id))
        if not role:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        if member.bot:
            return

        try:
            await member.remove_roles(role, reason="Reaction role removed")
            logger.info(f"Removed role {role.name} from {member.display_name} via reaction role")
        except discord.Forbidden:
            logger.warning(f"Missing permissions to remove role {role.name}")
        except discord.HTTPException as e:
            logger.error(f"Failed to remove role: {e}")

    @create_panel.error
    @add_role.error
    @remove_role.error
    @list_panels.error
    @delete_panel.error
    @edit_panel.error
    async def admin_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.followup.send(
                "❌ You need the **Manage Roles** permission to use reaction role commands.",
                ephemeral=True,
            )

    # ── Prefix command group (!rr / !reactionrole) ──────────────────────────

    @commands.group(name="reactionrole", aliases=["rr"], invoke_without_command=True)
    @commands.has_permissions(manage_roles=True)
    async def prefix_rr(self, ctx: commands.Context):
        """Reaction role management via prefix commands."""
        embed = discord.Embed(
            title="🎭 Reaction Role Commands",
            color=0x4488FF,
            description=(
                "**`!rr create`** — Interactive panel setup wizard\n"
                "**`!rr add <msg_id> <emoji> <@role>`** — Add emoji → role to a panel\n"
                "**`!rr remove <msg_id> <emoji>`** — Remove emoji → role from a panel\n"
                "**`!rr list`** — View all panels in this server\n"
                "**`!rr delete <msg_id>`** — Delete a panel and its message\n\n"
                "Slash commands also available: `/reactionrole create|add|remove|list|delete|edit`"
            ),
        )
        embed.set_footer(text="Requires Manage Roles permission • prefix: !")
        await ctx.send(embed=embed)

    @prefix_rr.command(name="create")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True, add_reactions=True)
    async def prefix_rr_create(self, ctx: commands.Context):
        """Interactive reaction role panel creation wizard."""

        def check(m: discord.Message) -> bool:
            return m.author == ctx.author and m.channel == ctx.channel

        async def ask(prompt: str, timeout: float = 60.0) -> Optional[str]:
            prompt_msg = await ctx.send(prompt)
            try:
                reply = await self.bot.wait_for("message", check=check, timeout=timeout)
                return reply.content.strip()
            except asyncio.TimeoutError:
                await ctx.send("⏱️ Timed out. Run `!rr create` again to start over.")
                return None

        # ── Step 1: title ────────────────────────────────────────────────────
        title = await ask(
            "**📋 Step 1 / 3 — Panel Title**\n"
            "What should the title of the reaction role panel be?\n"
            "*(Type any text, or `cancel` to abort)*"
        )
        if not title or title.lower() == "cancel":
            await ctx.send("❌ Cancelled.")
            return

        # ── Step 2: description ───────────────────────────────────────────────
        desc_raw = await ask(
            "**📋 Step 2 / 3 — Description**\n"
            "What description should appear under the title?\n"
            "*(Type text, or `skip` to use the default)*"
        )
        if desc_raw is None or desc_raw.lower() == "cancel":
            await ctx.send("❌ Cancelled.")
            return
        description = "React below to receive your roles!" if desc_raw.lower() == "skip" else desc_raw

        # ── Step 3: color ─────────────────────────────────────────────────────
        color_raw = await ask(
            "**📋 Step 3 / 3 — Color**\n"
            "Choose an embed color:\n"
            "`red` · `blue` · `green` · `purple` · `gold` · `pink` · `cyan` · `orange`\n"
            "*(Or `skip` for blue)*"
        )
        if color_raw is None or color_raw.lower() == "cancel":
            await ctx.send("❌ Cancelled.")
            return
        panel_color = PANEL_COLORS.get(color_raw.lower().strip(), 0x4488FF)

        # ── Post the empty panel ───────────────────────────────────────────────
        panel: dict = {
            "title": title,
            "description": description,
            "color": panel_color,
            "channel_id": str(ctx.channel.id),
            "guild_id": str(ctx.guild.id),
            "roles": {},
        }
        panel_msg = await ctx.send(embed=build_panel_embed(panel, panel_color))

        data = load_data()
        guild_id = str(ctx.guild.id)
        if guild_id not in data:
            data[guild_id] = {}
        data[guild_id][str(panel_msg.id)] = panel
        save_data(data)

        # ── Step 4: collect emoji-role pairs ──────────────────────────────────
        await ctx.send(
            f"✅ **Panel posted!** (Message ID: `{panel_msg.id}`)\n\n"
            "Now add emoji → role pairs one at a time.\n"
            "Format: `<emoji> <@role>` — e.g. `🎮 @Gamer`\n"
            "Type **`done`** when finished, or **`cancel`** to stop without adding more."
        )

        added = 0
        while True:
            try:
                reply = await self.bot.wait_for("message", check=check, timeout=120.0)
            except asyncio.TimeoutError:
                await ctx.send(f"⏱️ Timed out. Panel is saved with {added} role(s). Use `!rr add` to add more.")
                break

            text = reply.content.strip()
            if text.lower() in ("done", "cancel", "stop", "quit", "finish"):
                break

            parts = text.split(maxsplit=1)
            if len(parts) < 2:
                await ctx.send("❌ Format: `<emoji> <@role>` — e.g. `🎮 @Gamer`. Try again or type `done`.")
                continue

            raw_emoji, raw_role = parts[0].strip(), parts[1].strip()

            # Resolve role — prefer mention, fall back to name search
            role: Optional[discord.Role] = None
            if reply.role_mentions:
                role = reply.role_mentions[0]
            else:
                role = discord.utils.find(
                    lambda r, q=raw_role.lower(): r.name.lower() == q,
                    ctx.guild.roles,
                )

            if not role:
                await ctx.send("❌ Couldn't find that role. Try `@mentioning` it directly.")
                continue
            if role >= ctx.guild.me.top_role:
                await ctx.send(f"❌ **{role.name}** is above my highest role — I can't assign it.")
                continue
            if role.managed:
                await ctx.send(f"❌ **{role.name}** is managed by an integration and can't be assigned.")
                continue
            if len(panel["roles"]) >= 20:
                await ctx.send("❌ Maximum of 20 emoji-role pairs per panel reached.")
                break
            if raw_emoji in panel["roles"]:
                await ctx.send(f"❌ {raw_emoji} is already mapped on this panel.")
                continue

            # Store mapping, update embed, add reaction
            panel["roles"][raw_emoji] = str(role.id)
            save_data(data)

            try:
                await panel_msg.edit(embed=build_panel_embed(panel, panel_color))
                await panel_msg.add_reaction(raw_emoji)
                added += 1
                await reply.add_reaction("✅")
            except discord.HTTPException as e:
                panel["roles"].pop(raw_emoji, None)
                save_data(data)
                await ctx.send(f"❌ Failed to add that emoji — is it valid? (`{e}`)")

        await ctx.send(
            f"🎉 **Done!** Panel **{title}** is live with **{added}** role(s).\n"
            f"Message ID: `{panel_msg.id}`\n"
            f"Use `!rr add {panel_msg.id} <emoji> <@role>` to add more roles anytime."
        )

    @prefix_rr.command(name="add")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True, add_reactions=True)
    async def prefix_rr_add(
        self,
        ctx: commands.Context,
        message_id: str,
        emoji: str,
        role: discord.Role,
    ):
        """Add an emoji → role mapping to an existing panel."""
        guild_id = str(ctx.guild.id)
        data = load_data()

        if guild_id not in data or message_id not in data[guild_id]:
            await ctx.send("❌ No reaction role panel found with that message ID.")
            return

        panel = data[guild_id][message_id]

        if role >= ctx.guild.me.top_role:
            await ctx.send(f"❌ **{role.name}** is above my highest role — I can't assign it.")
            return
        if role.managed:
            await ctx.send(f"❌ **{role.name}** is managed by an integration.")
            return
        if len(panel["roles"]) >= 20:
            await ctx.send("❌ Maximum of 20 emoji-role pairs per panel.")
            return
        if emoji in panel["roles"]:
            await ctx.send(f"❌ {emoji} is already mapped on this panel. Remove it first.")
            return

        panel["roles"][emoji] = str(role.id)
        save_data(data)

        channel = ctx.guild.get_channel(int(panel["channel_id"]))
        if channel:
            try:
                msg = await channel.fetch_message(int(message_id))
                await msg.edit(embed=build_panel_embed(panel, panel["color"]))
                await msg.add_reaction(emoji)
            except (discord.NotFound, discord.HTTPException) as e:
                logger.warning(f"prefix rr add: could not update panel: {e}")

        await ctx.send(f"✅ Added {emoji} → **{role.name}** to panel `{message_id}`.")

    @prefix_rr.command(name="remove")
    @commands.has_permissions(manage_roles=True)
    async def prefix_rr_remove(self, ctx: commands.Context, message_id: str, emoji: str):
        """Remove an emoji → role mapping from a panel."""
        guild_id = str(ctx.guild.id)
        data = load_data()

        if guild_id not in data or message_id not in data[guild_id]:
            await ctx.send("❌ Panel not found.")
            return

        panel = data[guild_id][message_id]
        if emoji not in panel["roles"]:
            await ctx.send(f"❌ {emoji} is not mapped on this panel.")
            return

        role_id = panel["roles"].pop(emoji)
        save_data(data)

        channel = ctx.guild.get_channel(int(panel["channel_id"]))
        if channel:
            try:
                msg = await channel.fetch_message(int(message_id))
                await msg.edit(embed=build_panel_embed(panel, panel["color"]))
                await msg.clear_reaction(emoji)
            except (discord.NotFound, discord.HTTPException) as e:
                logger.warning(f"prefix rr remove: could not update panel: {e}")

        await ctx.send(f"✅ Removed {emoji} (was <@&{role_id}>) from panel `{message_id}`.")

    @prefix_rr.command(name="list")
    @commands.has_permissions(manage_roles=True)
    async def prefix_rr_list(self, ctx: commands.Context):
        """List all reaction role panels in this server."""
        guild_id = str(ctx.guild.id)
        data = load_data()
        panels = data.get(guild_id, {})

        if not panels:
            await ctx.send("❌ No reaction role panels in this server. Use `!rr create` to make one.")
            return

        embed = discord.Embed(title="📋 Reaction Role Panels", color=0x4488FF)
        for msg_id, panel in panels.items():
            channel = ctx.guild.get_channel(int(panel["channel_id"]))
            ch_mention = channel.mention if channel else f"<#{panel['channel_id']}>"
            roles_text = (
                "\n".join(f"{e} → <@&{r}>" for e, r in panel["roles"].items())
                or "*No roles added yet*"
            )
            embed.add_field(
                name=f"📌 {panel['title']} (ID: `{msg_id}`)",
                value=f"**Channel:** {ch_mention}\n{roles_text}",
                inline=False,
            )
        embed.set_footer(text=f"{len(panels)} panel(s) total")
        await ctx.send(embed=embed)

    @prefix_rr.command(name="delete")
    @commands.has_permissions(manage_roles=True)
    async def prefix_rr_delete(self, ctx: commands.Context, message_id: str):
        """Delete a reaction role panel and its Discord message."""
        guild_id = str(ctx.guild.id)
        data = load_data()

        if guild_id not in data or message_id not in data[guild_id]:
            await ctx.send("❌ Panel not found.")
            return

        panel = data[guild_id].pop(message_id)
        save_data(data)

        channel = ctx.guild.get_channel(int(panel["channel_id"]))
        if channel:
            try:
                msg = await channel.fetch_message(int(message_id))
                await msg.delete()
            except (discord.NotFound, discord.HTTPException):
                pass

        await ctx.send(f"✅ Deleted panel **{panel['title']}** (`{message_id}`).")

    @prefix_rr.error
    @prefix_rr_create.error
    @prefix_rr_add.error
    @prefix_rr_remove.error
    @prefix_rr_list.error
    @prefix_rr_delete.error
    async def prefix_rr_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need **Manage Roles** permission to use reaction role commands.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I need **Manage Roles** and **Add Reactions** permissions to do that.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"❌ Invalid argument: {error}")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"❌ Missing argument: `{error.param.name}`\n"
                "Run `!rr` to see usage for each subcommand."
            )
        else:
            logger.error(f"Unexpected prefix_rr error: {error}")


async def setup(bot: commands.Bot):
    await bot.add_cog(ReactionRolesCog(bot))
