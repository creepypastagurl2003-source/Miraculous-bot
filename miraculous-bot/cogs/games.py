import discord
from discord import app_commands
from discord.ext import commands
import random
import re
from typing import Optional

# Each entry: (outcome_emoji, kwami_response, embed_color)
EIGHT_BALL_RESPONSES = [
    # ── Positive ──────────────────────────────────────────────────────────────
    ("✅", "🍪 Tikki says: *Absolutely! You've got this!*", 0x2ECC71),
    ("✅", "🐞 The Lucky Charm points to **YES**. Trust it.", 0x2ECC71),
    ("✅", "✨ The Miracle Box glows warmly. It's a yes.", 0x2ECC71),
    ("✅", "🌟 The stars aligned. Miraculous Ladybug confirms it.", 0x2ECC71),
    ("✅", "🐱 Cat Noir gives a thumbs up. Claws out — go for it!", 0x2ECC71),
    ("✅", "🐢 Wayzz has meditated on this. The answer is yes.", 0x2ECC71),
    ("✅", "🐝 Pollen has consulted her feelings. Most certainly, yes.", 0x2ECC71),
    # ── Neutral ───────────────────────────────────────────────────────────────
    ("🟡", "🦊 Trixx says: *Maybe. But probably not the way you're imagining it.*", 0xF1C40F),
    ("🟡", "🧀 Plagg shrugs and goes back to eating. Unclear.", 0xF1C40F),
    ("🟡", "🦋 The answer is somewhere in the shadows. Hawk Moth is also unsure.", 0xF1C40F),
    ("🟡", "🐍 Second Chance suggests trying again in five minutes.", 0xF1C40F),
    ("🟡", "🌑 The signs are murky. Shadow Moth is also confused.", 0xF1C40F),
    ("🟡", "🎭 The universe says: *it's complicated.* Very. Very complicated.", 0xF1C40F),
    # ── Negative ──────────────────────────────────────────────────────────────
    ("❌", "💀 The akuma says no. The butterfly says no. Everything says no.", 0xE74C3C),
    ("❌", "🧀 Plagg ate the answer. He says it was 'not great'.", 0xE74C3C),
    ("❌", "🤥 Lila Rossi would say yes. That should tell you something.", 0xE74C3C),
    ("❌", "🦚 Mayura senses doubt in this endeavour. Considerable doubt.", 0xE74C3C),
    ("❌", "💔 The ship rating for this plan came back at 4%. Don't.", 0xE74C3C),
    ("❌", "🐞 Ladybug shook her head slowly. That's a no.", 0xE74C3C),
]

SLOT_SYMBOLS = ["🍒", "🍋", "🍊", "🍇", "⭐", "💎", "7️⃣", "🔔", "🍀", "🎰"]

SLOT_PAYOUTS = {
    ("💎", "💎", "💎"): ("JACKPOT! 💎💎💎", 0xFFD700),
    ("7️⃣", "7️⃣", "7️⃣"): ("LUCKY SEVENS! 7️⃣7️⃣7️⃣", 0xFF6600),
    ("⭐", "⭐", "⭐"): ("TRIPLE STAR! ⭐⭐⭐", 0xFFCC00),
    ("🍀", "🍀", "🍀"): ("TRIPLE CLOVER! 🍀🍀🍀", 0x00CC00),
}

