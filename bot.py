
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os
import json
import random
from datetime import datetime

# ============================================
# CONFIG
# ============================================

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ============================================
# JSON FILES
# ============================================

FILES = {
    "characters": "characters.json",
    "babies": "babies.json",
    "pregnancies": "pregnancies.json",
    "relationships": "relationships.json",
    "timelines": "timelines.json",
    "settings": "settings.json"
}

# ============================================
# HELPERS
# ============================================

def load_data(file_name):
    try:
        with open(FILES[file_name], "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(file_name, data):
    with open(FILES[file_name], "w") as f:
        json.dump(data, f, indent=4)

def add_timeline(user_id, text, category="general"):
    data = load_data("timelines")

    if str(user_id) not in data:
        data[str(user_id)] = []

    data[str(user_id)].append({
        "text": text,
        "category": category,
        "time": str(datetime.now())
    })

    save_data("timelines", data)

# ============================================
# RANDOM EVENTS
# ============================================

REACTIONS = [
    "looks shocked",
    "starts crying",
    "gets angry",
    "offers support",
    "panics immediately",
    "stays quiet",
    "starts arguing"
]

PREGNANCY_EVENTS = [
    "Morning sickness hits unexpectedly.",
    "Someone notices the pregnancy bump.",
    "A rumor spreads around school.",
    "A parent becomes suspicious.",
    "A craving becomes overwhelming."
]

PREGNANCY_COMPLICATIONS = [
    "fainting episode",
    "false labor",
    "hospital scare",
    "stress complication",
    "early contractions"
]

BABY_EVENTS = [
    "The baby refuses to sleep.",
    "The baby starts crying loudly.",
    "The baby throws food everywhere.",
    "The baby laughs uncontrollably."
]

RELATIONSHIP_EVENTS = [
    "A jealous argument starts.",
    "A secret gets exposed.",
    "Someone storms out crying.",
    "Someone confesses their feelings."
]

SCHOOL_EVENTS = [
    "A rumor spreads through the hallway.",
    "Someone gets detention.",
    "A fight almost breaks out.",
    "A teacher catches someone skipping."
]

CELEBRITY_EVENTS = [
    "A paparazzi photo goes viral.",
    "Fans start a rumor online.",
    "A livestream clip spreads everywhere."
]

# ============================================
# READY EVENT
# ============================================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

# ============================================
# CHARACTER SYSTEM
# ============================================

@bot.tree.command(name="character_create")
async def character_create(interaction: discord.Interaction, name: str, age: int):
    data = load_data("characters")
    uid = str(interaction.user.id)

    if uid not in data:
        data[uid] = {}

    cid = f"char_{random.randint(1000,9999)}"

    data[uid][cid] = {
        "name": name,
        "age": age,
        "created": str(datetime.now())
    }

    save_data("characters", data)

    add_timeline(interaction.user.id, f"Created character {name}", "character")

    await interaction.response.send_message(f"Character {name} created.")

@bot.tree.command(name="character_list")
async def character_list(interaction: discord.Interaction):
    data = load_data("characters")
    uid = str(interaction.user.id)

    if uid not in data:
        await interaction.response.send_message("No characters found.")
        return

    output = []

    for cid, info in data[uid].items():
        output.append(f"{info['name']} ({info['age']})")

    await interaction.response.send_message("\n".join(output))

# ============================================
# BABY SYSTEM
# ============================================

@bot.tree.command(name="baby_create")
async def baby_create(interaction: discord.Interaction, name: str):
    data = load_data("babies")
    uid = str(interaction.user.id)

    if uid not in data:
        data[uid] = {}

    bid = f"baby_{random.randint(1000,9999)}"

    data[uid][bid] = {
        "name": name,
        "age": 0,
        "temperament": random.choice([
            "calm",
            "chaotic",
            "clingy",
            "playful",
            "shy"
        ])
    }

    save_data("babies", data)

    await interaction.response.send_message(f"Baby {name} created.")

@bot.tree.command(name="baby_event")
async def baby_event(interaction: discord.Interaction):
    event = random.choice(BABY_EVENTS)

    add_timeline(interaction.user.id, event, "baby")

    await interaction.response.send_message(event)

# ============================================
# PREGNANCY SYSTEM
# ============================================

@bot.tree.command(name="pregnancy_create")
async def pregnancy_create(interaction: discord.Interaction, character: str, partner: str):
    data = load_data("pregnancies")
    uid = str(interaction.user.id)

    if uid not in data:
        data[uid] = {}

    pid = f"preg_{random.randint(1000,9999)}"

    data[uid][pid] = {
        "character": character,
        "partner": partner,
        "weeks": 1,
        "days": 0,
        "hidden": False,
        "created": str(datetime.now())
    }

    save_data("pregnancies", data)

    add_timeline(interaction.user.id, f"{character} started a pregnancy storyline.", "pregnancy")

    await interaction.response.send_message(f"Pregnancy created for {character}.")

@bot.tree.command(name="pregnancy_event")
async def pregnancy_event(interaction: discord.Interaction):
    event = random.choice(PREGNANCY_EVENTS)
    reaction = random.choice(REACTIONS)

    add_timeline(interaction.user.id, event, "pregnancy")

    await interaction.response.send_message(
        f"Event: {event}\nReaction: {reaction}"
    )

@bot.tree.command(name="pregnancy_complication")
async def pregnancy_complication(interaction: discord.Interaction):
    complication = random.choice(PREGNANCY_COMPLICATIONS)
    reaction = random.choice(REACTIONS)

    add_timeline(interaction.user.id, complication, "medical")

    await interaction.response.send_message(
        f"Complication: {complication}\nReaction: {reaction}"
    )

# ============================================
# RELATIONSHIP SYSTEM
# ============================================

@bot.tree.command(name="relationship_event")
async def relationship_event(interaction: discord.Interaction):
    event = random.choice(RELATIONSHIP_EVENTS)

    add_timeline(interaction.user.id, event, "relationship")

    await interaction.response.send_message(event)

# ============================================
# SCHOOL SYSTEM
# ============================================

@bot.tree.command(name="school_event")
async def school_event(interaction: discord.Interaction):
    event = random.choice(SCHOOL_EVENTS)

    add_timeline(interaction.user.id, event, "school")

    await interaction.response.send_message(event)

# ============================================
# CELEBRITY SYSTEM
# ============================================

@bot.tree.command(name="celebrity_event")
async def celebrity_event(interaction: discord.Interaction):
    event = random.choice(CELEBRITY_EVENTS)

    add_timeline(interaction.user.id, event, "celebrity")

    await interaction.response.send_message(event)

# ============================================
# REACTION SYSTEM
# ============================================

@bot.tree.command(name="reaction_random")
async def reaction_random(interaction: discord.Interaction):
    reaction = random.choice(REACTIONS)

    await interaction.response.send_message(reaction)

# ============================================
# TIMELINE SYSTEM
# ============================================

@bot.tree.command(name="timeline_view")
async def timeline_view(interaction: discord.Interaction):
    data = load_data("timelines")
    uid = str(interaction.user.id)

    if uid not in data:
        await interaction.response.send_message("Timeline empty.")
        return

    entries = data[uid][-10:]

    output = []

    for entry in entries:
        output.append(f"[{entry['category']}] {entry['text']}")

    await interaction.response.send_message("\n".join(output))

# ============================================
# SETTINGS SYSTEM
# ============================================

@bot.tree.command(name="settings_chaos")
async def settings_chaos(interaction: discord.Interaction, level: str):
    data = load_data("settings")
    uid = str(interaction.user.id)

    if uid not in data:
        data[uid] = {}

    data[uid]["chaos"] = level

    save_data("settings", data)

    await interaction.response.send_message(f"Chaos set to {level}")

@bot.tree.command(name="settings_realism")
async def settings_realism(interaction: discord.Interaction, level: str):
    data = load_data("settings")
    uid = str(interaction.user.id)

    if uid not in data:
        data[uid] = {}

    data[uid]["realism"] = level

    save_data("settings", data)

    await interaction.response.send_message(f"Realism set to {level}")

# ============================================
# GENERATION SYSTEM
# ============================================

@bot.tree.command(name="generate_drama")
async def generate_drama(interaction: discord.Interaction):
    drama = random.choice([
        "A private text gets leaked.",
        "Someone overhears a secret conversation.",
        "An argument explodes publicly.",
        "A relationship starts falling apart."
    ])

    await interaction.response.send_message(drama)

# ============================================
# START BOT
# ============================================

bot.run(TOKEN)
