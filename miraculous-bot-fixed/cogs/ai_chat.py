import discord
from discord import app_commands
from discord.ext import commands
from openai import AsyncOpenAI
import os
import logging
import json
from typing import Optional
from collections import defaultdict

logger = logging.getLogger("bot.ai_chat")

client = AsyncOpenAI(
    api_key=os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY", ""),
    base_url=os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL", "https://api.openai.com/v1"),
)

SYSTEM_PROMPT = """You are Miraculous Bot ✨, a friendly and enthusiastic Discord assistant themed around the animated series "Miraculous: Tales of Ladybug & Cat Noir".

Your personality:
- Warm, encouraging, and playful — like Marinette with a splash of Cat Noir's pun energy
- You love the Miraculous universe and casually reference it (Kwamis, Miraculouses, Paris, akumatizations, etc.)
- You occasionally drop light puns or Miraculous references (but don't overdo it)
- You genuinely help users with any question — not just Miraculous stuff
- You keep responses concise and conversational for Discord (avoid walls of text)
- You use emojis naturally but not excessively
- You are never mean, sarcastic, or dismissive

Guidelines:
- Keep responses under ~300 words unless the question genuinely requires more detail
- If someone asks about Miraculous Ladybug, you are an expert and enthusiastic
- If someone asks a general question, help them warmly and competently
- Never break character or claim to be a different AI
- If you don't know something, say so charmingly ("Even Tikki doesn't know everything! 🐞")
- You can see the Discord username of who is talking to you"""

MAX_HISTORY = 16
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "ai_chat.json")


