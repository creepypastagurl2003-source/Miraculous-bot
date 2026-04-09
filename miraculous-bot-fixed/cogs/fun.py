import discord
from discord import app_commands
from discord.ext import commands
import random

# ── Kwami quotes ──────────────────────────────────────────────────────────────
# Each entry: (quote, kwami_name, emoji, embed_color)

KWAMI_QUOTES = [
    ("Marinette, you can do this! I believe in you!", "Tikki", "🍪", 0xFF3333),
    ("You're the best Ladybug I've ever had. And I've had a few.", "Tikki", "🍪", 0xFF3333),
    ("Sometimes the bravest thing you can do is trust yourself.", "Tikki", "🍪", 0xFF3333),
    ("I've been around for thousands of years and I still get excited about cookies.", "Tikki", "🍪", 0xFF3333),
    ("Camembert. That's it. That's all I need from life.", "Plagg", "🧀", 0x222244),
    ("Being Cat Noir is great and all, but have you tried sleeping 16 hours a day?", "Plagg", "🧀", 0x222244),
    ("I've destroyed civilisations. Not on purpose. Mostly.", "Plagg", "🧀", 0x222244),
    ("Cataclysm is a perfectly reasonable solution to most problems.", "Plagg", "🧀", 0x222244),
    ("Love is the most powerful force in the universe. I've seen empires fall because of it.", "Plagg", "🧀", 0x222244),
    ("Every Miraculous holder has one thing in common: they didn't think they were ready.", "Wayzz", "🐢", 0x2D6A4F),
    ("Patience is not just a virtue — it is a superpower.", "Wayzz", "🐢", 0x2D6A4F),
    ("A guardian's greatest strength is knowing when to step back.", "Wayzz", "🐢", 0x2D6A4F),
    ("Oh, you want to know a secret? I know LOTS of secrets. All of them.", "Trixx", "🦊", 0xFF6B00),
    ("Illusions are just truths that haven't been believed yet.", "Trixx", "🦊", 0xFF6B00),
    ("Never underestimate someone who can make you see what isn't there.", "Trixx", "🦊", 0xFF6B00),
    ("My chosen smells like lavender and determination. A winning combination.", "Pollen", "🐝", 0xFFD700),
    ("Royalty is a mindset, darling. Anyone can wear an invisible crown.", "Pollen", "🐝", 0xFFD700),
    ("Second chances are my specialty. It's literally what I do.", "Sass", "🐍", 0x00838F),
    ("Time is not a river. It's a circle. I know because I've looped it a few times.", "Sass", "🐍", 0x00838F),
    ("Music carries the heart when words fall short.", "Longg", "🐉", 0x003366),
    ("Power without compassion is just destruction with extra steps.", "Longg", "🐉", 0x003366),
    ("Every wish comes at a price. But so does giving up.", "Nooroo", "🦋", 0x6A0DAD),
    ("I was not meant for darkness — and yet here we are.", "Nooroo", "🦋", 0x6A0DAD),
    ("Hope is not naive. Hope is the reason any of this works.", "Tikki", "🍪", 0xFF3333),
    ("Destruction and creation are two sides of the same coin. I'd know.", "Plagg", "🧀", 0x222244),
]

# ── Hero quotes ───────────────────────────────────────────────────────────────

