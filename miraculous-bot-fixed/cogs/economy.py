import discord
from discord import app_commands
from discord.ext import commands
import json
import os
import random
import time
import logging
from typing import Optional

logger = logging.getLogger("bot.economy")

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "economy.json")

CURRENCY = "Miraculons"
CURRENCY_EMOJI = "🌟"

DAILY_AMOUNT = (200, 400)
WEEKLY_AMOUNT = (1500, 2500)
WORK_AMOUNT = (50, 200)
CRIME_AMOUNT = (100, 500)
CRIME_FINE = (50, 300)
ROB_MIN_BALANCE = 200
ROB_SUCCESS_CHANCE = 0.4
ROB_AMOUNT_RANGE = (0.1, 0.35)
ROB_FINE_RANGE = (50, 200)
GAMBLE_MIN = 10

COOLDOWNS = {
    "daily": 86400,
    "weekly": 604800,
    "work": 3600,
    "crime": 7200,
    "rob": 3600,
}

WORK_MESSAGES = [
    "You helped Marinette deliver fresh macarons from the Dupain-Cheng Bakery! 🥐",
    "You assisted Cat Noir on a midnight patrol across the rooftops of Paris! 🐱",
    "You worked as a model at the Agreste Fashion House runway show! 👗",
    "You sold exclusive Ladybug photos to Alya's Ladyblog! 📸",
    "You helped Master Fu restore ancient Miraculous artefacts! 🏺",
    "You taught fencing lessons at Kagami's dojo! ⚔️",
    "You performed at Kitty Section's surprise concert on the Liberty houseboat! 🎸",
    "You catered Chloé's birthday party at Le Grand Paris! 🎂",
    "You helped Nino DJ a school dance at Collège Françoise Dupont! 🎧",
    "You tutored Max in creative writing while Markov took notes! 🤖",
    "You ran errands for Mayor Bourgeois across Paris! 🗼",
    "You designed a costume for Luka's next performance! 🎵",
]

CRIME_WIN_MESSAGES = [
    "You snuck past Hawk Moth's cameras and made off with the loot! 🦋",
    "You swiped a rare Miraculous replica from the Paris museum before security noticed! 🏛️",
    "You ran a sneaky kwami smuggling ring right under Ladybug's nose! 🐞",
    "You sold counterfeit Lucky Charm bracelets at the Paris market! 🍀",
    "You talked your way past the Agreste mansion guards and pilfered the wine cellar! 🍷",
]

CRIME_FAIL_MESSAGES = [
    "Ladybug caught you red-handed and fined you on the spot! 🐞",
    "Cat Noir foiled your scheme with a perfectly timed Cataclysm! 🐱",
    "Ryuko spotted you from above and you had to pay up! 🐉",
    "You ran straight into a Carapace shield wall — ouch! 🐢",
    "Rena Rouge's Mirage made you think you escaped… then you got caught! 🦊",
]

SHOP_ITEMS = {
    "ladybug_charm": {
        "name": "Ladybug Charm",
        "emoji": "🐞",
        "price": 300,
        "description": "A lucky charm blessed by Ladybug herself. Doubles your next `/daily` reward.",
        "usable": True,
        "effect": "double_daily",
    },
    "cat_noir_badge": {
        "name": "Cat Noir Badge",
        "emoji": "🐱",
        "price": 300,
        "description": "An authentic Cat Noir paw badge. Doubles your next `/work` earnings.",
        "usable": True,
        "effect": "double_work",
    },
    "lucky_charm": {
        "name": "Lucky Charm",
        "emoji": "🍀",
        "price": 500,
        "description": "Swing the odds in your favour! Boosts your gamble win chance to 60% once.",
        "usable": True,
        "effect": "lucky_gamble",
    },
    "cataclysm_coin": {
        "name": "Cataclysm Coin",
        "emoji": "⚫",
        "price": 700,
        "description": "Charged with Plagg's energy. Instantly double your gamble winnings once.",
        "usable": True,
        "effect": "double_gamble",
    },
    "kwami_companion": {
        "name": "Kwami Companion",
        "emoji": "✨",
        "price": 1000,
        "description": "A tiny kwami spirit follows you around. Pure bragging rights.",
        "usable": False,
        "effect": None,
    },
    "butterfly_brooch": {
        "name": "Butterfly Brooch",
        "emoji": "🦋",
        "price": 2500,
        "description": "A replica of Hawk Moth's infamous brooch. The rarest collectible.",
        "usable": False,
        "effect": None,
    },
    "miraculous_box": {
        "name": "Miraculous Box",
        "emoji": "📦",
        "price": 5000,
        "description": "A legendary box rumoured to contain a secret kwami. Ultimate flex.",
        "usable": False,
        "effect": None,
    },
}


