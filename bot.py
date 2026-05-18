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
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
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

GENRE_CHOICES = [
    app_commands.Choice(name="School", value="school"),
    app_commands.Choice(name="College", value="college"),
    app_commands.Choice(name="Family", value="family"),
    app_commands.Choice(name="Slice of Life", value="slice_of_life"),
    app_commands.Choice(name="Teen Drama", value="teen_drama"),
    app_commands.Choice(name="Adult Drama", value="adult_drama"),
    app_commands.Choice(name="Romance", value="romance"),
    app_commands.Choice(name="Celebrity", value="celebrity"),
    app_commands.Choice(name="Influencer", value="influencer"),
    app_commands.Choice(name="Medical", value="medical"),
    app_commands.Choice(name="Pregnancy", value="pregnancy"),
    app_commands.Choice(name="Hospital", value="hospital"),
    app_commands.Choice(name="Fantasy", value="fantasy"),
    app_commands.Choice(name="Supernatural", value="supernatural"),
    app_commands.Choice(name="Vampire", value="vampire"),
    app_commands.Choice(name="Werewolf", value="werewolf"),
    app_commands.Choice(name="Witch / Magic", value="magic"),
    app_commands.Choice(name="Royalty", value="royalty"),
    app_commands.Choice(name="Crime", value="crime"),
    app_commands.Choice(name="Mafia", value="mafia"),
    app_commands.Choice(name="Mystery", value="mystery"),
    app_commands.Choice(name="Apocalypse", value="apocalypse"),
    app_commands.Choice(name="Sci-Fi", value="sci_fi"),
    app_commands.Choice(name="Comedy", value="comedy"),
    app_commands.Choice(name="Parenthood", value="parenthood"),
]

temperaments = ["calm", "fussy", "clingy", "dramatic", "sleepy", "curious", "playful", "sensitive", "stubborn", "easygoing"]

baby_events = {
    "calm": ["The baby softly whimpers, face scrunched a little. They seem hungry, but not fully upset yet."],
    "fussy": ["The baby starts crying hard, face scrunched up and little legs kicking. Something is definitely bothering them."],
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
    "family": ["A parent notices the character acting strange and starts asking direct questions."],
    "romance": ["Their partner notices something is off and quietly asks what is really going on."],
    "fantasy": ["Something strange happens nearby, and the air suddenly feels different."],
    "crime": ["Someone shows up with information they definitely should not have."],
    "default": ["Something unexpected happens, and everyone has to react fast."]
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
        super().__init__(timeout=120)
        self.character_data = character_data

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        u = get_user(data, str(interaction.user.id))
        u["characters"][self.character_data["name"].lower()] = self.character_data
        save_data(data)
        await interaction.response.edit_message(content=f"✅ Character **{self.character_data['name']}** created!", view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ Character creation cancelled.", view=None)

class CharacterCreateModal(discord.ui.Modal, title="Create Character"):
    def __init__(self, genre):
        super().__init__()
        self.genre_value = genre

    name = discord.ui.TextInput(label="Name", required=True)
    age = discord.ui.TextInput(label="Age", required=True)
    gender = discord.ui.TextInput(label="Gender", required=True)
    notes = discord.ui.TextInput(label="Notes", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        character_data = {
            "name": str(self.name),
            "age": str(self.age),
            "gender": str(self.gender),
            "genre": self.genre_value,
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
event_group = app_commands.Group(name="event", description="Event commands")
reaction_group = app_commands.Group(name="reaction", description="Reaction commands")
timeline_group = app_commands.Group(name="timeline", description="Timeline commands")

@character_group.command(name="create", description="Create a character")
@app_commands.choices(genre=GENRE_CHOICES)
async def character_create(interaction: discord.Interaction, genre: app_commands.Choice[str]):
    await interaction.response.send_modal(CharacterCreateModal(genre.value))

@character_group.command(name="list", description="List your characters")
async def character_list(interaction: discord.Interaction):
    data = load_data()
    u = get_user(data, str(interaction.user.id))
    if not u["characters"]:
        await interaction.response.send_message("You have no characters yet.", ephemeral=True)
        return
    msg = "\n".join([f"- **{c['name']}** | {c['age']} | {c['gender']} | {c['genre']}" for c in u["characters"].values()])
    await interaction.response.send_message(f"**Your Characters:**\n{msg}")

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

@baby_group.command(name="event", description="Generate a baby event")
async def baby_event(interaction: discord.Interaction, name: str):
    data = load_data()
    u = get_user(data, str(interaction.user.id))
    baby = u["babies"].get(name.lower())
    if not baby:
        await interaction.response.send_message("Baby not found.", ephemeral=True)
        return
    await interaction.response.send_message(f"**{baby['name']}**\n\n{random.choice(baby_events[baby['temperament']])}")

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

@event_group.command(name="generate", description="Generate a RP event by genre")
@app_commands.choices(genre=GENRE_CHOICES)
async def event_generate(interaction: discord.Interaction, genre: app_commands.Choice[str]):
    pool = events.get(genre.value, events["default"])
    await interaction.response.send_message(f"**{genre.name} Event:**\n{random.choice(pool)}")

@reaction_group.command(name="generate", description="Generate an NPC reaction")
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
    u["timeline"].append({"date": datetime.now().strftime("%Y-%m-%d"), "note": note})
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
bot.tree.add_command(event_group)
bot.tree.add_command(reaction_group)
bot.tree.add_command(timeline_group)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Logged in as {bot.user}")
        print(f"Synced {len(synced)} global commands")
    except Exception as e:
        print(f"Sync failed: {e}")

bot.run(TOKEN)