HERO_QUOTES = [
    ("Bug out!", "Ladybug", "🐞", 0xFF0000),
    ("Every time I put on this mask, I choose to be brave. Even when I'm scared.", "Ladybug", "🐞", 0xFF0000),
    ("Paris will always have a guardian — and I will always be her.", "Ladybug", "🐞", 0xFF0000),
    ("Lucky Charm! ...I still don't know how this works but I trust it.", "Ladybug", "🐞", 0xFF0000),
    ("I may be clumsy sometimes, but when it counts? I never miss.", "Ladybug", "🐞", 0xFF0000),
    ("Claws out!", "Cat Noir", "🐱", 0x1A1A2E),
    ("I know I can be a bit much. But I'd rather be a bit much than give up.", "Cat Noir", "🐱", 0x1A1A2E),
    ("Every time she looks at me like a hero, I want to be one.", "Cat Noir", "🐱", 0x1A1A2E),
    ("Cataclysm! ...Sorry, I've always wanted to say that dramatically.", "Cat Noir", "🐱", 0x1A1A2E),
    ("I'd follow her into any disaster. Which is good because there are a lot of those.", "Cat Noir", "🐱", 0x1A1A2E),
    ("Get foxy!", "Rena Rouge", "🦊", 0xFF6B00),
    ("Mirage! The trick isn't making them see something false — it's making them believe it.", "Rena Rouge", "🦊", 0xFF6B00),
    ("I was born to be a superhero. Also a journalist. Mainly the journalist, honestly.", "Rena Rouge", "🦊", 0xFF6B00),
    ("Shell on!", "Carapace", "🐢", 0x2D6A4F),
    ("My job is to make sure everyone makes it home safe. So that's what I do.", "Carapace", "🐢", 0x2D6A4F),
    ("Second Chance! ...Okay but why can't I use this for exams?", "Viperion", "🐍", 0x00838F),
    ("I've lived this moment seventeen times. I still choose to be here.", "Viperion", "🐍", 0x00838F),
    ("Venom! That sounded cooler in my head but I'm committed now.", "Queen Bee", "🐝", 0xFFD700),
    ("I may not always be kind. But I'm always honest. That has to count for something.", "Queen Bee", "🐝", 0xFFD700),
    ("Kameiko! Fire, water, lightning — yes, all three, at once.", "Ryuko", "🐉", 0x003366),
    ("Strength without discipline is chaos. I choose discipline.", "Ryuko", "🐉", 0x003366),
    ("They think a guardian is someone who fights. I think a guardian is someone who shows up.", "Ladybug", "🐞", 0xFF0000),
    ("Being a hero isn't about the suit. The suit is just a very cool bonus.", "Cat Noir", "🐱", 0x1A1A2E),
]

# ── Villain quotes ────────────────────────────────────────────────────────────

VILLAIN_QUOTES = [
    ("Fly away, my little akuma, and evilise him!", "Hawk Moth", "🦋", 0x6A0DAD),
    ("Paris will bow to me — it's simply a matter of time.", "Hawk Moth", "🦋", 0x6A0DAD),
    ("You call this a setback? I call it act two.", "Hawk Moth", "🦋", 0x6A0DAD),
    ("Grief is powerful. Loss is powerful. And I have both in abundance.", "Hawk Moth", "🦋", 0x6A0DAD),
    ("They underestimate me. They always underestimate me. It's getting tedious.", "Hawk Moth", "🦋", 0x6A0DAD),
    ("I don't create monsters. I simply give people permission to become what they already are.", "Hawk Moth", "🦋", 0x6A0DAD),
    ("Two Miraculouses. Double the power. Double the inevitability.", "Shadow Moth", "🌑", 0x2C003E),
    ("Patience is the only resource I have in infinite supply.", "Shadow Moth", "🌑", 0x2C003E),
    ("They call me a villain. I call myself a father who refuses to give up.", "Shadow Moth", "🌑", 0x2C003E),
    ("The greatest lie a hero tells is that they never doubt.", "Shadow Moth", "🌑", 0x2C003E),
    ("I create Sentimonsters from emotion. Yours will be particularly interesting.", "Mayura", "🦚", 0x005F73),
    ("Loyalty is not weakness. It is the most dangerous thing in the world.", "Mayura", "🦚", 0x005F73),
    ("I've lied to everyone in this room. Most of them thanked me for it.", "Lila Rossi", "🤥", 0xB22222),
    ("Ladybug's biggest weakness isn't her yo-yo. It's that she trusts people.", "Lila Rossi", "🤥", 0xB22222),
    ("The truth is overrated. A good story is far more powerful.", "Lila Rossi", "🤥", 0xB22222),
]

# ── Fun facts ─────────────────────────────────────────────────────────────────

