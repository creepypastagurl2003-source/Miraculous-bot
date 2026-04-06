import discord
from discord import app_commands
from discord.ext import commands, tasks
import aiohttp
import os
import json
import logging
import re
from typing import Optional

logger = logging.getLogger("bot.notifications")

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "notifications.json")

YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
TWITCH_CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID", "")
TWITCH_CLIENT_SECRET = os.environ.get("TWITCH_CLIENT_SECRET", "")

YT_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"
YT_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
TWITCH_STREAMS_URL = "https://api.twitch.tv/helix/streams"
TWITCH_USERS_URL = "https://api.twitch.tv/helix/users"

DEFAULT_YT_MSG = "📢 **{channel}** just uploaded a new video!\n🎬 **{title}**\n🔗 {link}"
DEFAULT_TW_MSG = "🔴 **{streamer}** is now **LIVE** on Twitch!\n🎮 Playing: **{game}**\n👀 {viewers} viewers\n🔗 {link}"


# ─── helpers ───────────────────────────────────────────────────────────────────

def load_data() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"youtube": [], "twitch": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def parse_youtube_input(raw: str) -> str:
    """Return a channel handle/ID/username from a URL or plain string."""
    raw = raw.strip()
    # Full URL with channel ID
    m = re.search(r"youtube\.com/channel/([A-Za-z0-9_-]+)", raw)
    if m:
        return m.group(1)
    # Handle URL  (@name)
    m = re.search(r"youtube\.com/@([A-Za-z0-9_.-]+)", raw)
    if m:
        return "@" + m.group(1)
    # /c/ or /user/ URL
    m = re.search(r"youtube\.com/(?:c|user)/([A-Za-z0-9_.-]+)", raw)
    if m:
        return m.group(1)
    # Bare @handle
    if raw.startswith("@"):
        return raw
    return raw


def parse_twitch_input(raw: str) -> str:
    """Return just the Twitch username from a URL or plain string."""
    raw = raw.strip().rstrip("/")
    m = re.search(r"twitch\.tv/([A-Za-z0-9_]+)$", raw)
    if m:
        return m.group(1).lower()
    return raw.lower()


# ─── YouTube API helpers ────────────────────────────────────────────────────────

async def resolve_youtube_channel(session: aiohttp.ClientSession, query: str) -> Optional[dict]:
    """Resolve a channel query to {id, title}. Returns None on failure."""
    if not YOUTUBE_API_KEY:
        return None

    # Already a UC channel ID
    if re.match(r"^UC[A-Za-z0-9_-]{22}$", query):
        params = {"part": "snippet", "id": query, "key": YOUTUBE_API_KEY}
        async with session.get(YT_CHANNEL_URL, params=params) as r:
            data = await r.json()
            items = data.get("items", [])
            if items:
                return {"id": query, "title": items[0]["snippet"]["title"]}
        return None

    # Handle (@name)
    if query.startswith("@"):
        params = {"part": "snippet", "forHandle": query.lstrip("@"), "key": YOUTUBE_API_KEY}
        async with session.get(YT_CHANNEL_URL, params=params) as r:
            data = await r.json()
            items = data.get("items", [])
            if items:
                return {"id": items[0]["id"], "title": items[0]["snippet"]["title"]}

    # Legacy username
    params = {"part": "snippet", "forUsername": query, "key": YOUTUBE_API_KEY}
    async with session.get(YT_CHANNEL_URL, params=params) as r:
        data = await r.json()
        items = data.get("items", [])
        if items:
            return {"id": items[0]["id"], "title": items[0]["snippet"]["title"]}

    return None


async def fetch_latest_video(session: aiohttp.ClientSession, channel_id: str) -> Optional[dict]:
    """Fetch the most recent video from a channel. Returns {id, title, link} or None."""
    if not YOUTUBE_API_KEY:
        return None
    params = {
        "part": "snippet",
        "channelId": channel_id,
        "order": "date",
        "maxResults": 1,
        "type": "video",
        "key": YOUTUBE_API_KEY,
    }
    async with session.get(YT_SEARCH_URL, params=params) as r:
        if r.status != 200:
            return None
        data = await r.json()
        items = data.get("items", [])
        if not items:
            return None
        vid = items[0]
        vid_id = vid["id"].get("videoId")
        if not vid_id:
            return None
        return {
            "id": vid_id,
            "title": vid["snippet"]["title"],
            "link": f"https://www.youtube.com/watch?v={vid_id}",
            "channel": vid["snippet"]["channelTitle"],
        }


