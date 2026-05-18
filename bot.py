import discord
from discord import app_commands
from discord.ext import commands
import os, json, random
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "0"))
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

temperaments = ["calm", "fussy", "clingy", "dramatic", "sleepy", "curious", "playful", "sensitive", "stubborn", "easygoing"]

baby_events = {
    "calm": ["The baby gives a soft whimper, face scrunching slightly. They seem hungry but not too upset yet."],
    "fussy": ["The baby starts crying hard, face scrunched up and little legs kicking. They might be hungry, gassy, or uncomfortable."],
    "clingy": ["The baby starts whining the second they are put down, reaching out like they want to be held."],
    "dramatic": ["The baby gives one tiny warning whine… then completely loses it like the world ended."],
    "sleepy": ["The baby rubs their face and whines, fighting sleep even though they are clearly tired."],
    "curious": ["The baby reaches for something nearby, then fusses when they cannot grab it."],
    "playful": ["The baby babbles happily, then fusses when nobody keeps playing with them."],
    "sensitive": ["The baby startles at a sound and begins crying, clearly overwhelmed."],
    "stubborn": ["The baby fusses and turns away, refusing to settle even when comforted."],
    "easygoing": ["The baby makes a few tiny noises, calmly letting everyone know they need something."]
}

events = {
    "school": ["A rumor starts spreading in the hallway, and people keep looking over like they know something."],
    "celebrity": ["A fan gets way too close and starts asking personal questions they should not know."],
    "medical": ["The doctor walks in with a serious expression and asks a few follow-up questions."],
    "relationship": ["Their partner notices something is off and quietly asks what is really going on."],
    "family": ["A parent notices the character acting strange and starts asking direct questions."],
    "public": ["A stranger notices something happening and stares a little too long."]
}

reactions = {
    "random": ["They freeze for a second, clearly unsure what to say."],
    "parent": ["Their parent’s face tightens, voice becoming firm as they ask what is going on."],
    "partner": ["Their partner goes quiet, watching them carefully before stepping closer."],
    "fan": ["The fan gasps and immediately starts whispering to someone nearby."],
    "doctor": ["The doctor keeps their voice calm and explains the next steps carefully."]
}

