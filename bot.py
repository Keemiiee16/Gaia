import discord
from discord import app_commands
from discord.ext import commands
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
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_user(data, user_id):
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


class ConfirmCharacterView(discord.ui.View):
    def __init__(self, character_data):
        super().__init__(timeout=60)
        self.character_data = character_data

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        user_id = str(interaction.user.id)
        u = get_user(data, user_id)

        key = self.character_data["name"].lower()
        u["characters"][key] = self.character_data

        save_data(data)

        await interaction.response.edit_message(
            content=f"✅ Character **{self.character_data['name']}** created!",
            view=None
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="❌ Character creation cancelled.",
            view=None
        )


class CharacterCreateModal(discord.ui.Modal, title="Create Character"):
    name = discord.ui.TextInput(label="Name", placeholder="Emmy Nelson", required=True)
    age = discord.ui.TextInput(label="Age", placeholder="17", required=True)
    gender = discord.ui.TextInput(label="Gender", placeholder="Female / Male / Nonbinary / etc", required=True)
    genre = discord.ui.TextInput(label="Genre", placeholder="school, celebrity, fantasy, medical, etc", required=True)
    notes = discord.ui.TextInput(label="Notes", placeholder="Personality, family, secrets, etc", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        character_data = {
            "name": str(self.name),
            "age": str(self.age),
            "gender": str(self.gender),
            "genre": str(self.genre),
            "notes": str(self.notes)
        }

        msg = (
            f"Create this character?\n\n"
            f"**Name:** {character_data['name']}\n"
            f"**Age:** {character_data['age']}\n"
            f"**Gender:** {character_data['gender']}\n"
            f"**Genre:** {character_data['genre']}\n"
            f"**Notes:** {character_data['notes'] or 'None'}"
        )

        await interaction.response.send_message(
            msg,
            view=ConfirmCharacterView(character_data),
            ephemeral=True
        )


character_group = app_commands.Group(name="character", description="Character commands")
baby_group = app_commands.Group(name="baby", description="Baby commands")
parent_group = app_commands.Group(name="parent", description="Parent commands")
event_group = app_commands.Group(name="event", description="Event commands")
reaction_group = app_commands.Group(name="reaction", description="Reaction commands")
timeline_group = app_commands.Group(name="timeline", description="Timeline commands")


@character_group.command(name="create", description="Create a character with a questionnaire")
async def character_create(interaction: discord.Interaction):
    await interaction.response.send_modal(CharacterCreateModal())


@character_group.command(name="list", description="List your characters")
async def character_list(interaction: discord.Interaction):
    data = load_data()
    u = get_user(data, str(interaction.user.id))

    if not u["characters"]:
        await interaction.response.send_message("You have no characters yet.", ephemeral=True)
        return

    msg = "\n".join([
        f"- **{c['name']}** | Age: {c['age']} | Gender: {c['gender']} | Genre: {c['genre']}"
        for c in u["characters"].values()
    ])

    await interaction.response.send_message(f"**Your Characters:**\n{msg}")


@character_group.command(name="profile", description="View a character profile")
async def character_profile(interaction: discord.Interaction, name: str):
    data = load_data()
    u = get_user(data, str(interaction.user.id))
    char = u["characters"].get(name.lower())

    if not char:
        await interaction.response.send_message("Character not found.", ephemeral=True)
        return

    await interaction.response.send_message(
        f"**{char['name']}**\n"
        f"Age: {char['age']}\n"
        f"Gender: {char['gender']}\n"
        f"Genre: {char['genre']}\n"
        f"Notes: {char.get('notes', 'None')}"
    )


@character_group.command(name="delete", description="Delete a character")
async def character_delete(interaction: discord.Interaction, name: str):
    data = load_data()
    u = get_user(data, str(interaction.user.id))

    if name.lower() not in u["characters"]:
        await interaction.response.send_message("Character not found.", ephemeral=True)
        return

    del u["characters"][name.lower()]
    save_data(data)
    await interaction.response.send_message(f"🗑️ Deleted **{name}**.")


@baby_group.command(name="create", description="Create a baby with hidden temperament")
async def baby_create(interaction: discord.Interaction, name: str, age: str = "newborn", parent: str = "unknown"):
    data = load_data()
    u = get_user(data, str(interaction.user.id))

    temperament = random.choice(temperaments)

    u["babies"][name.lower()] = {
        "name": name,
        "age": age,
        "parent": parent,
        "temperament": temperament,
        "revealed": False
    }

    save_data(data)

    await interaction.response.send_message(
        f"👶 Baby **{name}** created.\n"
        f"Age: **{age}**\n"
        f"Parent: **{parent}**\n"
        f"Temperament: **Hidden**"
    )


@baby_group.command(name="event", description="Generate a random baby event")
async def baby_event(interaction: discord.Interaction, name: str):
    data = load_data()
    u = get_user(data, str(interaction.user.id))
    baby = u["babies"].get(name.lower())

    if not baby:
        await interaction.response.send_message("Baby not found.", ephemeral=True)
        return

    temp = baby["temperament"]
    result = random.choice(baby_events[temp])

    await interaction.response.send_message(
        f"**{baby['name']}**\n\n{result}"
    )


@baby_group.command(name="reveal", description="Reveal a baby's hidden temperament")
async def baby_reveal(interaction: discord.Interaction, name: str):
    data = load_data()
    u = get_user(data, str(interaction.user.id))
    baby = u["babies"].get(name.lower())

    if not baby:
        await interaction.response.send_message("Baby not found.", ephemeral=True)
        return

    baby["revealed"] = True
    save_data(data)

    await interaction.response.send_message(
        f"👀 **{baby['name']}** temperament is **{baby['temperament']}**."
    )


@baby_group.command(name="profile", description="View baby profile")
async def baby_profile(interaction: discord.Interaction, name: str):
    data = load_data()
    u = get_user(data, str(interaction.user.id))
    baby = u["babies"].get(name.lower())

    if not baby:
        await interaction.response.send_message("Baby not found.", ephemeral=True)
        return

    temperament = baby["temperament"] if baby.get("revealed") else "Hidden"

    await interaction.response.send_message(
        f"**{baby['name']}**\n"
        f"Age: {baby['age']}\n"
        f"Parent: {baby['parent']}\n"
        f"Temperament: {temperament}"
    )


@baby_group.command(name="list", description="List your babies")
async def baby_list(interaction: discord.Interaction):
    data = load_data()
    u = get_user(data, str(interaction.user.id))

    if not u["babies"]:
        await interaction.response.send_message("You have no babies created.", ephemeral=True)
        return

    msg = "\n".join([
        f"- **{b['name']}** | Age: {b['age']} | Parent: {b['parent']}"
        for b in u["babies"].values()
    ])

    await interaction.response.send_message(f"**Your Babies:**\n{msg}")


@parent_group.command(name="add", description="Add a parent or guardian")
async def parent_add(interaction: discord.Interaction, character: str, parent_name: str, personality: str = "protective"):
    data = load_data()
    u = get_user(data, str(interaction.user.id))

    u["parents"][parent_name.lower()] = {
        "name": parent_name,
        "character": character,
        "personality": personality
    }

    save_data(data)

    await interaction.response.send_message(
        f"👨‍👩‍👧 Parent **{parent_name}** added for **{character}**.\n"
        f"Personality: **{personality}**"
    )


@parent_group.command(name="list", description="List parents")
async def parent_list(interaction: discord.Interaction):
    data = load_data()
    u = get_user(data, str(interaction.user.id))

    if not u["parents"]:
        await interaction.response.send_message("No parents added yet.", ephemeral=True)
        return

    msg = "\n".join([
        f"- **{p['name']}** for **{p['character']}** | {p['personality']}"
        for p in u["parents"].values()
    ])

    await interaction.response.send_message(f"**Parents:**\n{msg}")


@event_group.command(name="generate", description="Generate a life RP event")
@app_commands.choices(category=[
    app_commands.Choice(name="School", value="school"),
    app_commands.Choice(name="Celebrity", value="celebrity"),
    app_commands.Choice(name="Medical", value="medical"),
    app_commands.Choice(name="Relationship", value="relationship"),
    app_commands.Choice(name="Family", value="family"),
    app_commands.Choice(name="Public", value="public")
])
async def event_generate(interaction: discord.Interaction, category: app_commands.Choice[str]):
    result = random.choice(events[category.value])
    await interaction.response.send_message(
        f"**{category.name} Event:**\n{result}"
    )


@reaction_group.command(name="generate", description="Generate an NPC reaction")
@app_commands.choices(type=[
    app_commands.Choice(name="Random", value="random"),
    app_commands.Choice(name="Parent", value="parent"),
    app_commands.Choice(name="Partner", value="partner"),
    app_commands.Choice(name="Fan", value="fan"),
    app_commands.Choice(name="Doctor", value="doctor")
])
async def reaction_generate(interaction: discord.Interaction, type: app_commands.Choice[str]):
    result = random.choice(reactions[type.value])
    await interaction.response.send_message(
        f"**{type.name} Reaction:**\n{result}"
    )


@timeline_group.command(name="add", description="Add something to timeline")
async def timeline_add(interaction: discord.Interaction, note: str):
    data = load_data()
    u = get_user(data, str(interaction.user.id))

    u["timeline"].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "note": note
    })

    save_data(data)

    await interaction.response.send_message("✅ Added to timeline.")


@timeline_group.command(name="view", description="View timeline")
async def timeline_view(interaction: discord.Interaction):
    data = load_data()
    u = get_user(data, str(interaction.user.id))

    if not u["timeline"]:
        await interaction.response.send_message("Timeline is empty.", ephemeral=True)
        return

    msg = "\n".join([
        f"- {t['date']}: {t['note']}"
        for t in u["timeline"][-10:]
    ])

    await interaction.response.send_message(f"**Timeline:**\n{msg}")


bot.tree.add_command(character_group)
bot.tree.add_command(baby_group)
bot.tree.add_command(parent_group)
bot.tree.add_command(event_group)
bot.tree.add_command(reaction_group)
bot.tree.add_command(timeline_group)


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Logged in as {bot.user}")
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Sync failed: {e}")


bot.run(TOKEN)