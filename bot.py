import discord
from discord.ext import commands
from discord import app_commands
import os, json, random
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data.json"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def user_data(data, user_id):
    data.setdefault(user_id, {
        "characters": {},
        "babies": {},
        "parents": {},
        "timeline": []
    })
    return data[user_id]

temperaments = [
    "calm", "fussy", "clingy", "dramatic", "sleepy",
    "curious", "playful", "sensitive", "stubborn", "easygoing"
]

baby_events = {
    "calm": [
        "The baby gives a soft whimper, face scrunching slightly. They seem hungry but not too upset yet.",
        "The baby wiggles quietly and blinks slowly, clearly starting to get sleepy."
    ],
    "fussy": [
        "The baby starts crying hard, face scrunched up and little legs kicking. They might be hungry, gassy, or uncomfortable.",
        "The baby fusses loudly and refuses to settle. Something is definitely bothering them."
    ],
    "clingy": [
        "The baby starts whining the second they are put down, reaching out like they want to be held.",
        "The baby cries softly and turns toward the nearest person, clearly wanting comfort."
    ],
    "dramatic": [
        "The baby gives one tiny warning whine… then completely loses it like the world ended.",
        "The baby’s face scrunches up before they burst into loud crying, demanding attention immediately."
    ],
    "sleepy": [
        "The baby rubs their face and whines, fighting sleep even though they are clearly tired.",
        "The baby gets cranky out of nowhere, fussing because they are overtired."
    ],
    "curious": [
        "The baby stares around, reaches for something nearby, then fusses when they cannot grab it.",
        "The baby gets distracted for a moment, then suddenly whines again."
    ],
    "playful": [
        "The baby babbles happily, then fusses when nobody keeps playing with them.",
        "The baby kicks their legs and makes little noises, clearly wanting attention."
    ],
    "sensitive": [
        "The baby startles at a sound and begins crying, clearly overwhelmed.",
        "The baby’s lip trembles before they start crying softly, needing gentle comfort."
    ],
    "stubborn": [
        "The baby fusses and turns away, refusing to settle even when comforted.",
        "The baby cries with determination, clearly unhappy and not easy to distract."
    ],
    "easygoing": [
        "The baby makes a few tiny noises, calmly letting everyone know they need something.",
        "The baby wiggles around and gives a small whine but stays mostly calm."
    ]
}

events = {
    "school": [
        "A rumor starts spreading in the hallway, and people keep looking over like they know something.",
        "A teacher notices the character acting different and quietly pulls them aside after class.",
        "Someone catches the character looking upset during lunch and asks what happened."
    ],
    "celebrity": [
        "A fan gets way too close and starts asking personal questions they should not know.",
        "Someone nearby starts recording, hoping the moment goes viral.",
        "A paparazzi camera flashes at the worst possible time."
    ],
    "medical": [
        "The doctor walks in with a serious expression and asks a few follow-up questions.",
        "The nurse checks vitals, but the pause afterward makes the room feel tense.",
        "The appointment starts normally, but the doctor says they want to run one more test."
    ],
    "relationship": [
        "Their partner notices something is off and quietly asks what is really going on.",
        "A small misunderstanding turns into a tense conversation.",
        "One of them gets jealous but tries very hard not to show it."
    ],
    "family": [
        "A parent notices the character acting strange and starts asking direct questions.",
        "A family member walks in at the worst possible time.",
        "Someone at home notices something they were trying to hide."
    ],
    "public": [
        "A stranger notices something happening and stares a little too long.",
        "The situation gets awkward when someone nearby decides to comment.",
        "A random person tries to help, but makes the moment more chaotic."
    ]
}

reactions = {
    "random": [
        "They freeze for a second, clearly unsure what to say.",
        "They try to stay calm, but their face gives away how worried they are.",
        "They immediately step closer, protective and tense."
    ],
    "parent": [
        "Their parent’s face tightens, voice becoming firm as they ask what is going on.",
        "Their parent softens immediately, more worried than angry.",
        "Their parent crosses their arms, clearly suspicious."
    ],
    "partner": [
        "Their partner goes quiet, watching them carefully before stepping closer.",
        "Their partner tries to act calm but keeps asking if they are okay.",
        "Their partner becomes protective fast, barely hiding their worry."
    ],
    "fan": [
        "The fan gasps and immediately starts whispering to someone nearby.",
        "The fan pulls out their phone, clearly tempted to record.",
        "The fan looks shocked, like they just witnessed something huge."
    ],
    "doctor": [
        "The doctor keeps their voice calm and explains the next steps carefully.",
        "The doctor studies the chart, then asks a few more questions.",
        "The doctor reassures them, but still wants to keep an eye on things."
    ]
}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="character_create", description="Create an RP character")
async def character_create(interaction: discord.Interaction, name: str, age: str, genre: str = "general"):
    data = load_data()
    u = user_data(data, str(interaction.user.id))
    u["characters"][name.lower()] = {
        "name": name,
        "age": age,
        "genre": genre,
        "notes": ""
    }
    save_data(data)
    await interaction.response.send_message(f"Character **{name}** created.")