FUN_FACTS = [
    ("The Miracle Box has existed for over 5,000 years — making it older than most countries, all fashion trends, and definitely older than Adrien's dad's ego. 🏛️", 0xFF0000),
    ("Plagg is responsible for the extinction of the dinosaurs. He claims it was an accident. Tikki has never confirmed this. Plagg has never denied it. 🦕", 0x222244),
    ("Tikki is one of the oldest beings in existence — and she still gets excited about fresh-baked cookies like it's the first time every time. 🍪", 0xFF3333),
    ("Miraculous holders temporarily lose their powers if their transformation timer runs out. Adrien has learned this lesson in the most dramatic ways possible. ⏰", 0x1A1A2E),
    ("The Ladybug Miraculous is considered the most powerful because it can fix any damage caused during a battle. No refunds, though. ✨", 0xFF0000),
    ("Cat Noir's ring has been passed down through history. Some of the most legendary figures in history may have worn it. Plagg ate cheese with all of them. 💍", 0x222244),
    ("The Fox Miraculous creates illusions so convincing they can fool even Miraculous wielders. Trixx considers this its greatest achievement. 🦊", 0xFF6B00),
    ("Hawk Moth can feel the emotions of his akumatized victims at all times. Paris must be absolutely exhausting for him on a Friday night. 🦋", 0x6A0DAD),
    ("Kwamis cannot enter any space without being invited. This makes them technically more polite than most people at parties. 🎉", 0xFF3333),
    ("The Snake Miraculous's Second Chance power resets a 5-minute window of time. Luka has used this to redo conversations at least three times. Nobody knows but him. 🐍", 0x00838F),
    ("Gabriel Agreste is both one of Paris's most beloved citizens and its greatest supervillain. His calendar must be chaos. 📅", 0x6A0DAD),
    ("Marinette has saved Paris over 100 times. She still can't talk to Adrien without losing the ability to form sentences. 🐞", 0xFF0000),
    ("The Turtle Miraculous grants the power of protection — making it the one Miraculous that would actually be useful in rush-hour traffic. 🐢", 0x2D6A4F),
    ("Nino once DJ'd a party mid-battle as Carapace. The set was apparently fire. No notes. 🎧", 0x2D6A4F),
    ("Alya runs the Ladyblog, which documents every akuma attack in Paris. She has more footage than the police. This should concern more people. 📱", 0xFF6B00),
]

# ── Compliments ───────────────────────────────────────────────────────────────

COMPLIMENTS = [
    ("You radiate Ladybug energy — brave, creative, and always figuring it out even when things get chaotic. ✨🐞", 0xFF0000),
    ("You have the kind of heart Tikki would absolutely choose. Warm, determined, and made of pure goodness. 🍪", 0xFF3333),
    ("You're giving Cat Noir levels of charisma today and it's working spectacularly. 🐱", 0x1A1A2E),
    ("If the Miracle Box chose you, I wouldn't question it for a second. You were made for this. 💎", 0xFFD700),
    ("You're the kind of person who would show up to help even when they didn't have to. That's rarer than a Legendary Miraculous. 🏆", 0xFF6B00),
    ("Even Plagg would leave his camembert to cheer you on. That's saying something significant. 🧀", 0x222244),
    ("You have Alya energy — you see the story in everything and you show up with your whole heart every single time. 📱", 0xFF6B00),
    ("Your vibe is warm and steady like Wayzz — the kind of presence that makes everyone around you feel safe. 🐢", 0x2D6A4F),
    ("You're doing amazing. Genuinely. Tikki says so, and she's been around for five thousand years, so she knows. 🍪", 0xFF3333),
    ("The universe clearly went out of its way to put someone like you in it. Lucky us. 🌟", 0xFFD700),
    ("You're someone's favourite person. Multiple people's, probably. Just thought you should know. 💕", 0xFF88CC),
    ("Whatever you're carrying right now — you're handling it with more grace than you know. Keep going. 🌸", 0xFF88CC),
    ("Pollen would give you the biggest bow because you deserve nothing less than full queen treatment. 🐝", 0xFFD700),
    ("Your energy is the 100% on a ship rating. No notes. Completely exceptional. 💘", 0xFF0000),
    ("If there's a Miraculous that grants the power of being genuinely wonderful, you're already wearing it. ✨", 0xFF6B00),
]

# ── Roasts ────────────────────────────────────────────────────────────────────