def load_settings() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_settings(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def split_message(text: str, limit: int = 1900) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts = []
    while text:
        if len(text) <= limit:
            parts.append(text)
            break
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = text.rfind(" ", 0, limit)
        if split_at == -1:
            split_at = limit
        parts.append(text[:split_at].rstrip())
        text = text[split_at:].lstrip()
    return parts


class AIChatCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.histories: dict[str, list[dict]] = defaultdict(list)
        self.processing: set[int] = set()

    def _channel_key(self, guild_id: int | None, channel_id: int) -> str:
        return f"{guild_id or 'dm'}:{channel_id}"

    def _add_to_history(self, key: str, role: str, content: str):
        self.histories[key].append({"role": role, "content": content})
        if len(self.histories[key]) > MAX_HISTORY:
            self.histories[key] = self.histories[key][-MAX_HISTORY:]

    async def _generate_reply(
        self,
        channel_key: str,
        user_message: str,
        username: str,
        extra_context: str = "",
    ) -> str:
        user_content = f"[{username}]: {user_message}"
        if extra_context:
            user_content = f"{extra_context}\n{user_content}"

        self._add_to_history(channel_key, "user", user_content)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.histories[channel_key]

        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_completion_tokens=600,
            )
            reply = response.choices[0].message.content or "✨ (no response)"
            self._add_to_history(channel_key, "assistant", reply)
            return reply
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            self.histories[channel_key].pop()
            raise

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if message.channel.id in self.processing:
            return

        is_mentioned = self.bot.user in message.mentions
        settings = load_settings()
        guild_id = str(message.guild.id) if message.guild else None
        channel_id = str(message.channel.id)

        ai_channel = (
            guild_id
            and settings.get(guild_id, {}).get("ai_channel") == channel_id
        )

        if not is_mentioned and not ai_channel:
            return

        content = message.content
        for mention in message.mentions:
            content = content.replace(f"<@{mention.id}>", "").replace(f"<@!{mention.id}>", "")
        content = content.strip()

        if not content and not message.attachments:
            await message.reply(
                "You called? ✨ Ask me anything — Miraculous trivia, homework, life advice... I'm all ears! 🐞",
                mention_author=False,
            )
            return

        self.processing.add(message.channel.id)
        async with message.channel.typing():
            try:
                key = self._channel_key(
                    message.guild.id if message.guild else None,
                    message.channel.id,
                )
                reply = await self._generate_reply(
                    key,
                    content or "[sent an attachment]",
                    message.author.display_name,
                )
                parts = split_message(reply)
                first = True
                for part in parts:
                    if first:
                        await message.reply(part, mention_author=False)
                        first = False
                    else:
                        await message.channel.send(part)
            except Exception as e:
                logger.error(f"AI reply failed: {e}")
                await message.reply(
                    "🐛 Oh no! My Miraculous seems to be glitching... try again in a moment!",
                    mention_author=False,
                )
            finally:
                self.processing.discard(message.channel.id)

    ai_group = app_commands.Group(name="ai", description="AI chat commands")

    @ai_group.command(name="chat", description="Chat with Miraculous Bot AI!")
    @app_commands.describe(message="What do you want to ask or talk about?")
    async def chat(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer()
        key = self._channel_key(
            interaction.guild_id,
            interaction.channel_id,
        )
        try:
            reply = await self._generate_reply(key, message, interaction.user.display_name)
            parts = split_message(reply)
            embed = discord.Embed(
                description=parts[0],
                color=0xFF0090,
            )
            embed.set_author(
                name=f"{interaction.user.display_name} asked...",
                icon_url=interaction.user.display_avatar.url,
            )
            embed.set_footer(text="Miraculous Bot AI ✨ • Powered by Replit AI")
            await interaction.followup.send(embed=embed)
            for part in parts[1:]:
                await interaction.followup.send(part)
        except Exception as e:
            logger.error(f"AI chat command failed: {e}")
            await interaction.followup.send(
                "🐛 My Miraculous is on the fritz! Try again in a moment. ✨"
            )

    @ai_group.command(name="reset", description="Clear the AI conversation history for this channel.")
    async def reset(self, interaction: discord.Interaction):
        await interaction.response.defer()
        key = self._channel_key(interaction.guild_id, interaction.channel_id)
        self.histories[key] = []
        await interaction.followup.send(
            "🔄 Conversation history cleared! Starting fresh — *pound it!* 🐾",
            ephemeral=True,
        )

    @ai_group.command(name="setchannel", description="Set a channel where the AI responds to ALL messages. (Admin only)")
    @app_commands.describe(channel="The channel for always-on AI chat (leave empty to disable)")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_channel(
        self,
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None,
    ):
        await interaction.response.defer()
        settings = load_settings()
        guild_id = str(interaction.guild_id)
        if guild_id not in settings:
            settings[guild_id] = {}

        if channel:
            settings[guild_id]["ai_channel"] = str(channel.id)
            save_settings(settings)
            embed = discord.Embed(
                title="✨ AI Chat Channel Set!",
                description=(
                    f"The bot will now respond to **every message** in {channel.mention}.\n\n"
                    f"Members can also **@mention** the bot anywhere to chat with it.\n"
                    f"Use `/ai chat` for a slash command version."
                ),
                color=0xFF0090,
            )
            await interaction.followup.send(embed=embed)
        else:
            settings[guild_id].pop("ai_channel", None)
            save_settings(settings)
            await interaction.followup.send(
                "✅ Always-on AI channel disabled. The bot will still respond to @mentions.",
                ephemeral=True,
            )

    @ai_group.command(name="personality", description="Learn about Miraculous Bot's AI personality.")
    async def personality(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = discord.Embed(
            title="✨ About Miraculous Bot AI",
            description=(
                "I'm your Miraculous-themed AI assistant, powered by Replit AI! 🐞🐱\n\n"
                "I have the enthusiasm of Marinette, the wit of Cat Noir, and the wisdom of Master Fu — "
                "all rolled into one friendly bot."
            ),
            color=0xFF0090,
        )
        embed.add_field(
            name="💬 How to chat with me",
            value=(
                "• **@mention** me anywhere — I'll reply!\n"
                "• Use `/ai chat [message]` for a clean embed response\n"
                "• Admins can set a dedicated AI chat channel with `/ai setchannel`"
            ),
            inline=False,
        )
        embed.add_field(
            name="🧠 What I can do",
            value=(
                "• Answer Miraculous Ladybug questions 🐞\n"
                "• Help with homework, trivia, or casual chat\n"
                "• Remember the last few messages in a conversation\n"
                "• Tell jokes, write poems, brainstorm ideas..."
            ),
            inline=False,
        )
        embed.add_field(
            name="🔄 Reset history",
            value="Use `/ai reset` to clear my memory for this channel and start fresh.",
            inline=False,
        )
        embed.set_footer(text="Miraculous Bot AI ✨ • Powered by Replit AI")
        await interaction.followup.send(embed=embed)

    @set_channel.error
    async def admin_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.followup.send(
                "❌ You need the **Manage Server** permission to configure the AI channel.",
                ephemeral=True,
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(AIChatCog(bot))