@bot.tree.command(name="character_list", description="List your characters")
async def character_list(interaction: discord.Interaction):
    data = load_data()
    u = user_data(data, str(interaction.user.id))
    if not u["characters"]:
        await interaction.response.send_message("You have no characters yet.")
        return
    msg = "\n".join([f"- **{c['name']}**, age {c['age']} | {c['genre']}" for c in u["characters"].values()])
    await interaction.response.send_message(msg)

@bot.tree.command(name="baby_create", description="Create a baby with random temperament")
async def baby_create(interaction: discord.Interaction, name: str, age: str = "newborn", parent: str = "unknown"):
    data = load_data()
    u = user_data(data, str(interaction.user.id))
    temperament = random.choice(temperaments)
    u["babies"][name.lower()] = {
        "name": name,
        "age": age,
        "parent": parent,
        "temperament": temperament
    }
    save_data(data)
    await interaction.response.send_message(
        f"Baby **{name}** created.\nAge: **{age}**\nParent: **{parent}**\nTemperament: **{temperament}**"
    )

@bot.tree.command(name="baby_event", description="Generate a random baby event")
async def baby_event(interaction: discord.Interaction, name: str):
    data = load_data()
    u = user_data(data, str(interaction.user.id))
    baby = u["babies"].get(name.lower())
    if not baby:
        await interaction.response.send_message("I couldn’t find that baby.")
        return
    temp = baby["temperament"]
    event = random.choice(baby_events[temp])
    await interaction.response.send_message(f"**{baby['name']}** | temperament: **{temp}**\n\n{event}")

@bot.tree.command(name="parent_add", description="Add a parent/guardian to a character")
async def parent_add(interaction: discord.Interaction, character: str, parent_name: str, personality: str = "protective"):
    data = load_data()
    u = user_data(data, str(interaction.user.id))
    u["parents"][parent_name.lower()] = {
        "name": parent_name,
        "character": character,
        "personality": personality
    }
    save_data(data)
    await interaction.response.send_message(
        f"Parent **{parent_name}** added for **{character}**.\nPersonality: **{personality}**"
    )

@bot.tree.command(name="event", description="Generate a life RP event")
async def event(interaction: discord.Interaction, category: str):
    category = category.lower()
    if category not in events:
        await interaction.response.send_message("Use: school, celebrity, medical, relationship, family, public")
        return
    await interaction.response.send_message(f"**{category.title()} Event:**\n{random.choice(events[category])}")

@bot.tree.command(name="reaction", description="Generate an NPC reaction")
async def reaction(interaction: discord.Interaction, type: str = "random"):
    type = type.lower()
    if type not in reactions:
        await interaction.response.send_message("Use: random, parent, partner, fan, doctor")
        return
    await interaction.response.send_message(f"**{type.title()} Reaction:**\n{random.choice(reactions[type])}")

@bot.tree.command(name="timeline_add", description="Add something to your RP timeline")
async def timeline_add(interaction: discord.Interaction, note: str):
    data = load_data()
    u = user_data(data, str(interaction.user.id))
    u["timeline"].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "note": note
    })
    save_data(data)
    await interaction.response.send_message("Added to timeline.")

@bot.tree.command(name="timeline_view", description="View your RP timeline")
async def timeline_view(interaction: discord.Interaction):
    data = load_data()
    u = user_data(data, str(interaction.user.id))
    if not u["timeline"]:
        await interaction.response.send_message("Your timeline is empty.")
        return
    msg = "\n".join([f"- {t['date']}: {t['note']}" for t in u["timeline"][-10:]])
    await interaction.response.send_message(f"**Timeline:**\n{msg}")

bot.run(TOKEN)