ROASTS = [
    ("You have the same number of successful plans as Hawk Moth. And the same track record of blaming everyone else. 🦋", 0x6A0DAD),
    ("Plagg has more emotional intelligence than you, and he once destroyed Atlantis out of boredom. 🧀", 0x222244),
    ("Your fashion sense has Lila Rossi writing concerned letters. That's the feedback. 🤥", 0xB22222),
    ("You have Chloé energy — pre-character-development Chloé. In season one. Episode two. 👑", 0xFFD700),
    ("The Miracle Box took one look at you and gently closed itself. Respectfully. 📦", 0xFF6B00),
    ("Trixx could create an illusion of you being competent and nobody would notice the difference. 🦊", 0xFF6B00),
    ("Plagg rated your personality three out of ten camemberts. He's never given three before. He usually just leaves. 🧀", 0x222244),
    ("You have all the planning skills of Marinette trying to confess to Adrien. Results pending. 🎀", 0xFF88AA),
    ("Even akumatized versions of people have better fashion coordination than that. Just saying. 🦋", 0x6A0DAD),
    ("The Ladybug algorithm for shipping you came back as a question mark. It gave up mid-calculation. 🐞", 0xFF0000),
    ("Luka tried to play a song that captured your vibe. The strings snapped. He's working on it. 🎸", 0x00838F),
    ("You're giving very 'background character who gets akumatized in the first five minutes' energy today. ⚡", 0xAAAAAA),
    ("Hawk Moth considered making you a villain and then thought the akuma would just get confused. 🦋", 0x6A0DAD),
    ("Cat Noir has made better puns than your last decision and he makes them in the middle of battles. 🐱", 0x1A1A2E),
]

# ── Mood messages ─────────────────────────────────────────────────────────────
# Each entry: (mood_name, mood_description, emoji, color)

MOODS = [
    ("🌸 Soft and Wholesome", "You're giving warm-bakery-on-a-Sunday energy. Tikki approves. Carry on.", "🍪", 0xFF88AA),
    ("⚡ Chaotic Feral", "Something in you has decided today is a day for poor decisions and great stories. Plagg is proud.", "🧀", 0x222244),
    ("🌙 Mysteriously Tired", "You're present. Technically. Somewhere behind your eyes something is definitely awake. Probably.", "🌙", 0x2C2C54),
    ("🔥 Unhinged Confidence", "You woke up and chose violence against self-doubt. Spectacular. Unexplainable. Iconic.", "🔥", 0xFF4400),
    ("🐢 Slow and Peaceful", "You're in no rush. The turtle miraculous energy. Patient, grounded, impossibly calm.", "🐢", 0x2D6A4F),
    ("💛 Sunshine Mode", "You are emitting positive frequencies at dangerous levels. Multiple people have already felt better near you.", "☀️", 0xFFD700),
    ("🦊 Chaotically Clever", "Your brain is working but in a way nobody around you fully understands. Trixx thinks it's cool.", "🦊", 0xFF6B00),
    ("😤 Ready to Fight (Metaphorically)", "Something has activated you today. Not sure what. But you are READY. Ryuko respects it.", "⚔️", 0x003366),
    ("🤍 Soft Reset Mode", "You don't have words for it, just vibes. It's okay. Wayzz says sometimes silence is also an answer.", "🐢", 0xEEEEEE),
    ("💫 Main Character Energy", "You felt it the moment you woke up. Today you are the protagonist. The plot is yours.", "💫", 0xAA44FF),
    ("🌊 Deep in the Feels", "Something is stirring beneath the surface. Luka's already writing a song about it.", "🎸", 0x00838F),
    ("😌 Unbothered Queen", "Negativity has tried to reach you today. It could not. You were unavailable. Pollen is pleased.", "🐝", 0xFFD700),
    ("💀 Dramatic Villain Arc", "You've decided everything is theatrical today and you're playing the antagonist. Hawk Moth nods in understanding.", "🦋", 0x6A0DAD),
    ("🍃 Peaceful Drifter", "You're somewhere between 'doing fine' and 'floating gently through existence'. It's actually kind of nice.", "🌿", 0x5A9E6F),
    ("🎉 Chaotic Joy", "You have chosen happiness today for absolutely no reason and it is working. The kwamis are celebrating.", "✨", 0xFF6B00),
]


class FunCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── /kwamiquote ───────────────────────────────────────────────────────────

    @app_commands.command(name="kwamiquote", description="Get a random quote from a Miraculous kwami! 🍪")
    async def kwamiquote(self, interaction: discord.Interaction):
        await interaction.response.defer()
        quote, kwami, emoji, color = random.choice(KWAMI_QUOTES)
        embed = discord.Embed(description=f"*\"{quote}\"*", color=color)
        embed.set_author(name=f"{emoji}  {kwami}")
        embed.set_footer(text="✨ Miraculous Kwami Wisdom")
        await interaction.followup.send(embed=embed)

    # ── /heroquote ────────────────────────────────────────────────────────────

    @app_commands.command(name="heroquote", description="Get an inspiring quote from a Miraculous hero! 🐞")
    async def heroquote(self, interaction: discord.Interaction):
        await interaction.response.defer()
        quote, hero, emoji, color = random.choice(HERO_QUOTES)
        embed = discord.Embed(description=f"*\"{quote}\"*", color=color)
        embed.set_author(name=f"{emoji}  {hero}")
        embed.set_footer(text="✨ Miraculous Hero Quotes")
        await interaction.followup.send(embed=embed)

    # ── /villainquote ─────────────────────────────────────────────────────────

    @app_commands.command(name="villainquote", description="A dramatic quote from the villains of Paris... 🦋")
    async def villainquote(self, interaction: discord.Interaction):
        await interaction.response.defer()
        quote, villain, emoji, color = random.choice(VILLAIN_QUOTES)
        embed = discord.Embed(description=f"*\"{quote}\"*", color=color)
        embed.set_author(name=f"{emoji}  {villain}")
        embed.set_footer(text="🌑 Miraculous Villain Monologues")
        await interaction.followup.send(embed=embed)

    # ── /funfact ──────────────────────────────────────────────────────────────

    @app_commands.command(name="funfact", description="Learn a random Miraculous fun fact! ✨")
    async def funfact(self, interaction: discord.Interaction):
        await interaction.response.defer()
        fact, color = random.choice(FUN_FACTS)
        embed = discord.Embed(
            title="📖  Miraculous Fun Fact",
            description=fact,
            color=color,
        )
        embed.set_footer(text="✨ Did you know? • /funfact for another one!")
        await interaction.followup.send(embed=embed)

    # ── /compliment ───────────────────────────────────────────────────────────

    @app_commands.command(name="compliment", description="Receive a wholesome Miraculous-themed compliment! 💖")
    async def compliment(self, interaction: discord.Interaction):
        await interaction.response.defer()
        text, color = random.choice(COMPLIMENTS)
        embed = discord.Embed(
            title="💌  A Message for You",
            description=text,
            color=color,
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url,
        )
        embed.set_footer(text="✨ You deserve this • Miraculous Bot")
        await interaction.followup.send(embed=embed)

    # ── /roast ────────────────────────────────────────────────────────────────

    @app_commands.command(name="roast", description="Get a light, Miraculous-themed roast. Purely for fun! 🔥")
    async def roast(self, interaction: discord.Interaction):
        await interaction.response.defer()
        text, color = random.choice(ROASTS)
        embed = discord.Embed(
            title="🔥  The Roast Has Been Delivered",
            description=text,
            color=color,
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url,
        )
        embed.set_footer(text="🤍 All in good fun • No kwamis were harmed")
        await interaction.followup.send(embed=embed)

    # ── /mood ─────────────────────────────────────────────────────────────────

    @app_commands.command(name="mood", description="Get your random Miraculous mood of the moment! 🌸")
    async def mood(self, interaction: discord.Interaction):
        await interaction.response.defer()
        mood_name, mood_desc, mood_emoji, color = random.choice(MOODS)
        embed = discord.Embed(
            title=f"Your Mood Right Now:  {mood_name}",
            description=mood_desc,
            color=color,
        )
        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url,
        )
        embed.set_footer(text="✨ Mood generated by the Miracle Box • /mood for a new one!")
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(FunCog(bot))