TRIVIA_QUESTIONS = [
    {"q": "What is the capital of France?", "choices": ["Berlin", "Paris", "Rome", "Madrid"], "answer": 1},
    {"q": "How many sides does a hexagon have?", "choices": ["5", "6", "7", "8"], "answer": 1},
    {"q": "Which planet is known as the Red Planet?", "choices": ["Venus", "Jupiter", "Mars", "Saturn"], "answer": 2},
    {"q": "What is the chemical symbol for gold?", "choices": ["Ag", "Fe", "Au", "Cu"], "answer": 2},
    {"q": "Who painted the Mona Lisa?", "choices": ["Michelangelo", "Leonardo da Vinci", "Raphael", "Caravaggio"], "answer": 1},
    {"q": "What is the largest ocean on Earth?", "choices": ["Atlantic", "Indian", "Arctic", "Pacific"], "answer": 3},
    {"q": "How many bones are in the human body?", "choices": ["196", "206", "216", "226"], "answer": 1},
    {"q": "What language has the most native speakers?", "choices": ["English", "Spanish", "Mandarin Chinese", "Hindi"], "answer": 2},
    {"q": "What year did the Titanic sink?", "choices": ["1910", "1912", "1914", "1916"], "answer": 1},
    {"q": "Which element has the atomic number 1?", "choices": ["Helium", "Oxygen", "Carbon", "Hydrogen"], "answer": 3},
    {"q": "What is the fastest land animal?", "choices": ["Lion", "Cheetah", "Greyhound", "Pronghorn"], "answer": 1},
    {"q": "How many strings does a standard guitar have?", "choices": ["4", "5", "6", "7"], "answer": 2},
    {"q": "What is the square root of 144?", "choices": ["11", "12", "13", "14"], "answer": 1},
    {"q": "Which country invented pizza?", "choices": ["France", "Greece", "Italy", "Spain"], "answer": 2},
    {"q": "What is the longest river in the world?", "choices": ["Amazon", "Yangtze", "Mississippi", "Nile"], "answer": 3},
    {"q": "Which Disney movie features the song 'Let It Go'?", "choices": ["Tangled", "Brave", "Moana", "Frozen"], "answer": 3},
    {"q": "How many planets are in our solar system?", "choices": ["7", "8", "9", "10"], "answer": 1},
    {"q": "What sport is played at Wimbledon?", "choices": ["Cricket", "Golf", "Tennis", "Badminton"], "answer": 2},
    {"q": "What is the hardest natural substance on Earth?", "choices": ["Platinum", "Quartz", "Diamond", "Corundum"], "answer": 2},
    {"q": "Which animal is the symbol of the World Wildlife Fund?", "choices": ["Polar Bear", "Giant Panda", "Snow Leopard", "Tiger"], "answer": 1},
]

TRUTH_QUESTIONS = [
    "What is the most embarrassing thing that has ever happened to you?",
    "What is your biggest fear?",
    "Have you ever lied to get out of trouble? What happened?",
    "What is the most childish thing you still do?",
    "Who was your first crush?",
    "What is the weirdest dream you've ever had?",
    "What is the worst gift you've ever received?",
    "Have you ever cheated on a test?",
    "What is something you've never told anyone?",
    "What is the most embarrassing song you secretly love?",
    "What is your most annoying habit?",
    "If you could be invisible for a day, what would you do?",
    "What is the pettiest thing you've ever done?",
    "Have you ever pretended to be sick to avoid something?",
    "What is the worst thing you've ever said to someone?",
    "What is something you regret doing?",
    "What is your guilty pleasure?",
    "Have you ever blamed someone else for something you did?",
    "What is the strangest thing you've ever eaten?",
    "What is your most embarrassing childhood memory?",
]

DARE_QUESTIONS = [
    "Send a voice message of you singing a random song.",
    "Change your nickname to whatever the next person chooses for an hour.",
    "Write a dramatic poem about someone in this server and share it.",
    "Send the most unflattering selfie you can take.",
    "Do your best impression of another server member.",
    "Send a message entirely in emojis that describes your day.",
    "Change your profile picture to something funny for 1 hour.",
    "Speak in rhymes for the next 5 minutes in chat.",
    "Send the most embarrassing photo you have in your camera roll.",
    "Type everything in alternating caps for the next 5 messages.",
    "Send a dramatic reading of the last message in this channel.",
    "Give a sincere compliment to every person currently online.",
    "Write a short story using only words with 4 letters or less.",
    "Send a voice message in your most exaggerated accent.",
    "Change your status to something embarrassing for 30 minutes.",
]