# ─── Twitch API helpers ─────────────────────────────────────────────────────────

_twitch_token: Optional[str] = None


async def get_twitch_token(session: aiohttp.ClientSession) -> Optional[str]:
    global _twitch_token
    if _twitch_token:
        return _twitch_token
    if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
        return None
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials",
    }
    async with session.post(TWITCH_TOKEN_URL, params=params) as r:
        if r.status != 200:
            return None
        data = await r.json()
        _twitch_token = data.get("access_token")
        return _twitch_token


async def fetch_twitch_stream(session: aiohttp.ClientSession, username: str) -> Optional[dict]:
    """Returns stream info dict if live, None if offline."""
    token = await get_twitch_token(session)
    if not token:
        return None
    headers = {"Client-ID": TWITCH_CLIENT_ID, "Authorization": f"Bearer {token}"}
    async with session.get(TWITCH_STREAMS_URL, params={"user_login": username}, headers=headers) as r:
        if r.status == 401:
            global _twitch_token
            _twitch_token = None
            return None
        if r.status != 200:
            return None
        data = await r.json()
        items = data.get("data", [])
        if not items:
            return None
        s = items[0]
        return {
            "streamer": s["user_name"],
            "title": s["title"],
            "game": s.get("game_name", "Unknown"),
            "viewers": s.get("viewer_count", 0),
            "link": f"https://twitch.tv/{username}",
            "thumbnail": s.get("thumbnail_url", "").replace("{width}", "320").replace("{height}", "180"),
        }


async def resolve_twitch_user(session: aiohttp.ClientSession, username: str) -> Optional[str]:
    """Validate the Twitch username exists; return display name or None."""
    token = await get_twitch_token(session)
    if not token:
        return None
    headers = {"Client-ID": TWITCH_CLIENT_ID, "Authorization": f"Bearer {token}"}
    async with session.get(TWITCH_USERS_URL, params={"login": username}, headers=headers) as r:
        if r.status != 200:
            return None
        data = await r.json()
        items = data.get("data", [])
        return items[0]["display_name"] if items else None


# ─── Cog ────────────────────────────────────────────────────────────────────────

class NotificationsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session: Optional[aiohttp.ClientSession] = None
        self.youtube_poll.start()
        self.twitch_poll.start()

    def cog_unload(self):
        self.youtube_poll.cancel()
        self.twitch_poll.cancel()
        if self.session and not self.session.closed:
            self.bot.loop.create_task(self.session.close())

    async def get_session(self) -> aiohttp.ClientSession:
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    # ── YouTube group ──────────────────────────────────────────────────────────

    yt_group = app_commands.Group(name="youtube_notify", description="YouTube upload notifications")

    @yt_group.command(name="add", description="Get notified when a YouTube channel uploads a new video.")
    @app_commands.describe(
        youtube_channel="YouTube channel name, @handle, or full URL",
        discord_channel="Discord channel to send notifications in",
        message="Custom message format (use {channel}, {title}, {link})",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def yt_add(
        self,
        interaction: discord.Interaction,
        youtube_channel: str,
        discord_channel: discord.TextChannel,
        message: Optional[str] = None,
    ):
        await interaction.response.defer(ephemeral=True)

        if not YOUTUBE_API_KEY:
            await interaction.followup.send(
                "⚠️ **YouTube API key not configured.**\n"
                "Please add `YOUTUBE_API_KEY` to your Replit secrets, then use this command again.\n"
                "Get a free key at: <https://console.cloud.google.com/> → YouTube Data API v3",
                ephemeral=True,
            )
            return

        query = parse_youtube_input(youtube_channel)
        session = await self.get_session()

        channel_info = await resolve_youtube_channel(session, query)
        if not channel_info:
            await interaction.followup.send(
                f"❌ Could not find a YouTube channel matching **{youtube_channel}**.\n"
                "Try the full channel URL or @handle.",
                ephemeral=True,
            )
            return

        data = load_data()
        guild_id = str(interaction.guild_id)

        # Prevent duplicate subscriptions
        for sub in data["youtube"]:
            if sub["guild_id"] == guild_id and sub["youtube_channel_id"] == channel_info["id"]:
                await interaction.followup.send(
                    f"❌ Already subscribed to **{channel_info['title']}** in this server.", ephemeral=True
                )
                return

        # Fetch current latest video so we don't re-announce old videos on first run
        latest = await fetch_latest_video(session, channel_info["id"])

        data["youtube"].append({
            "guild_id": guild_id,
            "discord_channel_id": str(discord_channel.id),
            "youtube_channel_id": channel_info["id"],
            "youtube_channel_name": channel_info["title"],
            "message_format": message or DEFAULT_YT_MSG,
            "last_video_id": latest["id"] if latest else None,
        })
        save_data(data)

        embed = discord.Embed(
            title="✅ YouTube Notifications Set Up!",
            color=0xFF0000,
        )
        embed.add_field(name="📺 YouTube Channel", value=channel_info["title"], inline=True)
        embed.add_field(name="📢 Discord Channel", value=discord_channel.mention, inline=True)
        embed.add_field(
            name="💬 Message Format",
            value=f"```{message or DEFAULT_YT_MSG}```",
            inline=False,
        )
        embed.set_footer(text="The bot checks for new uploads every 10 minutes.")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @yt_group.command(name="remove", description="Remove a YouTube notification subscription.")
    @app_commands.describe(youtube_channel="The YouTube channel name or @handle to remove")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def yt_remove(self, interaction: discord.Interaction, youtube_channel: str):
        await interaction.response.defer(ephemeral=True)
        data = load_data()
        guild_id = str(interaction.guild_id)
        q = youtube_channel.lower()
        before = len(data["youtube"])
        data["youtube"] = [
            s for s in data["youtube"]
            if not (
                s["guild_id"] == guild_id
                and (q in s["youtube_channel_name"].lower() or q in s["youtube_channel_id"].lower())
            )
        ]
        if len(data["youtube"]) == before:
            await interaction.followup.send(
                f"❌ No YouTube subscription found for **{youtube_channel}**.", ephemeral=True
            )
            return
        save_data(data)
        await interaction.followup.send(
            f"✅ Removed YouTube notifications for **{youtube_channel}**.", ephemeral=True
        )

    @yt_group.command(name="list", description="List all YouTube notification subscriptions in this server.")
    async def yt_list(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        data = load_data()
        guild_id = str(interaction.guild_id)
        subs = [s for s in data["youtube"] if s["guild_id"] == guild_id]
        if not subs:
            await interaction.followup.send(
                "📋 No YouTube subscriptions set up. Use `/youtube_notify add` to get started.",
                ephemeral=True,
            )
            return
        embed = discord.Embed(title="📺 YouTube Notification Subscriptions", color=0xFF0000)
        for s in subs:
            embed.add_field(
                name=f"📺 {s['youtube_channel_name']}",
                value=f"**Channel:** <#{s['discord_channel_id']}>\n**Last video:** `{s['last_video_id'] or 'N/A'}`",
                inline=False,
            )
        embed.set_footer(text=f"{len(subs)} subscription(s)")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @yt_group.command(name="test", description="Immediately send a test notification for a YouTube subscription.")
    @app_commands.describe(youtube_channel="The subscribed YouTube channel to test (leave blank to test the first one)")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def yt_test(self, interaction: discord.Interaction, youtube_channel: Optional[str] = None):
        await interaction.response.defer(ephemeral=True)

        if not YOUTUBE_API_KEY:
            await interaction.followup.send(
                "❌ **YouTube API key not configured.**\n"
                "Add `YOUTUBE_API_KEY` to your Replit secrets to enable this.",
                ephemeral=True,
            )
            return

        data = load_data()
        guild_id = str(interaction.guild_id)
        subs = [s for s in data["youtube"] if s["guild_id"] == guild_id]

        if not subs:
            await interaction.followup.send(
                "❌ No YouTube subscriptions in this server.\nUse `/youtube_notify add` to set one up first.",
                ephemeral=True,
            )
            return

        sub = None
        if youtube_channel:
            q = youtube_channel.lower()
            sub = next(
                (s for s in subs if q in s["youtube_channel_name"].lower() or q in s["youtube_channel_id"].lower()),
                None,
            )
            if not sub:
                names = ", ".join(f"`{s['youtube_channel_name']}`" for s in subs)
                await interaction.followup.send(
                    f"❌ No subscription found matching **{youtube_channel}**.\nSubscribed channels: {names}",
                    ephemeral=True,
                )
                return
        else:
            sub = subs[0]

        target_channel = interaction.guild.get_channel(int(sub["discord_channel_id"]))
        if not target_channel:
            await interaction.followup.send(
                "❌ The configured Discord channel no longer exists.\nPlease re-add the subscription with a valid channel.",
                ephemeral=True,
            )
            return

        try:
            session = await self.get_session()
            latest = await fetch_latest_video(session, sub["youtube_channel_id"])
        except Exception as e:
            logger.error(f"yt_test: API error for channel {sub['youtube_channel_id']}: {e}")
            await interaction.followup.send(
                "❌ A network error occurred while contacting the YouTube API.\nPlease try again in a moment.",
                ephemeral=True,
            )
            return

        if not latest:
            await interaction.followup.send(
                f"❌ Could not fetch videos from **{sub['youtube_channel_name']}**.\n"
                "Make sure the YouTube Data API v3 is enabled on your API key and the channel is correct.",
                ephemeral=True,
            )
            return

        # Build the rich notification embed posted to the channel
        thumbnail_url = f"https://img.youtube.com/vi/{latest['id']}/hqdefault.jpg"
        msg = sub["message_format"].format(
            channel=latest["channel"],
            title=latest["title"],
            link=latest["link"],
            url=latest["link"],
        )
        notify_embed = discord.Embed(
            title=latest["title"],
            url=latest["link"],
            description=msg,
            color=0xFF0000,
        )
        notify_embed.set_author(
            name=f"📺 {latest['channel']}",
            url=f"https://www.youtube.com/channel/{sub['youtube_channel_id']}",
            icon_url="https://www.youtube.com/s/desktop/5b3b4b5b/img/favicon_144x144.png",
        )
        notify_embed.set_image(url=thumbnail_url)
        notify_embed.set_footer(text="YouTube • New Upload  |  ⚙️ Test Notification")

        try:
            await target_channel.send(embed=notify_embed)
        except discord.Forbidden:
            await interaction.followup.send(
                f"❌ I don't have permission to send messages in {target_channel.mention}.",
                ephemeral=True,
            )
            return
        except Exception as e:
            logger.error(f"yt_test: failed to send to channel: {e}")
            await interaction.followup.send(
                "❌ Failed to send the test notification to the channel.",
                ephemeral=True,
            )
            return

        # Private confirmation embed back to the admin
        confirm_embed = discord.Embed(
            title="✅ YouTube Test Sent",
            color=0x44CC88,
        )
        confirm_embed.add_field(name="📺 Channel", value=sub["youtube_channel_name"], inline=True)
        confirm_embed.add_field(name="📢 Posted In", value=target_channel.mention, inline=True)
        confirm_embed.add_field(name="🎬 Latest Video", value=f"[{latest['title']}]({latest['link']})", inline=False)
        confirm_embed.add_field(
            name="⏱️ Auto-check",
            value="The bot polls this channel every **10 minutes** for new uploads.",
            inline=False,
        )
        confirm_embed.set_image(url=thumbnail_url)
        await interaction.followup.send(embed=confirm_embed, ephemeral=True)

    # ── Twitch group ───────────────────────────────────────────────────────────

    tw_group = app_commands.Group(name="twitch_notify", description="Twitch live stream notifications")

    @tw_group.command(name="add", description="Get notified when a Twitch streamer goes live.")
    @app_commands.describe(
        twitch_user="Twitch username or full Twitch URL",
        discord_channel="Discord channel to send live alerts in",
        message="Custom message format (use {streamer}, {game}, {viewers}, {link})",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def tw_add(
        self,
        interaction: discord.Interaction,
        twitch_user: str,
        discord_channel: discord.TextChannel,
        message: Optional[str] = None,
    ):
        await interaction.response.defer(ephemeral=True)

        if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
            await interaction.followup.send(
                "⚠️ **Twitch API credentials not configured.**\n"
                "Please add `TWITCH_CLIENT_ID` and `TWITCH_CLIENT_SECRET` to your Replit secrets.\n"
                "Register a free app at: <https://dev.twitch.tv/console>",
                ephemeral=True,
            )
            return

        username = parse_twitch_input(twitch_user)
        session = await self.get_session()
        display_name = await resolve_twitch_user(session, username)

        if not display_name:
            await interaction.followup.send(
                f"❌ Could not find Twitch user **{twitch_user}**. Check the username and try again.",
                ephemeral=True,
            )
            return

        data = load_data()
        guild_id = str(interaction.guild_id)

        for sub in data["twitch"]:
            if sub["guild_id"] == guild_id and sub["twitch_username"] == username:
                await interaction.followup.send(
                    f"❌ Already tracking **{display_name}** in this server.", ephemeral=True
                )
                return

        # Check if currently live so we don't fire an alert immediately
        stream = await fetch_twitch_stream(session, username)

        data["twitch"].append({
            "guild_id": guild_id,
            "discord_channel_id": str(discord_channel.id),
            "twitch_username": username,
            "twitch_display_name": display_name,
            "message_format": message or DEFAULT_TW_MSG,
            "is_live": stream is not None,
        })
        save_data(data)

        embed = discord.Embed(title="✅ Twitch Notifications Set Up!", color=0x9146FF)
        embed.add_field(name="🎮 Twitch User", value=display_name, inline=True)
        embed.add_field(name="📢 Discord Channel", value=discord_channel.mention, inline=True)
        embed.add_field(
            name="💬 Message Format",
            value=f"```{message or DEFAULT_TW_MSG}```",
            inline=False,
        )
        if stream:
            embed.add_field(
                name="📡 Current Status",
                value=f"🔴 **Currently LIVE** — Playing {stream['game']} with {stream['viewers']:,} viewers",
                inline=False,
            )
        embed.set_footer(text="The bot checks for live status every 2 minutes.")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @tw_group.command(name="remove", description="Remove a Twitch notification subscription.")
    @app_commands.describe(twitch_user="The Twitch username to remove")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def tw_remove(self, interaction: discord.Interaction, twitch_user: str):
        await interaction.response.defer(ephemeral=True)
        username = parse_twitch_input(twitch_user)
        data = load_data()
        guild_id = str(interaction.guild_id)
        before = len(data["twitch"])
        data["twitch"] = [
            s for s in data["twitch"]
            if not (s["guild_id"] == guild_id and s["twitch_username"] == username)
        ]
        if len(data["twitch"]) == before:
            await interaction.followup.send(
                f"❌ No Twitch subscription found for **{twitch_user}**.", ephemeral=True
            )
            return
        save_data(data)
        await interaction.followup.send(
            f"✅ Removed Twitch notifications for **{twitch_user}**.", ephemeral=True
        )

    @tw_group.command(name="list", description="List all Twitch notification subscriptions in this server.")
    async def tw_list(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        data = load_data()
        guild_id = str(interaction.guild_id)
        subs = [s for s in data["twitch"] if s["guild_id"] == guild_id]
        if not subs:
            await interaction.followup.send(
                "📋 No Twitch subscriptions set up. Use `/twitch_notify add` to get started.",
                ephemeral=True,
            )
            return
        embed = discord.Embed(title="🎮 Twitch Notification Subscriptions", color=0x9146FF)
        for s in subs:
            status = "🔴 LIVE" if s.get("is_live") else "⚫ Offline"
            embed.add_field(
                name=f"🎮 {s['twitch_display_name']} — {status}",
                value=f"**Channel:** <#{s['discord_channel_id']}>",
                inline=False,
            )
        embed.set_footer(text=f"{len(subs)} subscription(s)")
        await interaction.followup.send(embed=embed, ephemeral=True)

    @tw_group.command(name="test", description="Immediately send a test Twitch notification for a subscription.")
    @app_commands.describe(twitch_user="The subscribed Twitch username to test (leave blank to test the first one)")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def tw_test(self, interaction: discord.Interaction, twitch_user: Optional[str] = None):
        await interaction.response.defer(ephemeral=True)

        if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
            await interaction.followup.send(
                "❌ **Twitch API credentials not configured.**\n"
                "Add `TWITCH_CLIENT_ID` and `TWITCH_CLIENT_SECRET` to your Replit secrets to enable this.",
                ephemeral=True,
            )
            return

        data = load_data()
        guild_id = str(interaction.guild_id)
        subs = [s for s in data["twitch"] if s["guild_id"] == guild_id]

        if not subs:
            await interaction.followup.send(
                "❌ No Twitch subscriptions in this server.\nUse `/twitch_notify add` to set one up first.",
                ephemeral=True,
            )
            return

        sub = None
        if twitch_user:
            q = parse_twitch_input(twitch_user)
            sub = next((s for s in subs if s["twitch_username"] == q), None)
            if not sub:
                names = ", ".join(f"`{s['twitch_display_name']}`" for s in subs)
                await interaction.followup.send(
                    f"❌ No subscription found for **{twitch_user}**.\nSubscribed streamers: {names}",
                    ephemeral=True,
                )
                return
        else:
            sub = subs[0]

        target_channel = interaction.guild.get_channel(int(sub["discord_channel_id"]))
        if not target_channel:
            await interaction.followup.send(
                "❌ The configured Discord channel no longer exists.\nPlease re-add the subscription with a valid channel.",
                ephemeral=True,
            )
            return

        try:
            session = await self.get_session()
            stream = await fetch_twitch_stream(session, sub["twitch_username"])
        except Exception as e:
            logger.error(f"tw_test: API error for {sub['twitch_username']}: {e}")
            await interaction.followup.send(
                "❌ A network error occurred while contacting the Twitch API.\nPlease try again in a moment.",
                ephemeral=True,
            )
            return

        is_live = stream is not None

        # Use real data when live, clean placeholder when offline
        info = stream if is_live else {
            "streamer": sub["twitch_display_name"],
            "title": "Test Stream Title",
            "game": "Just Chatting",
            "viewers": 0,
            "link": f"https://twitch.tv/{sub['twitch_username']}",
            "thumbnail": "",
        }

        msg = sub["message_format"].format(
            streamer=info["streamer"],
            game=info["game"],
            viewers=f"{info['viewers']:,}",
            link=info["link"],
            title=info["title"],
            channel=info["streamer"],
            url=info["link"],
        )

        # Build the rich notification embed posted to the channel
        notify_embed = discord.Embed(
            title=f"🔴 {info['streamer']} is now LIVE!",
            url=info["link"],
            description=msg,
            color=0x9146FF,
        )
        notify_embed.add_field(name="🎮 Game", value=info["game"], inline=True)
        if is_live:
            notify_embed.add_field(name="👀 Viewers", value=f"{info['viewers']:,}", inline=True)
        notify_embed.add_field(
            name="📺 Stream Title",
            value=info["title"],
            inline=False,
        )
        if info.get("thumbnail"):
            # Replace dimensions in thumbnail URL for a clean image
            thumb = info["thumbnail"].replace("{width}", "1280").replace("{height}", "720")
            notify_embed.set_image(url=thumb)
        notify_embed.set_author(
            name=info["streamer"],
            url=info["link"],
            icon_url="https://static.twitchcdn.net/assets/favicon-32-e29e246c157142c1.png",
        )
        footer_note = "Twitch • Live Alert" if is_live else "Twitch • Live Alert  |  ⚙️ Simulated (streamer is offline)"
        notify_embed.set_footer(text=footer_note)

        try:
            await target_channel.send(embed=notify_embed)
        except discord.Forbidden:
            await interaction.followup.send(
                f"❌ I don't have permission to send messages in {target_channel.mention}.",
                ephemeral=True,
            )
            return
        except Exception as e:
            logger.error(f"tw_test: failed to send to channel: {e}")
            await interaction.followup.send(
                "❌ Failed to send the test notification to the channel.",
                ephemeral=True,
            )
            return

        # Private confirmation embed back to the admin
        status_label = "🔴 **Live** — used real stream data" if is_live else "⚫ **Offline** — sent a simulated notification"
        confirm_embed = discord.Embed(
            title="✅ Twitch Test Sent",
            color=0x9146FF,
        )
        confirm_embed.add_field(name="🎮 Streamer", value=sub["twitch_display_name"], inline=True)
        confirm_embed.add_field(name="📢 Posted In", value=target_channel.mention, inline=True)
        confirm_embed.add_field(name="📡 Current Status", value=status_label, inline=False)
        confirm_embed.add_field(
            name="⏱️ Auto-check",
            value="The bot polls this streamer every **2 minutes** while they're live.",
            inline=False,
        )
        await interaction.followup.send(embed=confirm_embed, ephemeral=True)

    # ── Background polling tasks ────────────────────────────────────────────────

    @tasks.loop(minutes=10)
    async def youtube_poll(self):
        if not YOUTUBE_API_KEY:
            return
        data = load_data()
        if not data["youtube"]:
            return

        session = await self.get_session()
        changed = False

        for sub in data["youtube"]:
            try:
                latest = await fetch_latest_video(session, sub["youtube_channel_id"])
                if not latest:
                    continue
                if latest["id"] == sub.get("last_video_id"):
                    continue

                # New video found
                sub["last_video_id"] = latest["id"]
                changed = True

                guild = self.bot.get_guild(int(sub["guild_id"]))
                if not guild:
                    continue
                channel = guild.get_channel(int(sub["discord_channel_id"]))
                if not channel:
                    continue

                msg = sub["message_format"].format(
                    channel=latest["channel"],
                    title=latest["title"],
                    link=latest["link"],
                    url=latest["link"],
                )

                embed = discord.Embed(
                    title=f"🎬 {latest['title']}",
                    url=latest["link"],
                    description=msg,
                    color=0xFF0000,
                )
                embed.set_author(name=latest["channel"])
                embed.set_footer(text="YouTube • New Upload")

                await channel.send(embed=embed)
                logger.info(f"YouTube: sent notification for '{latest['title']}' in {guild.name}")

            except Exception as e:
                logger.error(f"YouTube poll error for {sub.get('youtube_channel_name')}: {e}")

        if changed:
            save_data(data)

    @tasks.loop(minutes=2)
    async def twitch_poll(self):
        if not TWITCH_CLIENT_ID or not TWITCH_CLIENT_SECRET:
            return
        data = load_data()
        if not data["twitch"]:
            return

        session = await self.get_session()
        changed = False

        for sub in data["twitch"]:
            try:
                stream = await fetch_twitch_stream(session, sub["twitch_username"])
                was_live = sub.get("is_live", False)
                is_live = stream is not None

                if is_live and not was_live:
                    # Just went live — send notification
                    sub["is_live"] = True
                    changed = True

                    guild = self.bot.get_guild(int(sub["guild_id"]))
                    if not guild:
                        continue
                    channel = guild.get_channel(int(sub["discord_channel_id"]))
                    if not channel:
                        continue

                    msg = sub["message_format"].format(
                        streamer=stream["streamer"],
                        game=stream["game"],
                        viewers=f"{stream['viewers']:,}",
                        link=stream["link"],
                        title=stream["title"],
                        channel=stream["streamer"],
                        url=stream["link"],
                    )

                    embed = discord.Embed(
                        title=f"🔴 {stream['streamer']} is now LIVE!",
                        url=stream["link"],
                        description=msg,
                        color=0x9146FF,
                    )
                    embed.add_field(name="🎮 Game", value=stream["game"], inline=True)
                    embed.add_field(name="👀 Viewers", value=f"{stream['viewers']:,}", inline=True)
                    if stream.get("thumbnail"):
                        embed.set_image(url=stream["thumbnail"])
                    embed.set_footer(text="Twitch • Stream Alert")

                    await channel.send(embed=embed)
                    logger.info(f"Twitch: sent live alert for {stream['streamer']} in {guild.name}")

                elif not is_live and was_live:
                    # Stream ended
                    sub["is_live"] = False
                    changed = True
                    logger.info(f"Twitch: {sub['twitch_username']} went offline")

            except Exception as e:
                logger.error(f"Twitch poll error for {sub.get('twitch_username')}: {e}")

        if changed:
            save_data(data)

    @youtube_poll.before_loop
    @twitch_poll.before_loop
    async def before_polls(self):
        await self.bot.wait_until_ready()

    # ── Error handlers ─────────────────────────────────────────────────────────

    @yt_add.error
    @yt_remove.error
    @yt_list.error
    @yt_test.error
    @tw_add.error
    @tw_remove.error
    @tw_list.error
    @tw_test.error
    async def admin_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        # Unwrap CommandInvokeError to get the real exception
        cause = getattr(error, "original", error)
        if isinstance(error, app_commands.MissingPermissions):
            msg = "❌ You need the **Manage Server** permission to manage notification subscriptions."
        else:
            logger.error(f"Notification command error: {cause}", exc_info=cause)
            msg = "❌ An unexpected error occurred. Please try again."

        # Permission errors fire before defer(); all others fire after.
        # Use the right response method depending on whether we already deferred.
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(NotificationsCog(bot))