class ConfirmCharacterView(discord.ui.View):
    def __init__(self, character_data):
        super().__init__(timeout=60)
        self.character_data = character_data

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        u = get_user(data, str(interaction.user.id))
        u["characters"][self.character_data["name"].lower()] = self.character_data
        save_data(data)

        await interaction.response.edit_message(
            content=f"✅ Character **{self.character_data['name']}** created!",
            view=None
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ Cancelled.", view=None)

class CharacterCreateModal(discord.ui.Modal, title="Create Character"):
    name = discord.ui.TextInput(label="Name", required=True)
    age = discord.ui.TextInput(label="Age", required=True)
    gender = discord.ui.TextInput(label="Gender", required=True)
    genre = discord.ui.TextInput(label="Genre", required=True)
    notes = discord.ui.TextInput(label="Notes", style=discord.TextStyle.paragraph, required=False)

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

        await interaction.response.send_message(msg, view=ConfirmCharacterView(character_data), ephemeral=True)

character_group = app_commands.Group(name="character", description="Character commands")
baby_group = app_commands.Group(name="baby", description="Baby commands")
parent_group = app_commands.Group(name="parent", description="Parent commands")
event_group = app_commands.Group(name="event", description="Event commands")
reaction_group = app_commands.Group(name="reaction", description="Reaction commands")
timeline_group = app_commands.Group(name="timeline", description="Timeline commands")

@character_group.command(name="create", description="Create a character")
async def character_create(interaction: discord.Interaction):
    await interaction.response.send_modal(CharacterCreateModal())

@character_group.command(name="list", description="List your characters")
async def character_list(interaction: discord.Interaction):
    data = load_data()
    u = get_user(data, str(interaction.user.id))

    if not u["characters"]:
        await interaction.response.send_message("You have no characters yet.", ephemeral=True)
        return

    msg = "\n".join([f"- **{c['name']}** | {c['age']} | {c['gender']} | {c['genre']}" for c in u["characters"].values()])
    await interaction.response.send_message(f"**Your Characters:**\n{msg}")

@character_group.command(name="profile", description="View a character")
async def character_profile(interaction: discord.Interaction, name: str):
    data = load_data()
    u = get_user(data, str(interaction.user.id))
    char = u["characters"].get(name.lower())

    if not char:
        await interaction.response.send_message("Character not found.", ephemeral=True)
        return

    await interaction.response.send_message(
        f"**{char['name']}**\nAge: {char['age']}\nGender: {char['gender']}\nGenre: {char['genre']}\nNotes: {char.get('notes', 'None')}"
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

@baby_group.command(name="create", description="Create a baby")
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
    await interaction.response.send_message(f"👶 Baby **{name}** created.\nTemperament: **Hidden**")

@baby_group.command(name="event", description="Generate baby event")
async def baby_event(interaction: discord.Interaction, name: str):
    data = load_data()
    u = get_user(data, str(interaction.user.id))
    baby = u["babies"].get(name.lower())

    if not baby:
        await interaction.response.send_message("Baby not found.", ephemeral=True)
        return

    result = random.choice(baby_events[baby["temperament"]])
    await interaction.response.send_message(f"**{baby['name']}**\n\n{result}")

@baby_group.command(name="reveal", description="Reveal baby temperament")
async def baby_reveal(interaction: discord.Interaction, name: str):
    data = load_data()
    u = get_user(data, str(interaction.user.id))
    baby = u["babies"].get(name.lower())

    if not baby:
        await interaction.response.send_message("Baby not found.", ephemeral=True)
        return

    baby["revealed"] = True
    save_data(data)
    await interaction.response.send_message(f"👀 **{baby['name']}** temperament is **{baby['temperament']}**.")

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
        f"**{baby['name']}**\nAge: {baby['age']}\nParent: {baby['parent']}\nTemperament: {temperament}"
    )

@parent_group.command(name="add", description="Add a parent")
async def parent_add(interaction: discord.Interaction, character: str, parent_name: str, personality: str = "protective"):
    data = load_data()
    u = get_user(data, str(interaction.user.id))

    u["parents"][parent_name.lower()] = {
        "name": parent_name,
        "character": character,
        "personality": personality
    }

    save_data(data)
    await interaction.response.send_message(f"Parent **{parent_name}** added for **{character}**.")

@event_group.command(name="generate", description="Generate RP event")
@app_commands.choices(category=[
    app_commands.Choice(name="School", value="school"),
    app_commands.Choice(name="Celebrity", value="celebrity"),
    app_commands.Choice(name="Medical", value="medical"),
    app_commands.Choice(name="Relationship", value="relationship"),
    app_commands.Choice(name="Family", value="family"),
    app_commands.Choice(name="Public", value="public"),
])
async def event_generate(interaction: discord.Interaction, category: app_commands.Choice[str]):
    await interaction.response.send_message(f"**{category.name} Event:**\n{random.choice(events[category.value])}")

@reaction_group.command(name="generate", description="Generate NPC reaction")
@app_commands.choices(type=[
    app_commands.Choice(name="Random", value="random"),
    app_commands.Choice(name="Parent", value="parent"),
    app_commands.Choice(name="Partner", value="partner"),
    app_commands.Choice(name="Fan", value="fan"),
    app_commands.Choice(name="Doctor", value="doctor"),
])
async def reaction_generate(interaction: discord.Interaction, type: app_commands.Choice[str]):
    await interaction.response.send_message(f"**{type.name} Reaction:**\n{random.choice(reactions[type.value])}")

@timeline_group.command(name="add", description="Add to timeline")
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

    msg = "\n".join([f"- {t['date']}: {t['note']}" for t in u["timeline"][-10:]])
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
        if GUILD_ID:
            guild = discord.Object(id=GUILD_ID)
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"Logged in as {bot.user}")
            print(f"Synced {len(synced)} guild commands")
        else:
            synced = await bot.tree.sync()
            print(f"Logged in as {bot.user}")
            print(f"Synced {len(synced)} global commands")
    except Exception as e:
        print(f"Sync failed: {e}")

bot.run(TOKEN)