WYR_QUESTIONS = [
    ("Have the ability to fly", "Be able to breathe underwater"),
    ("Always speak your mind", "Never speak again"),
    ("Live in the past", "Live in the future"),
    ("Be incredibly rich but lonely", "Be poor but surrounded by loved ones"),
    ("Know when you'll die", "Know how you'll die"),
    ("Have super strength", "Have super speed"),
    ("Eat only sweet food forever", "Eat only spicy food forever"),
    ("Be able to talk to animals", "Be able to speak any human language"),
    ("Always be 10 minutes late", "Always be 20 minutes early"),
    ("Have no internet for a month", "Have no music for a year"),
    ("Fight one horse-sized duck", "Fight 100 duck-sized horses"),
    ("Lose all your memories from birth to age 10", "Lose your last year of memories"),
    ("Be famous but hated", "Be unknown but loved by close ones"),
    ("Have an extra arm", "Have an extra leg"),
    ("Never be able to use a phone again", "Never be able to watch TV again"),
]


class RPSView(discord.ui.View):
    OPTIONS = {"🪨 Rock": "rock", "📄 Paper": "paper", "✂️ Scissors": "scissors"}
    BEATS = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
    EMOJI = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}

    def __init__(self, challenger: discord.User, opponent: Optional[discord.User], bot_play: Optional[str]):
        super().__init__(timeout=60)
        self.challenger = challenger
        self.opponent = opponent
        self.bot_play = bot_play
        self.challenger_choice: Optional[str] = None
        self.opponent_choice: Optional[str] = None

        for label, value in self.OPTIONS.items():
            btn = discord.ui.Button(label=label, style=discord.ButtonStyle.primary, custom_id=value)
            btn.callback = self.make_callback(value)
            self.add_item(btn)

    def make_callback(self, choice: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id == self.challenger.id:
                if self.challenger_choice:
                    await interaction.response.send_message("You already chose!", ephemeral=True)
                    return
                self.challenger_choice = choice
            elif self.opponent and interaction.user.id == self.opponent.id:
                if self.opponent_choice:
                    await interaction.response.send_message("You already chose!", ephemeral=True)
                    return
                self.opponent_choice = choice
            else:
                await interaction.response.send_message("This game is not for you!", ephemeral=True)
                return

            if self.bot_play:
                self.opponent_choice = self.bot_play

            if self.challenger_choice and self.opponent_choice:
                await self.finish(interaction, choice)
            else:
                await interaction.response.send_message(
                    f"You chose **{self.EMOJI[choice]} {choice.capitalize()}**! Waiting for your opponent...",
                    ephemeral=True,
                )
        return callback

    async def finish(self, interaction: discord.Interaction, last_choice: str):
        await interaction.response.send_message(
            f"You chose **{self.EMOJI[last_choice]} {last_choice.capitalize()}**! Revealing results...",
            ephemeral=True,
        )
        self.stop()
        for item in self.children:
            item.disabled = True

        c = self.challenger_choice
        o = self.opponent_choice
        ce = self.EMOJI[c]
        oe = self.EMOJI[o]
        opp_name = self.opponent.display_name if self.opponent else "Bot"

        if c == o:
            result = "🤝 **It's a tie!**"
            color = discord.Color.yellow()
        elif self.BEATS[c] == o:
            result = f"🏆 **{self.challenger.display_name} wins!**"
            color = discord.Color.green()
        else:
            result = f"💀 **{opp_name} wins!**"
            color = discord.Color.red()

        embed = discord.Embed(
            title="🪨📄✂️ Rock Paper Scissors — Result!",
            description=(
                f"**{self.challenger.display_name}:** {ce} {c.capitalize()}\n"
                f"**{opp_name}:** {oe} {o.capitalize()}\n\n"
                f"{result}"
            ),
            color=color,
        )
        try:
            await interaction.message.edit(embed=embed, view=self)
        except Exception:
            pass

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


class TriviaView(discord.ui.View):
    def __init__(self, question: dict, asker: discord.User):
        super().__init__(timeout=30)
        self.question = question
        self.asker = asker
        self.answered = set()
        labels = ["A", "B", "C", "D"]
        colors = [
            discord.ButtonStyle.primary,
            discord.ButtonStyle.success,
            discord.ButtonStyle.danger,
            discord.ButtonStyle.secondary,
        ]
        for i, (choice, label, color) in enumerate(zip(question["choices"], labels, colors)):
            btn = discord.ui.Button(label=f"{label}: {choice}", style=color, custom_id=str(i))
            btn.callback = self.make_callback(i)
            self.add_item(btn)

    def make_callback(self, idx: int):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id in self.answered:
                await interaction.response.send_message("You already answered!", ephemeral=True)
                return
            self.answered.add(interaction.user.id)
            correct_idx = self.question["answer"]
            correct_text = self.question["choices"][correct_idx]
            labels = ["A", "B", "C", "D"]
            if idx == correct_idx:
                msg = f"✅ Correct! The answer is **{labels[correct_idx]}: {correct_text}**!"
            else:
                chosen = self.question["choices"][idx]
                msg = f"❌ Wrong! You chose **{labels[idx]}: {chosen}**. The correct answer was **{labels[correct_idx]}: {correct_text}**."
            await interaction.response.send_message(msg, ephemeral=True)
        return callback

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


class WYRView(discord.ui.View):
    def __init__(self, option_a: str, option_b: str):
        super().__init__(timeout=60)
        self.option_a = option_a
        self.option_b = option_b
        self.votes_a: set[int] = set()
        self.votes_b: set[int] = set()

    @discord.ui.button(label="Option A", style=discord.ButtonStyle.primary, emoji="🅰️")
    async def vote_a(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        uid = interaction.user.id
        if uid in self.votes_a:
            self.votes_a.discard(uid)
            await interaction.followup.send("Removed your vote for A.", ephemeral=True)
        else:
            self.votes_a.add(uid)
            self.votes_b.discard(uid)
            await interaction.followup.send(f"You voted for **A: {self.option_a}**!", ephemeral=True)
        await self.update_message(interaction)

    @discord.ui.button(label="Option B", style=discord.ButtonStyle.success, emoji="🅱️")
    async def vote_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        uid = interaction.user.id
        if uid in self.votes_b:
            self.votes_b.discard(uid)
            await interaction.followup.send("Removed your vote for B.", ephemeral=True)
        else:
            self.votes_b.add(uid)
            self.votes_a.discard(uid)
            await interaction.followup.send(f"You voted for **B: {self.option_b}**!", ephemeral=True)
        await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        total = len(self.votes_a) + len(self.votes_b)
        a_pct = round(len(self.votes_a) / total * 100) if total else 0
        b_pct = 100 - a_pct if total else 0

        def bar(pct: int) -> str:
            filled = round(pct / 10)
            return "█" * filled + "░" * (10 - filled)

        embed = discord.Embed(
            title="🤔 Would You Rather...",
            description=(
                f"🅰️ **{self.option_a}**\n`{bar(a_pct)}` {a_pct}% ({len(self.votes_a)} vote(s))\n\n"
                f"🅱️ **{self.option_b}**\n`{bar(b_pct)}` {b_pct}% ({len(self.votes_b)} vote(s))"
            ),
            color=discord.Color.blurple(),
        )
        embed.set_footer(text=f"{total} vote(s) total • Click again to unvote")
        try:
            await interaction.message.edit(embed=embed, view=self)
        except Exception:
            pass


HUG_GIFS = [
    "https://media.tenor.com/I_oWAjGMu9QAAAAC/anime-hug.gif",
    "https://media.tenor.com/7Q5Ck7i2gGAAAAAC/anime-hug-hug.gif",
    "https://media.tenor.com/UWxlGbdjbKYAAAAC/anime-hug.gif",
    "https://media.tenor.com/RJe-gJdJF9UAAAAC/hug-anime.gif",
    "https://media.tenor.com/p4bSl4FaRK8AAAAC/couple-hug-cute-couple.gif",
    "https://media.tenor.com/oB-8oGNqB_MAAAAC/hug-cute.gif",
    "https://media.tenor.com/6xyKhAjH0LUAAAAC/anime-hug-kawaii.gif",
    "https://media.tenor.com/mVFmCBa5XHIAAAAC/hug-anime-hug.gif",
    "https://media.tenor.com/jlFl1Q0lXqsAAAAC/anime-hug.gif",
    "https://media.tenor.com/yPAoXLMNmT4AAAAC/hug-cute-hug.gif",
    "https://media.tenor.com/0ZhblUuZVF4AAAAC/mochi-hug-mochi-mochi.gif",
    "https://media.tenor.com/OsQAJd0xkJAAAAAC/peach-and-goma-hug.gif",
]

HUG_MESSAGES = [
    "{hugger} sneaks up behind {hugged} and wraps them in the coziest bear hug! 🐻",
    "{hugger} tackles {hugged} with a hug so strong it could crush a Kwami. 💪✨",
    "{hugger} flings both arms around {hugged} and refuses to let go. This is home now.",
    "{hugger} squeezes {hugged} so tight they make little squeaky noises. The squeak is mandatory.",
    "{hugger} gives {hugged} a hug that lasts exactly 7 seconds — the scientifically optimal hug length. 🔬",
    "{hugger} ambushes {hugged} with a hug from out of nowhere. No warning. Only warmth. 🌸",
    "{hugger} wraps {hugged} in a hug like a warm burrito of love. 🌯💕",
    "{hugger} speed-runs to {hugged} and attaches like a koala. They are one now. 🐨",
    "{hugger} offers {hugged} a hug. {hugged} has no choice. It is happening. 🎀",
    "{hugger} hugs {hugged} and whispers 'you are appreciated' into their ear. Feeling okay yet? 💛",
    "{hugger} launches at {hugged} at full momentum. This is not just a hug — this is an event.",
    "{hugger} gives {hugged} the kind of hug that makes all problems 40% smaller. 🌟",
    "{hugger} and {hugged} are now stuck together. Scientists are baffled. Love has no explanation.",
    "{hugger} wraps {hugged} up like a little bean and holds on for dear life. 🫘💕",
    "{hugger} assigns {hugged} exactly one (1) wholesome hug. Please accept.",
]


class GamesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="8ball", description="Ask the Miracle Box a yes/no question! 🎱")
    @app_commands.describe(question="Your yes/no question for the Miracle Box")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        await interaction.response.defer()
        outcome, response, color = random.choice(EIGHT_BALL_RESPONSES)
        if outcome == "✅":
            title = "🟢  The Miracle Box Speaks"
        elif outcome == "🟡":
            title = "🟡  The Miracle Box Ponders"
        else:
            title = "🔴  The Miracle Box Has Concerns"
        embed = discord.Embed(title=title, color=color)
        embed.add_field(name="❓ Question", value=f"*{question}*", inline=False)
        embed.add_field(name=f"{outcome} Answer", value=response, inline=False)
        embed.set_footer(
            text=f"Asked by {interaction.user.display_name} • ✨ The Miracle Box knows all",
            icon_url=interaction.user.display_avatar.url,
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="coinflip", description="Flip a coin!")
    async def coinflip(self, interaction: discord.Interaction):
        await interaction.response.defer()
        result = random.choice(["Heads", "Tails"])
        embed = discord.Embed(
            title="🪙 Coin Flip!",
            description=f"The coin landed on... **{result}!**",
            color=discord.Color.gold(),
        )
        embed.set_footer(text=f"Flipped by {interaction.user.display_name}")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="roll", description="Roll dice! Supports notation like 2d6 or 1d20.")
    @app_commands.describe(dice="Dice notation (e.g. 2d6, 1d20, 3d8). Default: 1d6")
    async def roll(self, interaction: discord.Interaction, dice: str = "1d6"):
        await interaction.response.defer()
        dice = dice.strip().lower()
        match = re.fullmatch(r"(\d+)d(\d+)", dice)
        if not match:
            await interaction.followup.send("❌ Invalid dice format. Use something like `2d6`, `1d20`, `3d8`.", ephemeral=True)
            return
        count = int(match.group(1))
        sides = int(match.group(2))
        if count < 1 or count > 20:
            await interaction.followup.send("❌ You can roll between 1 and 20 dice.", ephemeral=True)
            return
        if sides < 2 or sides > 1000:
            await interaction.followup.send("❌ Dice must have between 2 and 1000 sides.", ephemeral=True)
            return
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls)
        embed = discord.Embed(title=f"🎲 Rolling {dice.upper()}", color=discord.Color.orange())
        if count == 1:
            embed.description = f"You rolled a **{total}**!"
        else:
            rolls_str = " + ".join(str(r) for r in rolls)
            embed.description = f"**Rolls:** {rolls_str}\n**Total:** {total}"
        if count > 1:
            embed.add_field(name="Min", value=str(min(rolls)), inline=True)
            embed.add_field(name="Max", value=str(max(rolls)), inline=True)
            embed.add_field(name="Average", value=f"{total / count:.1f}", inline=True)
        embed.set_footer(text=f"Rolled by {interaction.user.display_name}")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="slots", description="Spin the slot machine! 🎰")
    async def slots(self, interaction: discord.Interaction):
        await interaction.response.defer()
        reels = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
        result_tuple = tuple(reels)
        payout_key = None
        for key in SLOT_PAYOUTS:
            if result_tuple == key:
                payout_key = key
                break
        two_match = reels[0] == reels[1] or reels[1] == reels[2] or reels[0] == reels[2]
        display = f"[ {reels[0]} | {reels[1]} | {reels[2]} ]"
        if payout_key:
            label, color = SLOT_PAYOUTS[payout_key]
            result_text = f"🎉 **{label}**"
        elif two_match:
            result_text = "😊 **Two of a kind! Close one!**"
            color = 0x3498DB
        else:
            result_text = "😔 **No match. Better luck next time!**"
            color = 0x95A5A6
        embed = discord.Embed(
            title="🎰 Slot Machine",
            description=f"# {display}\n\n{result_text}",
            color=color if payout_key or not two_match else 0x3498DB,
        )
        embed.set_footer(text=f"Played by {interaction.user.display_name}")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="rps", description="Play Rock Paper Scissors!")
    @app_commands.describe(opponent="Challenge a user (leave empty to play against the bot)")
    async def rps(self, interaction: discord.Interaction, opponent: Optional[discord.Member] = None):
        await interaction.response.defer()
        if opponent and opponent.id == interaction.user.id:
            await interaction.followup.send("❌ You can't play against yourself!", ephemeral=True)
            return
        if opponent and opponent.bot:
            await interaction.followup.send("❌ You can't challenge another bot!", ephemeral=True)
            return
        bot_play = None
        if not opponent:
            bot_play = random.choice(["rock", "paper", "scissors"])
        opp_name = opponent.display_name if opponent else "Bot"
        desc = (
            f"**{interaction.user.display_name}** vs **{opp_name}**\n\nPick your move!"
            + (f"\n\n{opponent.mention}, it's your turn too!" if opponent else "")
        )
        embed = discord.Embed(title="🪨📄✂️ Rock Paper Scissors", description=desc, color=discord.Color.blurple())
        view = RPSView(challenger=interaction.user, opponent=opponent, bot_play=bot_play)
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="trivia", description="Answer a random trivia question!")
    async def trivia(self, interaction: discord.Interaction):
        await interaction.response.defer()
        q = random.choice(TRIVIA_QUESTIONS)
        labels = ["A", "B", "C", "D"]
        embed = discord.Embed(title="🧠 Trivia Time!", description=f"**{q['q']}**", color=discord.Color.purple())
        for i, (label, choice) in enumerate(zip(labels, q["choices"])):
            embed.add_field(name=f"{label}", value=choice, inline=True)
        embed.set_footer(text="You have 30 seconds to answer!")
        view = TriviaView(q, interaction.user)
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="wyr", description="Would you rather...?")
    async def wyr(self, interaction: discord.Interaction):
        await interaction.response.defer()
        option_a, option_b = random.choice(WYR_QUESTIONS)
        embed = discord.Embed(
            title="🤔 Would You Rather...",
            description=(
                f"🅰️ **{option_a}**\n`░░░░░░░░░░` 0% (0 vote(s))\n\n"
                f"🅱️ **{option_b}**\n`░░░░░░░░░░` 0% (0 vote(s))"
            ),
            color=discord.Color.blurple(),
        )
        embed.set_footer(text="0 vote(s) total • Click again to unvote")
        view = WYRView(option_a, option_b)
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="truth", description="Get a random truth question!")
    async def truth(self, interaction: discord.Interaction):
        await interaction.response.defer()
        question = random.choice(TRUTH_QUESTIONS)
        embed = discord.Embed(
            title="🔮 Truth",
            description=f"**{interaction.user.display_name}**, answer honestly:\n\n*{question}*",
            color=discord.Color.from_rgb(100, 149, 237),
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="dare", description="Get a random dare!")
    async def dare(self, interaction: discord.Interaction):
        await interaction.response.defer()
        challenge = random.choice(DARE_QUESTIONS)
        embed = discord.Embed(
            title="🔥 Dare",
            description=f"**{interaction.user.display_name}**, you must:\n\n*{challenge}*",
            color=discord.Color.from_rgb(255, 99, 71),
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="choose", description="Let the bot choose between multiple options!")
    @app_commands.describe(options="Options separated by commas (e.g. pizza, tacos, sushi)")
    async def choose(self, interaction: discord.Interaction, options: str):
        await interaction.response.defer()
        choices = [o.strip() for o in options.split(",") if o.strip()]
        if len(choices) < 2:
            await interaction.followup.send("❌ Please give at least 2 options separated by commas.", ephemeral=True)
            return
        if len(choices) > 20:
            await interaction.followup.send("❌ Maximum 20 options allowed.", ephemeral=True)
            return
        pick = random.choice(choices)
        embed = discord.Embed(title="🎯 The Bot Chooses...", description=f"**{pick}**", color=discord.Color.teal())
        embed.add_field(name="Options", value=" • ".join(choices), inline=False)
        embed.set_footer(text=f"Chosen from {len(choices)} options")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="rate", description="Let the bot rate anything!")
    @app_commands.describe(thing="What should the bot rate?")
    async def rate(self, interaction: discord.Interaction, thing: str):
        await interaction.response.defer()
        seed = sum(ord(c) for c in thing.lower()) + interaction.user.id
        rating = seed % 11
        bar_filled = "█" * rating + "░" * (10 - rating)
        if rating <= 3:
            emoji, comment = "💀", "Absolutely terrible."
        elif rating <= 5:
            emoji, comment = "😐", "Could be worse, I guess."
        elif rating <= 7:
            emoji, comment = "😊", "Pretty decent!"
        elif rating <= 9:
            emoji, comment = "🔥", "Really good!"
        else:
            emoji, comment = "💯", "Absolutely perfect!"
        embed = discord.Embed(
            title=f"{emoji} Rating: {thing}",
            description=f"`[{bar_filled}]` **{rating}/10**\n\n*{comment}*",
            color=discord.Color.orange(),
        )
        embed.set_footer(text="Totally scientific rating system™")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="hug", description="Give someone a warm hug! 🤗")
    @app_commands.describe(user="The person you want to hug")
    async def hug(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer()
        hugger = interaction.user.mention
        hugged = user.mention
        message = random.choice(HUG_MESSAGES).format(hugger=hugger, hugged=hugged)
        gif = random.choice(HUG_GIFS)
        embed = discord.Embed(description=message, color=0xFF9EC4)
        embed.set_image(url=gif)
        embed.set_footer(text="🤗 spread the love!")
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(GamesCog(bot))
