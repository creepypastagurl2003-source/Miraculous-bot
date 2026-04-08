import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("bot")

TOKEN = os.environ.get("MIRACULOUS_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("MIRACULOUS_BOT_TOKEN environment variable is not set.")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


def _local_signature() -> dict:
    """
    Build a map of {command_name: sorted list of subcommand names} for
    every top-level command the bot currently has loaded.
    This lets us detect both new top-level commands AND new subcommands
    inside existing groups without syncing on every restart.
    """
    sig = {}
    for cmd in bot.tree.get_commands():
        if hasattr(cmd, "commands"):
            sig[cmd.name] = sorted(sub.name for sub in cmd.commands)
        else:
            sig[cmd.name] = []
    return sig


async def smart_sync():
    """
    Only sync commands to Discord when the local command tree (including
    subcommands) differs from what is registered.  This avoids burning
    through the 200-command-create-per-day quota on every restart.
    """
    local_sig = _local_signature()
    local_names = set(local_sig.keys())

    for guild in bot.guilds:
        try:
            registered = await bot.tree.fetch_commands(guild=guild)
            registered_sig = {}
            for cmd in registered:
                # AppCommand objects expose .options for subcommands
                subs = [
                    o.name for o in getattr(cmd, "options", [])
                    if hasattr(o, "options")  # subcommand groups / commands
                ]
                registered_sig[cmd.name] = sorted(subs)

            registered_names = set(registered_sig.keys())

            added = local_names - registered_names
            removed = registered_names - local_names
            changed = {
                name for name in local_names & registered_names
                if local_sig[name] != registered_sig.get(name, [])
            }

            if not added and not removed and not changed:
                logger.info(
                    f"Commands already up-to-date in guild '{guild.name}' "
                    f"({len(local_names)} commands) — skipping sync."
                )
                continue

            if added:
                logger.info(f"New commands in '{guild.name}': {added}")
            if removed:
                logger.info(f"Stale commands in '{guild.name}': {removed}")
            if changed:
                logger.info(f"Updated subcommands in '{guild.name}': {changed}")

            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            logger.info(f"Synced {len(synced)} commands to guild '{guild.name}'")

        except discord.HTTPException as e:
            if e.code == 30034:
                logger.warning(
                    "Daily command-create limit (200) reached. "
                    "Commands that were already registered will still work. "
                    "Newly added commands will become available after midnight UTC."
                )
            elif e.code == 50240:
                logger.warning(f"Entry Point restriction in '{guild.name}' — skipping.")
            else:
                logger.error(f"Sync failed for guild '{guild.name}': {e}")
        except Exception as e:
            logger.error(f"Unexpected sync error for guild '{guild.name}': {e}")


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await smart_sync()


@bot.command(name="sync", hidden=True)
@commands.is_owner()
async def force_sync(ctx):
    """Owner-only: force a full command sync regardless of diff."""
    await ctx.send("⏳ Force-syncing commands...")
    total = 0
    for guild in bot.guilds:
        try:
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            total += len(synced)
        except discord.HTTPException as e:
            if e.code == 30034:
                await ctx.send(
                    "⚠️ Hit Discord's daily command-create limit (200/day). "
                    "Try again after midnight UTC."
                )
                return
            await ctx.send(f"❌ Sync error: {e}")
            return
    await ctx.send(f"✅ Force-synced **{total}** command(s) across {len(bot.guilds)} guild(s).")


async def load_cogs():
    cogs = [
        "cogs.marriage",
        "cogs.shipping",
        "cogs.kwami",
        "cogs.quotes",
        "cogs.family",
        "cogs.mod",
        "cogs.games",
        "cogs.miraculous",
        "cogs.reaction_roles",
        "cogs.ai_chat",
        "cogs.economy",
        "cogs.collection",
        "cogs.profile",
        "cogs.fun",
        "cogs.help",
    ]
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            logger.info(f"Loaded cog: {cog}")
        except Exception as e:
            logger.error(f"Failed to load cog {cog}: {e}")


async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)


if __name__ == "__main__":
    import asyncio
    keep_alive()
    asyncio.run(main())