def load_data() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"users": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_user(data: dict, user_id: str) -> dict:
    if user_id not in data["users"]:
        data["users"][user_id] = {
            "balance": 500,
            "last_daily": 0,
            "last_weekly": 0,
            "last_work": 0,
            "last_crime": 0,
            "last_rob": 0,
            "inventory": [],
            "active_effects": [],
            "total_earned": 500,
            "total_spent": 0,
        }
    u = data["users"][user_id]
    for key, default in {
        "last_daily": 0, "last_weekly": 0, "last_work": 0,
        "last_crime": 0, "last_rob": 0, "inventory": [],
        "active_effects": [], "total_earned": 0, "total_spent": 0,
    }.items():
        if key not in u:
            u[key] = default
    return u


def format_balance(amount: int) -> str:
    return f"{CURRENCY_EMOJI} **{amount:,}** {CURRENCY}"


def cooldown_remaining(last_used: float, cooldown: int) -> int:
    remaining = int(cooldown - (time.time() - last_used))
    return max(0, remaining)


def format_time(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m}m {s}s"
    h, rem = divmod(seconds, 3600)
    m, _ = divmod(rem, 60)
    return f"{h}h {m}m"


def has_effect(user: dict, effect: str) -> bool:
    return effect in user.get("active_effects", [])


def consume_effect(user: dict, effect: str):
    effects = user.get("active_effects", [])
    if effect in effects:
        effects.remove(effect)
        user["active_effects"] = effects
        return True
    return False


class EconomyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    eco_group = app_commands.Group(name="economy", description="Miraculous economy system")

    @eco_group.command(name="balance", description="Check your or someone else's Miraculons balance.")
    @app_commands.describe(user="User to check (leave empty for yourself)")
    async def balance(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        await interaction.response.defer()
        target = user or interaction.user
        data = load_data()
        u = get_user(data, str(target.id))
        save_data(data)

        embed = discord.Embed(
            title=f"{CURRENCY_EMOJI} {target.display_name}'s Wallet",
            color=0xFFD700,
        )
        embed.add_field(name="💰 Balance", value=format_balance(u["balance"]), inline=True)
        embed.add_field(name="📈 Total Earned", value=f"{CURRENCY_EMOJI} {u['total_earned']:,}", inline=True)
        embed.add_field(name="🛍️ Total Spent", value=f"{CURRENCY_EMOJI} {u['total_spent']:,}", inline=True)

        items = u.get("inventory", [])
        effects = u.get("active_effects", [])
        if items:
            item_display = ", ".join(
                f"{SHOP_ITEMS[i]['emoji']} {SHOP_ITEMS[i]['name']}"
                for i in items if i in SHOP_ITEMS
            )
            embed.add_field(name="🎒 Inventory", value=item_display or "Empty", inline=False)
        if effects:
            embed.add_field(
                name="⚡ Active Effects",
                value=", ".join(f"`{e}`" for e in effects),
                inline=False,
            )

        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text="Miraculous Economy • Earn Miraculons and rise to the top!")
        await interaction.followup.send(embed=embed)

    @eco_group.command(name="daily", description="Claim your daily Miraculons reward!")
    async def daily(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        u = get_user(data, str(interaction.user.id))

        cd = cooldown_remaining(u["last_daily"], COOLDOWNS["daily"])
        if cd > 0:
            await interaction.followup.send(
                f"⏳ You already claimed your daily! Come back in **{format_time(cd)}**.",
                ephemeral=True,
            )
            return

        amount = random.randint(*DAILY_AMOUNT)
        doubled = has_effect(u, "double_daily")
        if doubled:
            consume_effect(u, "double_daily")
            amount *= 2

        u["balance"] += amount
        u["total_earned"] += amount
        u["last_daily"] = time.time()
        save_data(data)

        embed = discord.Embed(
            title="🌅 Daily Reward Claimed!",
            color=0xFFD700,
        )
        embed.add_field(name="💰 Received", value=format_balance(amount), inline=True)
        embed.add_field(name="👛 New Balance", value=format_balance(u["balance"]), inline=True)
        if doubled:
            embed.add_field(name="✨ Bonus", value="Ladybug Charm doubled your reward!", inline=False)
        embed.set_footer(text="Come back tomorrow for more! • /economy weekly for bigger rewards")
        await interaction.followup.send(embed=embed)

    @eco_group.command(name="weekly", description="Claim your weekly Miraculons reward!")
    async def weekly(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        u = get_user(data, str(interaction.user.id))

        cd = cooldown_remaining(u["last_weekly"], COOLDOWNS["weekly"])
        if cd > 0:
            await interaction.followup.send(
                f"⏳ Weekly reward already claimed! Come back in **{format_time(cd)}**.",
                ephemeral=True,
            )
            return

        amount = random.randint(*WEEKLY_AMOUNT)
        u["balance"] += amount
        u["total_earned"] += amount
        u["last_weekly"] = time.time()
        save_data(data)

        embed = discord.Embed(
            title="📅 Weekly Reward Claimed!",
            description=f"Miraculous guardians reward loyalty! Here's your weekly haul.",
            color=0xFF8C00,
        )
        embed.add_field(name="💰 Received", value=format_balance(amount), inline=True)
        embed.add_field(name="👛 New Balance", value=format_balance(u["balance"]), inline=True)
        embed.set_footer(text="Come back next week!")
        await interaction.followup.send(embed=embed)

    @eco_group.command(name="work", description="Do some work and earn Miraculons!")
    async def work(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        u = get_user(data, str(interaction.user.id))

        cd = cooldown_remaining(u["last_work"], COOLDOWNS["work"])
        if cd > 0:
            await interaction.followup.send(
                f"⏳ You're tired from your last job! Rest for **{format_time(cd)}**.",
                ephemeral=True,
            )
            return

        amount = random.randint(*WORK_AMOUNT)
        doubled = has_effect(u, "double_work")
        if doubled:
            consume_effect(u, "double_work")
            amount *= 2

        u["balance"] += amount
        u["total_earned"] += amount
        u["last_work"] = time.time()
        save_data(data)

        job = random.choice(WORK_MESSAGES)
        embed = discord.Embed(
            title="💼 Work Complete!",
            description=job,
            color=0x44CC88,
        )
        embed.add_field(name="💰 Earned", value=format_balance(amount), inline=True)
        embed.add_field(name="👛 New Balance", value=format_balance(u["balance"]), inline=True)
        if doubled:
            embed.add_field(name="🐱 Bonus", value="Cat Noir Badge doubled your pay!", inline=False)
        embed.set_footer(text=f"Work again in {format_time(COOLDOWNS['work'])}")
        await interaction.followup.send(embed=embed)

    @eco_group.command(name="crime", description="Commit a risky crime for a big payout — or a fine!")
    async def crime(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        u = get_user(data, str(interaction.user.id))

        cd = cooldown_remaining(u["last_crime"], COOLDOWNS["crime"])
        if cd > 0:
            await interaction.followup.send(
                f"⏳ Laying low after your last scheme! Try again in **{format_time(cd)}**.",
                ephemeral=True,
            )
            return

        u["last_crime"] = time.time()
        success = random.random() < 0.5

        if success:
            amount = random.randint(*CRIME_AMOUNT)
            u["balance"] += amount
            u["total_earned"] += amount
            save_data(data)
            msg = random.choice(CRIME_WIN_MESSAGES)
            embed = discord.Embed(title="🦹 Crime Successful!", description=msg, color=0x6A0DAD)
            embed.add_field(name="💰 Stolen", value=format_balance(amount), inline=True)
            embed.add_field(name="👛 New Balance", value=format_balance(u["balance"]), inline=True)
        else:
            fine = random.randint(*CRIME_FINE)
            fine = min(fine, u["balance"])
            u["balance"] -= fine
            u["total_spent"] += fine
            save_data(data)
            msg = random.choice(CRIME_FAIL_MESSAGES)
            embed = discord.Embed(title="🚔 Caught Red-Handed!", description=msg, color=0xFF4444)
            embed.add_field(name="💸 Fine Paid", value=format_balance(fine), inline=True)
            embed.add_field(name="👛 New Balance", value=format_balance(u["balance"]), inline=True)

        embed.set_footer(text=f"Crime again in {format_time(COOLDOWNS['crime'])}")
        await interaction.followup.send(embed=embed)

    @eco_group.command(name="gamble", description="Gamble your Miraculons — double or nothing!")
    @app_commands.describe(amount="Amount to gamble (or 'all')")
    async def gamble(self, interaction: discord.Interaction, amount: str):
        await interaction.response.defer()
        data = load_data()
        u = get_user(data, str(interaction.user.id))

        if amount.lower() == "all":
            bet = u["balance"]
        else:
            try:
                bet = int(amount)
            except ValueError:
                await interaction.followup.send(
                    "❌ Invalid amount. Use a number or `all`.", ephemeral=True
                )
                return

        if bet < GAMBLE_MIN:
            await interaction.followup.send(
                f"❌ Minimum gamble is {CURRENCY_EMOJI} **{GAMBLE_MIN}** {CURRENCY}.", ephemeral=True
            )
            return
        if bet > u["balance"]:
            await interaction.followup.send(
                f"❌ You only have {format_balance(u['balance'])}!", ephemeral=True
            )
            return

        win_chance = 0.45
        cataclysm = has_effect(u, "double_gamble")
        lucky = has_effect(u, "lucky_gamble")

        if lucky:
            win_chance = 0.60
            consume_effect(u, "lucky_gamble")
        if cataclysm:
            consume_effect(u, "double_gamble")

        won = random.random() < win_chance
        winnings = bet * 2 if (won and cataclysm) else bet

        if won:
            u["balance"] += winnings
            u["total_earned"] += winnings
            color = 0xFFD700
            title = "🎰 You Won!"
            result_text = f"+{format_balance(winnings)}"
        else:
            u["balance"] -= bet
            u["total_spent"] += bet
            color = 0xFF4444
            title = "🎰 You Lost!"
            result_text = f"-{format_balance(bet)}"

        save_data(data)

        outcomes = ["🍒 Cherry", "🍋 Lemon", "🐞 Ladybug", "🐱 Cat Noir", "⭐ Star", "🦋 Butterfly"]
        slot1, slot2, slot3 = random.choices(outcomes, k=3)
        slots_display = f"{slot1} | {slot2} | {slot3}"

        embed = discord.Embed(title=title, color=color)
        embed.add_field(name="🎰 Slots", value=slots_display, inline=False)
        embed.add_field(name="💸 Bet", value=format_balance(bet), inline=True)
        embed.add_field(name="📊 Result", value=result_text, inline=True)
        embed.add_field(name="👛 New Balance", value=format_balance(u["balance"]), inline=True)
        if cataclysm and won:
            embed.add_field(name="⚫ Cataclysm Coin", value="Doubled your winnings!", inline=False)
        if lucky:
            embed.add_field(name="🍀 Lucky Charm", value=f"Win chance boosted to 60%!", inline=False)
        await interaction.followup.send(embed=embed)

    @eco_group.command(name="rob", description="Try to rob another member's wallet!")
    @app_commands.describe(user="The person to rob")
    async def rob(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer()
        if user.bot:
            await interaction.followup.send("❌ You can't rob a bot!", ephemeral=True)
            return
        if user.id == interaction.user.id:
            await interaction.followup.send("❌ You can't rob yourself!", ephemeral=True)
            return

        data = load_data()
        robber = get_user(data, str(interaction.user.id))
        victim = get_user(data, str(user.id))

        cd = cooldown_remaining(robber["last_rob"], COOLDOWNS["rob"])
        if cd > 0:
            await interaction.followup.send(
                f"⏳ You're still wanted! Lay low for **{format_time(cd)}**.", ephemeral=True
            )
            return

        if victim["balance"] < ROB_MIN_BALANCE:
            await interaction.followup.send(
                f"❌ {user.display_name} is too broke to rob! They have less than "
                f"{CURRENCY_EMOJI} {ROB_MIN_BALANCE} {CURRENCY}.",
                ephemeral=True,
            )
            return

        robber["last_rob"] = time.time()
        success = random.random() < ROB_SUCCESS_CHANCE

        if success:
            pct = random.uniform(*ROB_AMOUNT_RANGE)
            stolen = int(victim["balance"] * pct)
            stolen = max(50, stolen)
            victim["balance"] -= stolen
            robber["balance"] += stolen
            robber["total_earned"] += stolen
            save_data(data)

            embed = discord.Embed(
                title="🦹 Successful Heist!",
                description=f"You snuck into {user.mention}'s wallet while Ladybug was distracted!",
                color=0x6A0DAD,
            )
            embed.add_field(name="💰 Stolen", value=format_balance(stolen), inline=True)
            embed.add_field(name="👛 Your Balance", value=format_balance(robber["balance"]), inline=True)
        else:
            fine = random.randint(*ROB_FINE_RANGE)
            fine = min(fine, robber["balance"])
            robber["balance"] -= fine
            robber["total_spent"] += fine
            save_data(data)

            embed = discord.Embed(
                title="🚔 Caught by Ladybug!",
                description=f"You tried to rob {user.mention} but got caught and fined!",
                color=0xFF4444,
            )
            embed.add_field(name="💸 Fine Paid", value=format_balance(fine), inline=True)
            embed.add_field(name="👛 Your Balance", value=format_balance(robber["balance"]), inline=True)

        embed.set_footer(text=f"Rob again in {format_time(COOLDOWNS['rob'])}")
        await interaction.followup.send(embed=embed)

    @eco_group.command(name="pay", description="Send Miraculons to another member.")
    @app_commands.describe(user="Who to pay", amount="How many Miraculons to send")
    async def pay(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        await interaction.response.defer()
        if user.bot:
            await interaction.followup.send("❌ You can't pay a bot!", ephemeral=True)
            return
        if user.id == interaction.user.id:
            await interaction.followup.send("❌ You can't pay yourself!", ephemeral=True)
            return
        if amount <= 0:
            await interaction.followup.send("❌ Amount must be positive!", ephemeral=True)
            return

        data = load_data()
        sender = get_user(data, str(interaction.user.id))

        if sender["balance"] < amount:
            await interaction.followup.send(
                f"❌ You don't have enough! You have {format_balance(sender['balance'])}.",
                ephemeral=True,
            )
            return

        receiver = get_user(data, str(user.id))
        sender["balance"] -= amount
        sender["total_spent"] += amount
        receiver["balance"] += amount
        receiver["total_earned"] += amount
        save_data(data)

        embed = discord.Embed(
            title="💸 Payment Sent!",
            color=0x44CC88,
        )
        embed.add_field(name="📤 Sent", value=format_balance(amount), inline=True)
        embed.add_field(name="📥 To", value=user.mention, inline=True)
        embed.add_field(name="👛 Your Balance", value=format_balance(sender["balance"]), inline=True)
        await interaction.followup.send(embed=embed)

    @eco_group.command(name="leaderboard", description="See the richest members in the server!")
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()

        member_ids = {str(m.id) for m in interaction.guild.members}
        entries = [
            (uid, udata["balance"])
            for uid, udata in data["users"].items()
            if uid in member_ids
        ]
        entries.sort(key=lambda x: x[1], reverse=True)
        top = entries[:10]

        embed = discord.Embed(
            title=f"{CURRENCY_EMOJI} Miraculous Wealth Leaderboard",
            color=0xFFD700,
        )

        medals = ["🥇", "🥈", "🥉"]
        lines = []
        for i, (uid, bal) in enumerate(top):
            medal = medals[i] if i < 3 else f"`#{i + 1}`"
            member = interaction.guild.get_member(int(uid))
            name = member.display_name if member else f"<@{uid}>"
            lines.append(f"{medal} **{name}** — {CURRENCY_EMOJI} {bal:,}")

        embed.description = "\n".join(lines) if lines else "No data yet — use `/economy daily` to start!"

        user_id = str(interaction.user.id)
        if user_id in data["users"]:
            rank = next((i + 1 for i, (uid, _) in enumerate(entries) if uid == user_id), None)
            if rank:
                embed.set_footer(text=f"Your rank: #{rank} of {len(entries)} members")

        await interaction.followup.send(embed=embed)

    @eco_group.command(name="shop", description="Browse the Miraculous item shop!")
    async def shop(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = discord.Embed(
            title="🛍️ Miraculous Item Shop",
            description="Use `/economy buy [item name]` to purchase an item!",
            color=0xFF69B4,
        )
        for item_id, item in SHOP_ITEMS.items():
            embed.add_field(
                name=f"{item['emoji']} {item['name']} — {CURRENCY_EMOJI} {item['price']:,}",
                value=item["description"],
                inline=False,
            )
        embed.set_footer(text="Usable items activate automatically when you use the matching command.")
        await interaction.followup.send(embed=embed)

    @eco_group.command(name="buy", description="Buy an item from the Miraculous shop!")
    @app_commands.describe(item="Item name to buy")
    async def buy(self, interaction: discord.Interaction, item: str):
        await interaction.response.defer()
        item_id = item.lower().replace(" ", "_")
        if item_id not in SHOP_ITEMS:
            names = ", ".join(f"`{i['name']}`" for i in SHOP_ITEMS.values())
            await interaction.followup.send(
                f"❌ Item not found! Available items: {names}", ephemeral=True
            )
            return

        shop_item = SHOP_ITEMS[item_id]
        data = load_data()
        u = get_user(data, str(interaction.user.id))

        if u["balance"] < shop_item["price"]:
            await interaction.followup.send(
                f"❌ You need {format_balance(shop_item['price'])} but only have {format_balance(u['balance'])}.",
                ephemeral=True,
            )
            return

        u["balance"] -= shop_item["price"]
        u["total_spent"] += shop_item["price"]
        u["inventory"].append(item_id)

        if shop_item.get("usable") and shop_item.get("effect"):
            u["active_effects"].append(shop_item["effect"])

        save_data(data)

        embed = discord.Embed(
            title=f"✅ Purchased {shop_item['emoji']} {shop_item['name']}!",
            description=shop_item["description"],
            color=0x44CC88,
        )
        embed.add_field(name="💸 Paid", value=format_balance(shop_item["price"]), inline=True)
        embed.add_field(name="👛 Remaining", value=format_balance(u["balance"]), inline=True)
        if shop_item.get("usable"):
            embed.add_field(
                name="⚡ Effect Ready",
                value="This item's bonus will activate automatically next time you use the matching command!",
                inline=False,
            )
        await interaction.followup.send(embed=embed)

    @buy.autocomplete("item")
    async def buy_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=f"{i['emoji']} {i['name']} ({CURRENCY_EMOJI} {i['price']:,})", value=i["name"])
            for i in SHOP_ITEMS.values()
            if current.lower() in i["name"].lower()
        ][:25]

    @eco_group.command(name="inventory", description="View your Miraculous item inventory.")
    async def inventory(self, interaction: discord.Interaction):
        await interaction.response.defer()
        data = load_data()
        u = get_user(data, str(interaction.user.id))
        save_data(data)

        items = u.get("inventory", [])
        effects = u.get("active_effects", [])

        embed = discord.Embed(
            title=f"🎒 {interaction.user.display_name}'s Inventory",
            color=0xFF69B4,
        )
        if not items:
            embed.description = "Your inventory is empty! Visit `/economy shop` to browse items."
        else:
            from collections import Counter
            counts = Counter(items)
            lines = []
            for item_id, count in counts.items():
                if item_id in SHOP_ITEMS:
                    si = SHOP_ITEMS[item_id]
                    lines.append(f"{si['emoji']} **{si['name']}** x{count}")
            embed.description = "\n".join(lines)

        if effects:
            embed.add_field(
                name="⚡ Active Effects",
                value="\n".join(f"• `{e}`" for e in effects),
                inline=False,
            )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)

    @eco_group.command(name="give", description="Give Miraculons to a user. (Admin only)")
    @app_commands.describe(user="Target user", amount="Amount to give")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def admin_give(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        await interaction.response.defer()
        if amount <= 0:
            await interaction.followup.send("❌ Amount must be positive.", ephemeral=True)
            return
        data = load_data()
        u = get_user(data, str(user.id))
        u["balance"] += amount
        u["total_earned"] += amount
        save_data(data)
        await interaction.followup.send(
            f"✅ Gave {format_balance(amount)} to {user.mention}. New balance: {format_balance(u['balance'])}.",
            ephemeral=True,
        )

    @eco_group.command(name="take", description="Take Miraculons from a user. (Admin only)")
    @app_commands.describe(user="Target user", amount="Amount to take")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def admin_take(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        await interaction.response.defer()
        if amount <= 0:
            await interaction.followup.send("❌ Amount must be positive.", ephemeral=True)
            return
        data = load_data()
        u = get_user(data, str(user.id))
        taken = min(amount, u["balance"])
        u["balance"] -= taken
        save_data(data)
        await interaction.followup.send(
            f"✅ Took {format_balance(taken)} from {user.mention}. New balance: {format_balance(u['balance'])}.",
            ephemeral=True,
        )

    @eco_group.command(name="reset", description="Reset a user's economy data. (Admin only)")
    @app_commands.describe(user="User to reset")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def admin_reset(self, interaction: discord.Interaction, user: discord.Member):
        await interaction.response.defer()
        data = load_data()
        if str(user.id) in data["users"]:
            del data["users"][str(user.id)]
            save_data(data)
        await interaction.followup.send(
            f"✅ Reset economy data for {user.mention}.", ephemeral=True
        )

    @admin_give.error
    @admin_take.error
    @admin_reset.error
    async def admin_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.followup.send(
                "❌ You need the **Manage Server** permission for admin economy commands.",
                ephemeral=True,
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(EconomyCog(bot))
