"""
Gaia RP Bot — Life/Drama Simulation Version
Single-file JSON bot.

Features:
- No school system
- /character create -> 3 genre dropdown -> popup form
- /add parent -> parent type dropdown -> popup form, saved under a character
- /add dr -> doctor type dropdown -> doctor style dropdown -> popup form
- /medical visit -> visit type dropdown -> popup form -> doctor response by style/type
- /start pregnancy -> month dropdown -> gender dropdown -> popup form
- JSON storage across servers by Discord user ID

requirements.txt:
discord.py
"""

import os
import json
import random
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List

import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("BOT_TOKEN")
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

FILES = {
    "characters": DATA_DIR / "characters.json",
    "parents": DATA_DIR / "parents.json",
    "doctors": DATA_DIR / "doctors.json",
    "medical": DATA_DIR / "medical.json",
    "pregnancies": DATA_DIR / "pregnancies.json",
    "babies": DATA_DIR / "babies.json",
    "relationships": DATA_DIR / "relationships.json",
    "timelines": DATA_DIR / "timelines.json",
    "settings": DATA_DIR / "settings.json",
}

DEFAULT_SETTINGS = {"realism": "medium", "chaos": "medium", "privacy": "private"}

CHARACTER_GENRES = [
    discord.SelectOption(label="Slice of Life", value="slice_of_life", description="Everyday life, emotions, family, friendships."),
    discord.SelectOption(label="Romance", value="romance", description="Love, dating, jealousy, heartbreak."),
    discord.SelectOption(label="Family Drama", value="family_drama", description="Parents, siblings, secrets, conflict."),
    discord.SelectOption(label="Celebrity Drama", value="celebrity_drama", description="Fame, fans, paparazzi, scandal."),
    discord.SelectOption(label="Medical Drama", value="medical_drama", description="Doctors, injuries, sickness, pregnancy."),
    discord.SelectOption(label="Fantasy", value="fantasy", description="Magic, realms, powers, supernatural stories."),
    discord.SelectOption(label="Crime/Thriller", value="crime_thriller", description="Secrets, danger, mystery, tension."),
    discord.SelectOption(label="Chaotic RP", value="chaotic_rp", description="Messy, wild, dramatic twists."),
]

PARENT_TYPES = [
    discord.SelectOption(label="Supportive", value="supportive"),
    discord.SelectOption(label="Strict", value="strict"),
    discord.SelectOption(label="Overprotective", value="overprotective"),
    discord.SelectOption(label="Traditional", value="traditional"),
    discord.SelectOption(label="Dramatic", value="dramatic"),
    discord.SelectOption(label="Absent", value="absent"),
    discord.SelectOption(label="Religious", value="religious"),
    discord.SelectOption(label="Messy", value="messy"),
    discord.SelectOption(label="Gentle", value="gentle"),
    discord.SelectOption(label="Wealthy", value="wealthy"),
]

DOCTOR_TYPES = [
    discord.SelectOption(label="OBGYN", value="obgyn"),
    discord.SelectOption(label="Primary Care", value="primary_care"),
    discord.SelectOption(label="Pediatrician", value="pediatrician"),
    discord.SelectOption(label="ER Doctor", value="er_doctor"),
    discord.SelectOption(label="Surgeon", value="surgeon"),
    discord.SelectOption(label="Therapist", value="therapist"),
    discord.SelectOption(label="Specialist", value="specialist"),
]

DOCTOR_STYLES = [
    discord.SelectOption(label="Attentive", value="attentive"),
    discord.SelectOption(label="Gentle", value="gentle"),
    discord.SelectOption(label="Hands-on", value="hands_on"),
    discord.SelectOption(label="Blunt", value="blunt"),
    discord.SelectOption(label="Strict", value="strict"),
    discord.SelectOption(label="Rude", value="rude"),
    discord.SelectOption(label="Annoying", value="annoying"),
    discord.SelectOption(label="Warm", value="warm"),
]

VISIT_TYPES = [
    discord.SelectOption(label="General Checkup", value="checkup"),
    discord.SelectOption(label="Pregnancy Appointment", value="pregnancy_appointment"),
    discord.SelectOption(label="Ultrasound", value="ultrasound"),
    discord.SelectOption(label="Injury Visit", value="injury"),
    discord.SelectOption(label="Sickness Visit", value="sickness"),
    discord.SelectOption(label="Emergency", value="emergency"),
    discord.SelectOption(label="Follow-up", value="followup"),
    discord.SelectOption(label="Results", value="results"),
]

PREGNANCY_MONTHS = [discord.SelectOption(label=f"{i} Month{'s' if i > 1 else ''}", value=str(i)) for i in range(1, 10)]
BABY_GENDERS = [
    discord.SelectOption(label="Boy", value="boy"),
    discord.SelectOption(label="Girl", value="girl"),
    discord.SelectOption(label="Twins", value="twins"),
    discord.SelectOption(label="Randomize", value="random"),
]
LEVEL_CHOICES = [app_commands.Choice(name="Low", value="low"), app_commands.Choice(name="Medium", value="medium"), app_commands.Choice(name="High", value="high")]

MINOR_INJURIES = ["sprained ankle", "wrist strain", "minor burn", "bruised ribs", "nosebleed", "small cut needing stitches", "mild concussion", "dehydration"]
MAJOR_INJURIES = ["broken arm", "torn ligament", "severe concussion", "surgery recovery", "car accident trauma", "internal bleeding scare", "collapsed lung scare"]
MINOR_SICKNESSES = ["cold", "flu", "stomach bug", "migraine", "food poisoning", "sinus infection", "fever", "allergic reaction"]
SERIOUS_SICKNESSES = ["pneumonia", "severe anemia", "infection", "high fever complications", "fainting episodes", "chronic fatigue flare-up"]
PREGNANCY_CONDITIONS = ["low iron", "dehydration", "Braxton Hicks contractions", "false labor", "morning sickness", "high blood pressure scare", "baby growth concern"]
PREGNANCY_CRAVINGS = ["pickles", "ice cream", "spicy noodles", "burgers", "sour candy", "fruit", "chips", "chocolate milk", "fries", "cereal at midnight"]
PREGNANCY_SYMPTOMS = ["morning sickness", "fatigue", "dizziness", "mood swings", "food aversions", "back pain", "heartburn", "emotional crying", "baby kicks"]
BABY_TEMPERAMENTS = ["calm", "clingy", "chaotic", "playful", "shy", "sensitive", "curious", "dramatic"]

RELATIONSHIP_EVENTS = ["A jealous argument starts after someone misreads the situation.", "A quiet confession changes the mood completely.", "Someone storms out before the full truth comes out.", "A secret almost slips during an emotional moment.", "A soft moment happens when nobody expects it."]
CELEBRITY_EVENTS = ["A paparazzi photo goes viral with a messy caption.", "A livestream clip catches something it was not supposed to.", "Fans start connecting details and building theories.", "An interview question gets too personal.", "A scandal starts from one vague online post."]
SOFT_EVENTS = ["Someone offers comfort without asking too many questions.", "A quiet moment gives everyone room to breathe.", "A small act of care means more than expected."]
CHAOTIC_EVENTS = ["Everything goes wrong at the same time.", "A private conversation gets overheard.", "Someone sends a message to the wrong person.", "The wrong person shows up at the worst possible time."]

# ---------------- Storage ----------------
def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def ensure_file(name: str) -> None:
    FILES[name].parent.mkdir(exist_ok=True)
    if not FILES[name].exists():
        FILES[name].write_text("{}", encoding="utf-8")

def load_data(name: str) -> Dict[str, Any]:
    ensure_file(name)
    try:
        return json.loads(FILES[name].read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

def save_data(name: str, data: Dict[str, Any]) -> None:
    ensure_file(name)
    FILES[name].write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def uid(interaction: discord.Interaction) -> str:
    return str(interaction.user.id)

def make_id(prefix: str) -> str:
    return f"{prefix}_{random.randint(100000, 999999)}"

def get_bucket(name: str, user_id: str) -> Dict[str, Any]:
    data = load_data(name)
    data.setdefault(user_id, {})
    save_data(name, data)
    return data[user_id]

def set_bucket(name: str, user_id: str, bucket: Dict[str, Any]) -> None:
    data = load_data(name)
    data[user_id] = bucket
    save_data(name, data)

def add_timeline(user_id: str, text: str, category: str = "general") -> None:
    data = load_data("timelines")
    data.setdefault(user_id, [])
    data[user_id].append({"id": make_id("timeline"), "category": category, "text": text, "time": utc_now()})
    save_data("timelines", data)

def find_item(bucket: Dict[str, Any], query: str) -> Optional[tuple[str, Dict[str, Any]]]:
    q = query.lower().strip()
    if query in bucket:
        return query, bucket[query]
    for item_id, item in bucket.items():
        possible = [str(item.get("name", "")), str(item.get("character", "")), str(item.get("doctor_name", "")), str(item.get("parent_name", ""))]
        if any(x.lower() == q for x in possible):
            return item_id, item
    return None

def make_embed(title: str, description: str, color: int = 0xE8A2C8) -> discord.Embed:
    e = discord.Embed(title=title, description=description[:4000], color=color)
    e.set_footer(text="Gaia RP Bot")
    return e

async def send(interaction: discord.Interaction, title: str, text: str, ephemeral: bool = False):
    await interaction.response.send_message(embed=make_embed(title, text), ephemeral=ephemeral)

def format_list(bucket: Dict[str, Any], empty: str) -> str:
    if not bucket:
        return empty
    lines = []
    for item_id, item in bucket.items():
        name = item.get("name") or item.get("parent_name") or item.get("doctor_name") or item.get("character") or item_id
        detail = item.get("connected_character") or item.get("doctor_type") or item.get("status") or ""
        suffix = f" — {detail}" if detail else ""
        lines.append(f"`{item_id}`: **{name}**{suffix}")
    return "\n".join(lines)

# ---------------- Bot ----------------
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Slash sync failed: {e}")
    print(f"Gaia is online as {bot.user}.")

character = app_commands.Group(name="character", description="Character commands")
parent = app_commands.Group(name="parent", description="Parent commands")
doctor = app_commands.Group(name="dr", description="Doctor commands")
medical = app_commands.Group(name="medical", description="Medical commands")
pregnancy = app_commands.Group(name="pregnancy", description="Pregnancy commands")
start = app_commands.Group(name="start", description="Interactive setup commands")
baby = app_commands.Group(name="baby", description="Baby commands")
relationship = app_commands.Group(name="relationship", description="Relationship commands")
celebrity = app_commands.Group(name="celebrity", description="Celebrity commands")
reaction = app_commands.Group(name="reaction", description="Reaction commands")
timeline = app_commands.Group(name="timeline", description="Timeline commands")
generate = app_commands.Group(name="generate", description="Generation commands")
settings = app_commands.Group(name="settings", description="Settings commands")
add_group = app_commands.Group(name="add", description="Add/setup commands")

# ---------------- Character create dropdown + form ----------------
class CharacterCreateModal(discord.ui.Modal, title="Create Character"):
    def __init__(self, genres: List[str]):
        super().__init__()
        self.genres = genres
        self.name_input = discord.ui.TextInput(label="Name", placeholder="Character name", max_length=100)
        self.age_input = discord.ui.TextInput(label="Age", placeholder="Character age", max_length=20)
        self.gender_input = discord.ui.TextInput(label="Gender", placeholder="Character gender", max_length=80)
        self.appearance_input = discord.ui.TextInput(label="Appearance", placeholder="Describe their look, style, hair, features, etc.", style=discord.TextStyle.paragraph, max_length=1000)
        self.backstory_input = discord.ui.TextInput(label="Backstory", placeholder="Describe their family, past, struggles, goals, etc.", style=discord.TextStyle.paragraph, max_length=2000)
        self.add_item(self.name_input); self.add_item(self.age_input); self.add_item(self.gender_input); self.add_item(self.appearance_input); self.add_item(self.backstory_input)

    async def on_submit(self, interaction: discord.Interaction):
        user = uid(interaction)
        bucket = get_bucket("characters", user)
        char_id = make_id("char")
        bucket[char_id] = {"name": self.name_input.value, "age": self.age_input.value, "gender": self.gender_input.value, "genres": self.genres, "appearance": self.appearance_input.value, "backstory": self.backstory_input.value, "notes": "", "selected": False, "created_at": utc_now(), "updated_at": utc_now()}
        set_bucket("characters", user, bucket)
        add_timeline(user, f"Created character {self.name_input.value}.", "character")
        text = f"**{self.name_input.value}** has been created.\nID: `{char_id}`\nAge: **{self.age_input.value}**\nGender: **{self.gender_input.value}**\nGenres: **{', '.join(self.genres)}**\n\n**Appearance:** {self.appearance_input.value[:900]}\n\n**Backstory:** {self.backstory_input.value[:900]}"
        await interaction.response.send_message(embed=make_embed("Character Created", text))

class CharacterGenreSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(placeholder="Pick up to 3 genres for this character...", min_values=1, max_values=3, options=CHARACTER_GENRES)
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CharacterCreateModal(self.values))

class CharacterGenreView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(CharacterGenreSelect())

@character.command(name="create", description="Create character with genre dropdown and form")
async def character_create(interaction: discord.Interaction):
    await interaction.response.send_message("Choose up to **3 genres** for your character. Then Gaia will open the character form.", view=CharacterGenreView(), ephemeral=True)

@character.command(name="list", description="List your characters")
async def character_list(interaction: discord.Interaction):
    await send(interaction, "Characters", format_list(get_bucket("characters", uid(interaction)), "No characters found."))

@character.command(name="profile", description="View character profile")
async def character_profile(interaction: discord.Interaction, character_id_or_name: str):
    found = find_item(get_bucket("characters", uid(interaction)), character_id_or_name)
    if not found:
        await interaction.response.send_message("Character not found.", ephemeral=True); return
    char_id, item = found
    text = f"ID: `{char_id}`\nName: **{item.get('name')}**\nAge: {item.get('age')}\nGender: {item.get('gender')}\nGenres: {', '.join(item.get('genres', []))}\n\n**Appearance:** {item.get('appearance', 'N/A')}\n\n**Backstory:** {item.get('backstory', 'N/A')}\n\n**Notes:** {item.get('notes') or 'None'}"
    await send(interaction, "Character Profile", text)

@character.command(name="select", description="Select active character")
async def character_select(interaction: discord.Interaction, character_id_or_name: str):
    user = uid(interaction); bucket = get_bucket("characters", user); found = find_item(bucket, character_id_or_name)
    if not found:
        await interaction.response.send_message("Character not found.", ephemeral=True); return
    selected_id, selected = found
    for item in bucket.values(): item["selected"] = False
    selected["selected"] = True; bucket[selected_id] = selected; set_bucket("characters", user, bucket)
    await send(interaction, "Character Selected", f"Selected **{selected.get('name')}**.")

@character.command(name="edit", description="Quick edit a character")
async def character_edit(interaction: discord.Interaction, character_id_or_name: str, name: Optional[str] = None, age: Optional[str] = None, gender: Optional[str] = None, appearance: Optional[str] = None, backstory: Optional[str] = None):
    user = uid(interaction); bucket = get_bucket("characters", user); found = find_item(bucket, character_id_or_name)
    if not found:
        await interaction.response.send_message("Character not found.", ephemeral=True); return
    char_id, item = found
    for key, value in {"name": name, "age": age, "gender": gender, "appearance": appearance, "backstory": backstory}.items():
        if value is not None: item[key] = value
    item["updated_at"] = utc_now(); bucket[char_id] = item; set_bucket("characters", user, bucket)
    await send(interaction, "Character Updated", f"Updated **{item.get('name')}**.")

@character.command(name="delete", description="Delete a character")
async def character_delete(interaction: discord.Interaction, character_id_or_name: str):
    user = uid(interaction); bucket = get_bucket("characters", user); found = find_item(bucket, character_id_or_name)
    if not found:
        await interaction.response.send_message("Character not found.", ephemeral=True); return
    char_id, item = found; del bucket[char_id]; set_bucket("characters", user, bucket)
    await send(interaction, "Character Deleted", f"Deleted **{item.get('name', char_id)}**.")

@character.command(name="notes", description="Add/update character notes")
async def character_notes(interaction: discord.Interaction, character_id_or_name: str, notes: str):
    user = uid(interaction); bucket = get_bucket("characters", user); found = find_item(bucket, character_id_or_name)
    if not found:
        await interaction.response.send_message("Character not found.", ephemeral=True); return
    char_id, item = found; item["notes"] = notes; bucket[char_id] = item; set_bucket("characters", user, bucket)
    await send(interaction, "Notes Updated", f"Notes updated for **{item.get('name')}**.")

# ---------------- Parent dropdown + form ----------------
class ParentCreateModal(discord.ui.Modal, title="Add Parent"):
    def __init__(self, parent_types: List[str]):
        super().__init__(); self.parent_types = parent_types
        self.connected_character = discord.ui.TextInput(label="Connected Character", placeholder="Character name or ID")
        self.parent_name = discord.ui.TextInput(label="Parent Name", placeholder="Parent name")
        self.age = discord.ui.TextInput(label="Age", placeholder="Parent age")
        self.gender = discord.ui.TextInput(label="Gender", placeholder="Parent gender")
        self.backstory = discord.ui.TextInput(label="Personality / Backstory", placeholder="Describe what kind of parent they are.", style=discord.TextStyle.paragraph, max_length=2000)
        for x in [self.connected_character, self.parent_name, self.age, self.gender, self.backstory]: self.add_item(x)
    async def on_submit(self, interaction: discord.Interaction):
        user = uid(interaction); bucket = get_bucket("parents", user); parent_id = make_id("parent")
        bucket[parent_id] = {"parent_name": self.parent_name.value, "name": self.parent_name.value, "age": self.age.value, "gender": self.gender.value, "connected_character": self.connected_character.value, "parent_types": self.parent_types, "backstory": self.backstory.value, "created_at": utc_now()}
        set_bucket("parents", user, bucket); add_timeline(user, f"Added parent {self.parent_name.value} for {self.connected_character.value}.", "parent")
        text = f"**{self.parent_name.value}** added for **{self.connected_character.value}**.\nID: `{parent_id}`\nAge: {self.age.value}\nGender: {self.gender.value}\nTypes: **{', '.join(self.parent_types)}**\n\n**Info:** {self.backstory.value[:1000]}"
        await interaction.response.send_message(embed=make_embed("Parent Added", text))

class ParentTypeSelect(discord.ui.Select):
    def __init__(self): super().__init__(placeholder="Pick up to 3 parent types...", min_values=1, max_values=3, options=PARENT_TYPES)
    async def callback(self, interaction: discord.Interaction): await interaction.response.send_modal(ParentCreateModal(self.values))
class ParentTypeView(discord.ui.View):
    def __init__(self): super().__init__(timeout=180); self.add_item(ParentTypeSelect())

@add_group.command(name="parent", description="Add parent with type dropdown and form")
async def add_parent(interaction: discord.Interaction):
    await interaction.response.send_message("Choose up to **3 parent types**. Then Gaia will open the parent form.", view=ParentTypeView(), ephemeral=True)

@parent.command(name="list", description="List saved parents")
async def parent_list(interaction: discord.Interaction): await send(interaction, "Parents", format_list(get_bucket("parents", uid(interaction)), "No parents found."))
@parent.command(name="profile", description="View parent profile")
async def parent_profile(interaction: discord.Interaction, parent_id_or_name: str):
    found = find_item(get_bucket("parents", uid(interaction)), parent_id_or_name)
    if not found: await interaction.response.send_message("Parent not found.", ephemeral=True); return
    parent_id, item = found
    text = f"ID: `{parent_id}`\nName: **{item.get('parent_name')}**\nConnected Character: {item.get('connected_character')}\nAge: {item.get('age')}\nGender: {item.get('gender')}\nTypes: {', '.join(item.get('parent_types', []))}\n\n**Info:** {item.get('backstory', 'N/A')}"
    await send(interaction, "Parent Profile", text)
@parent.command(name="randomize", description="Randomize a parent type combo")
async def parent_randomize(interaction: discord.Interaction): await send(interaction, "Random Parent Type", " + ".join(random.sample([x.value for x in PARENT_TYPES], 3)))
@parent.command(name="delete", description="Delete a parent")
async def parent_delete(interaction: discord.Interaction, parent_id_or_name: str):
    user = uid(interaction); bucket = get_bucket("parents", user); found = find_item(bucket, parent_id_or_name)
    if not found: await interaction.response.send_message("Parent not found.", ephemeral=True); return
    parent_id, item = found; del bucket[parent_id]; set_bucket("parents", user, bucket); await send(interaction, "Parent Deleted", f"Deleted **{item.get('parent_name', parent_id)}**.")

# ---------------- Doctor dropdown + form ----------------
class DoctorCreateModal(discord.ui.Modal, title="Add Doctor"):
    def __init__(self, doctor_type: str, doctor_style: str):
        super().__init__(); self.doctor_type = doctor_type; self.doctor_style = doctor_style
        self.doctor_name = discord.ui.TextInput(label="Doctor Name", placeholder="Example: Dr. Judy")
        self.age = discord.ui.TextInput(label="Age", placeholder="Doctor age")
        self.gender = discord.ui.TextInput(label="Gender", placeholder="Doctor gender")
        self.clinic = discord.ui.TextInput(label="Clinic / Hospital", placeholder="Where they work")
        self.notes = discord.ui.TextInput(label="Notes", placeholder="How they speak, act, or treat patients.", style=discord.TextStyle.paragraph, max_length=1200, required=False)
        for x in [self.doctor_name, self.age, self.gender, self.clinic, self.notes]: self.add_item(x)
    async def on_submit(self, interaction: discord.Interaction):
        user = uid(interaction); bucket = get_bucket("doctors", user); doctor_id = make_id("dr")
        bucket[doctor_id] = {"doctor_name": self.doctor_name.value, "name": self.doctor_name.value, "age": self.age.value, "gender": self.gender.value, "clinic": self.clinic.value, "doctor_type": self.doctor_type, "doctor_style": self.doctor_style, "notes": self.notes.value, "created_at": utc_now()}
        set_bucket("doctors", user, bucket); add_timeline(user, f"Added doctor {self.doctor_name.value}.", "doctor")
        text = f"**{self.doctor_name.value}** added.\nID: `{doctor_id}`\nType: **{self.doctor_type}**\nStyle: **{self.doctor_style}**\nClinic: {self.clinic.value}\n\nNotes: {self.notes.value or 'None'}"
        await interaction.response.send_message(embed=make_embed("Doctor Added", text))
class DoctorStyleSelect(discord.ui.Select):
    def __init__(self, doctor_type: str): self.doctor_type = doctor_type; super().__init__(placeholder="Choose doctor's style/personality...", min_values=1, max_values=1, options=DOCTOR_STYLES)
    async def callback(self, interaction: discord.Interaction): await interaction.response.send_modal(DoctorCreateModal(self.doctor_type, self.values[0]))
class DoctorStyleView(discord.ui.View):
    def __init__(self, doctor_type: str): super().__init__(timeout=180); self.add_item(DoctorStyleSelect(doctor_type))
class DoctorTypeSelect(discord.ui.Select):
    def __init__(self): super().__init__(placeholder="Choose the kind of doctor...", min_values=1, max_values=1, options=DOCTOR_TYPES)
    async def callback(self, interaction: discord.Interaction): await interaction.response.send_message(f"Doctor type selected: **{self.values[0]}**. Now choose their style.", view=DoctorStyleView(self.values[0]), ephemeral=True)
class DoctorTypeView(discord.ui.View):
    def __init__(self): super().__init__(timeout=180); self.add_item(DoctorTypeSelect())
@add_group.command(name="dr", description="Add doctor with dropdowns and form")
async def add_dr(interaction: discord.Interaction): await interaction.response.send_message("Choose what kind of doctor this is.", view=DoctorTypeView(), ephemeral=True)
@doctor.command(name="list", description="List saved doctors")
async def doctor_list(interaction: discord.Interaction): await send(interaction, "Doctors", format_list(get_bucket("doctors", uid(interaction)), "No doctors found."))
@doctor.command(name="profile", description="View doctor profile")
async def doctor_profile(interaction: discord.Interaction, doctor_id_or_name: str):
    found = find_item(get_bucket("doctors", uid(interaction)), doctor_id_or_name)
    if not found: await interaction.response.send_message("Doctor not found.", ephemeral=True); return
    doctor_id, item = found
    text = f"ID: `{doctor_id}`\nName: **{item.get('doctor_name')}**\nType: {item.get('doctor_type')}\nStyle: {item.get('doctor_style')}\nAge: {item.get('age')}\nGender: {item.get('gender')}\nClinic: {item.get('clinic')}\n\nNotes: {item.get('notes') or 'None'}"
    await send(interaction, "Doctor Profile", text)
@doctor.command(name="delete", description="Delete a doctor")
async def doctor_delete(interaction: discord.Interaction, doctor_id_or_name: str):
    user = uid(interaction); bucket = get_bucket("doctors", user); found = find_item(bucket, doctor_id_or_name)
    if not found: await interaction.response.send_message("Doctor not found.", ephemeral=True); return
    doctor_id, item = found; del bucket[doctor_id]; set_bucket("doctors", user, bucket); await send(interaction, "Doctor Deleted", f"Deleted **{item.get('doctor_name', doctor_id)}**.")

# ---------------- Medical visit ----------------
def pick_condition(visit_type: str) -> str:
    if visit_type == "injury": return random.choice(MINOR_INJURIES + MAJOR_INJURIES)
    if visit_type == "sickness": return random.choice(MINOR_SICKNESSES + SERIOUS_SICKNESSES)
    if visit_type in ["pregnancy_appointment", "ultrasound"]: return random.choice(PREGNANCY_CONDITIONS + PREGNANCY_SYMPTOMS)
    if visit_type == "emergency": return random.choice(MAJOR_INJURIES + SERIOUS_SICKNESSES + PREGNANCY_CONDITIONS)
    if visit_type == "followup": return random.choice(["recovery progress", "symptoms improving", "needs more rest", "needs another checkup"])
    if visit_type == "results": return random.choice(["bloodwork results", "ultrasound results", "test results", "iron levels", "blood pressure results"])
    return random.choice(["healthy checkup", "slight concern", "routine exam", "wellness check"])

def doctor_response(doctor: Dict[str, Any], visit_type: str, condition: str, patient: str, notes: str) -> str:
    name = doctor.get("doctor_name", "The doctor"); doc_type = doctor.get("doctor_type", "doctor"); style = doctor.get("doctor_style", "attentive")
    if style in ["gentle", "warm", "attentive"]: text = f'{name} speaks softly and says, "You are doing okay, {patient}. We are going to take this seriously and keep an eye on {condition}."'
    elif style in ["blunt", "strict"]: text = f'{name} is direct: "I am not ignoring {condition}. You need to follow instructions and stop pushing yourself."'
    elif style == "rude": text = f"{name} is cold and dismissive, but still gives the medical plan for {condition}."
    elif style == "annoying": text = f"{name} talks way too much, makes an awkward joke, then finally explains that {condition} needs attention."
    else: text = f"{name} handles the {visit_type} visit and explains the situation around {condition}."
    if doc_type == "obgyn": text += " They mention vitamins, hydration, rest, and watching for dizziness or unusual pain."
    elif doc_type == "er_doctor": text += " They focus on stabilizing the situation quickly and checking vitals."
    elif doc_type == "therapist": text += " They focus on stress, emotional safety, and coping tools."
    elif doc_type == "pediatrician": text += " They explain things in a calm, family-friendly way."
    if notes: text += f"\n\n**Visit Notes:** {notes}"
    return text

class MedicalVisitModal(discord.ui.Modal, title="Medical Visit"):
    def __init__(self, visit_type: str):
        super().__init__(); self.visit_type = visit_type
        self.character_name = discord.ui.TextInput(label="Patient / Character", placeholder="Character name")
        self.doctor_name = discord.ui.TextInput(label="Doctor", placeholder="Doctor name or ID")
        self.notes = discord.ui.TextInput(label="Appointment Prompt / Notes", placeholder="Example: Dr. Judy was nice today and said you look healthy.", style=discord.TextStyle.paragraph, max_length=1500, required=False)
        self.add_item(self.character_name); self.add_item(self.doctor_name); self.add_item(self.notes)
    async def on_submit(self, interaction: discord.Interaction):
        user = uid(interaction); doctors = get_bucket("doctors", user); found_doc = find_item(doctors, self.doctor_name.value)
        doctor_id, doctor = found_doc if found_doc else ("unsaved", {"doctor_name": self.doctor_name.value, "doctor_type": "doctor", "doctor_style": "attentive"})
        condition = pick_condition(self.visit_type); response = doctor_response(doctor, self.visit_type, condition, self.character_name.value, self.notes.value)
        medical_bucket = get_bucket("medical", user); visit_id = make_id("visit")
        medical_bucket[visit_id] = {"character": self.character_name.value, "doctor": doctor.get("doctor_name"), "doctor_id": doctor_id, "visit_type": self.visit_type, "condition": condition, "notes": self.notes.value, "response": response, "created_at": utc_now()}
        set_bucket("medical", user, medical_bucket); add_timeline(user, f"{self.character_name.value} had a {self.visit_type} visit for {condition}.", "medical")
        text = f"**Patient:** {self.character_name.value}\n**Doctor:** {doctor.get('doctor_name')} ({doctor.get('doctor_type')} / {doctor.get('doctor_style')})\n**Visit Type:** {self.visit_type}\n**Condition/Focus:** {condition}\n\n{response}\n\nVisit ID: `{visit_id}`"
        await interaction.response.send_message(embed=make_embed("Medical Visit", text))
class MedicalVisitSelect(discord.ui.Select):
    def __init__(self): super().__init__(placeholder="Choose visit type...", min_values=1, max_values=1, options=VISIT_TYPES)
    async def callback(self, interaction: discord.Interaction): await interaction.response.send_modal(MedicalVisitModal(self.values[0]))
class MedicalVisitView(discord.ui.View):
    def __init__(self): super().__init__(timeout=180); self.add_item(MedicalVisitSelect())
@medical.command(name="visit", description="Start interactive medical visit")
async def medical_visit(interaction: discord.Interaction): await interaction.response.send_message("Choose the type of medical visit.", view=MedicalVisitView(), ephemeral=True)
@medical.command(name="status", description="View recent medical records")
async def medical_status(interaction: discord.Interaction):
    bucket = get_bucket("medical", uid(interaction))
    if not bucket: await interaction.response.send_message("No medical records found.", ephemeral=True); return
    lines = [f"`{visit_id}`: **{item.get('character')}** — {item.get('visit_type')} / {item.get('condition')}" for visit_id, item in list(bucket.items())[-10:]]
    await send(interaction, "Medical Records", "\n".join(lines))
@medical.command(name="delete", description="Delete medical record")
async def medical_delete(interaction: discord.Interaction, visit_id: str):
    user = uid(interaction); bucket = get_bucket("medical", user)
    if visit_id not in bucket: await interaction.response.send_message("Medical record not found.", ephemeral=True); return
    item = bucket.pop(visit_id); set_bucket("medical", user, bucket); await send(interaction, "Medical Record Deleted", f"Deleted record for **{item.get('character')}**.")

# ---------------- Start pregnancy dropdown flow ----------------
class PregnancyCreateModal(discord.ui.Modal, title="Start Pregnancy"):
    def __init__(self, month: str, baby_gender: str):
        super().__init__(); self.month = month; self.baby_gender = baby_gender
        self.character_name = discord.ui.TextInput(label="Pregnant Character", placeholder="Character name")
        self.partner_name = discord.ui.TextInput(label="Partner / Other Parent", placeholder="Partner name")
        self.hidden = discord.ui.TextInput(label="Hidden Pregnancy?", placeholder="yes or no")
        self.notes = discord.ui.TextInput(label="Notes", placeholder="Any setup details, drama, family situation, etc.", style=discord.TextStyle.paragraph, max_length=1200, required=False)
        self.add_item(self.character_name); self.add_item(self.partner_name); self.add_item(self.hidden); self.add_item(self.notes)
    async def on_submit(self, interaction: discord.Interaction):
        user = uid(interaction); bucket = get_bucket("pregnancies", user); preg_id = make_id("preg")
        gender = random.choice(["boy", "girl"]) if self.baby_gender == "random" else self.baby_gender
        bucket[preg_id] = {"character": self.character_name.value, "partner": self.partner_name.value, "month": int(self.month), "weeks": int(self.month) * 4, "days": 0, "baby_gender": gender, "hidden": self.hidden.value.lower().strip() in ["yes", "y", "true"], "status": "active", "symptom": random.choice(PREGNANCY_SYMPTOMS), "craving": random.choice(PREGNANCY_CRAVINGS), "notes": self.notes.value, "created_at": utc_now()}
        set_bucket("pregnancies", user, bucket); add_timeline(user, f"{self.character_name.value} started a pregnancy storyline.", "pregnancy")
        item = bucket[preg_id]
        text = f"Pregnancy created for **{item['character']}**.\nID: `{preg_id}`\nPartner: **{item['partner']}**\nMonth: **{item['month']}**\nBaby Gender: **{item['baby_gender']}**\nHidden: **{item['hidden']}**\nSymptom: **{item['symptom']}**\nCraving: **{item['craving']}**\n\nNotes: {item['notes'] or 'None'}"
        await interaction.response.send_message(embed=make_embed("Pregnancy Started", text))
class PregnancyGenderSelect(discord.ui.Select):
    def __init__(self, month: str): self.month = month; super().__init__(placeholder="Pick baby gender or randomize...", min_values=1, max_values=1, options=BABY_GENDERS)
    async def callback(self, interaction: discord.Interaction): await interaction.response.send_modal(PregnancyCreateModal(self.month, self.values[0]))
class PregnancyGenderView(discord.ui.View):
    def __init__(self, month: str): super().__init__(timeout=180); self.add_item(PregnancyGenderSelect(month))
class PregnancyMonthSelect(discord.ui.Select):
    def __init__(self): super().__init__(placeholder="Choose pregnancy month...", min_values=1, max_values=1, options=PREGNANCY_MONTHS)
    async def callback(self, interaction: discord.Interaction): await interaction.response.send_message(f"Month selected: **{self.values[0]}**. Now choose baby gender.", view=PregnancyGenderView(self.values[0]), ephemeral=True)
class PregnancyMonthView(discord.ui.View):
    def __init__(self): super().__init__(timeout=180); self.add_item(PregnancyMonthSelect())
@start.command(name="pregnancy", description="Start pregnancy with dropdowns and form")
async def start_pregnancy(interaction: discord.Interaction): await interaction.response.send_message("Choose what month the pregnancy starts in.", view=PregnancyMonthView(), ephemeral=True)
@pregnancy.command(name="profile", description="View pregnancy profile")
async def pregnancy_profile(interaction: discord.Interaction, pregnancy_id_or_character: str):
    found = find_item(get_bucket("pregnancies", uid(interaction)), pregnancy_id_or_character)
    if not found: await interaction.response.send_message("Pregnancy not found.", ephemeral=True); return
    preg_id, item = found
    text = f"ID: `{preg_id}`\nCharacter: **{item.get('character')}**\nPartner: {item.get('partner')}\nMonth: {item.get('month')}\nWeeks: {item.get('weeks')}w {item.get('days')}d\nBaby Gender: {item.get('baby_gender')}\nHidden: {item.get('hidden')}\nSymptom: {item.get('symptom')}\nCraving: {item.get('craving')}\n\nNotes: {item.get('notes') or 'None'}"
    await send(interaction, "Pregnancy Profile", text)
@pregnancy.command(name="list", description="List pregnancies")
async def pregnancy_list(interaction: discord.Interaction): await send(interaction, "Pregnancies", format_list(get_bucket("pregnancies", uid(interaction)), "No pregnancies found."))
@pregnancy.command(name="event", description="Generate pregnancy event")
async def pregnancy_event(interaction: discord.Interaction):
    event = random.choice(["A sudden craving becomes impossible to ignore.", "Morning sickness hits at the worst possible time.", "A parent starts getting suspicious.", "The baby kicks during an emotional conversation.", "A doctor's appointment brings unexpected news."])
    add_timeline(uid(interaction), event, "pregnancy"); await send(interaction, "Pregnancy Event", event)
@pregnancy.command(name="delete", description="Delete pregnancy")
async def pregnancy_delete(interaction: discord.Interaction, pregnancy_id_or_character: str):
    user = uid(interaction); bucket = get_bucket("pregnancies", user); found = find_item(bucket, pregnancy_id_or_character)
    if not found: await interaction.response.send_message("Pregnancy not found.", ephemeral=True); return
    preg_id, item = found; del bucket[preg_id]; set_bucket("pregnancies", user, bucket); await send(interaction, "Pregnancy Deleted", f"Deleted pregnancy for **{item.get('character')}**.")

# ---------------- Reactions + misc ----------------
def parent_reaction_text(parent_item: Dict[str, Any]) -> str:
    name = parent_item.get("parent_name", "The parent"); types = parent_item.get("parent_types", [])
    if "strict" in types or "traditional" in types: return f'{name} goes tense, their voice firm. "You knew better than this. We are not pretending this is nothing."'
    if "supportive" in types or "gentle" in types: return f'{name} softens immediately. "I am scared too, but I am here. We will figure it out."'
    if "overprotective" in types: return f"{name} starts pacing, asking where they were, who knew, and why nobody told them sooner."
    if "dramatic" in types or "messy" in types: return f"{name} reacts loudly, overwhelmed before anyone can even finish explaining."
    if "absent" in types: return f"{name} barely knows what to say, the distance between them suddenly obvious."
    if "religious" in types: return f'{name} closes their eyes. "We need to pray and talk about what happens next."'
    if "wealthy" in types: return f'{name} lowers their voice. "Do you understand what this could do to your reputation?"'
    return f"{name} reacts with concern, confusion, and emotion."

@reaction.command(name="parent", description="Generate parent reaction based on saved parent type")
async def reaction_parent(interaction: discord.Interaction, parent_id_or_name: Optional[str] = None):
    parents = get_bucket("parents", uid(interaction))
    if not parents: await send(interaction, "Parent Reaction", "No saved parents yet. Use `/add parent` first."); return
    if parent_id_or_name:
        found = find_item(parents, parent_id_or_name)
        if not found: await interaction.response.send_message("Parent not found.", ephemeral=True); return
        _, parent_item = found
    else: parent_item = random.choice(list(parents.values()))
    text = parent_reaction_text(parent_item); add_timeline(uid(interaction), text, "reaction"); await send(interaction, "Parent Reaction", text)
@reaction.command(name="partner", description="Generate partner reaction")
async def reaction_partner(interaction: discord.Interaction):
    text = random.choice(["They become protective and ask what is needed.", "They go quiet, overwhelmed but clearly trying.", "They get jealous before they can stop themselves.", "They softly promise they are not leaving."])
    add_timeline(uid(interaction), text, "reaction"); await send(interaction, "Partner Reaction", text)
@reaction.command(name="random", description="Generate random reaction")
async def reaction_random(interaction: discord.Interaction):
    text = random.choice(SOFT_EVENTS + CHAOTIC_EVENTS); add_timeline(uid(interaction), text, "reaction"); await send(interaction, "Random Reaction", text)

@baby.command(name="create", description="Create baby")
async def baby_create(interaction: discord.Interaction, name: str, parent_one: str, parent_two: Optional[str] = None):
    user = uid(interaction); bucket = get_bucket("babies", user); baby_id = make_id("baby"); temperament = random.choice(BABY_TEMPERAMENTS)
    bucket[baby_id] = {"name": name, "parent_one": parent_one, "parent_two": parent_two or "unknown", "age": "newborn", "temperament": temperament, "created_at": utc_now()}
    set_bucket("babies", user, bucket); await send(interaction, "Baby Created", f"**{name}** created.\nTemperament: **{temperament}**\nID: `{baby_id}`")
@baby.command(name="profile", description="View baby profile")
async def baby_profile(interaction: discord.Interaction, baby_id_or_name: str):
    found = find_item(get_bucket("babies", uid(interaction)), baby_id_or_name)
    if not found: await interaction.response.send_message("Baby not found.", ephemeral=True); return
    baby_id, item = found; text = f"ID: `{baby_id}`\nName: **{item.get('name')}**\nAge: {item.get('age')}\nParents: {item.get('parent_one')} + {item.get('parent_two')}\nTemperament: {item.get('temperament')}"
    await send(interaction, "Baby Profile", text)
@relationship.command(name="event", description="Generate relationship event")
async def relationship_event(interaction: discord.Interaction):
    text = random.choice(RELATIONSHIP_EVENTS); add_timeline(uid(interaction), text, "relationship"); await send(interaction, "Relationship Event", text)
@celebrity.command(name="event", description="Generate celebrity event")
async def celebrity_event(interaction: discord.Interaction):
    text = random.choice(CELEBRITY_EVENTS); add_timeline(uid(interaction), text, "celebrity"); await send(interaction, "Celebrity Event", text)
@generate.command(name="drama", description="Generate drama prompt")
async def generate_drama(interaction: discord.Interaction): await send(interaction, "Generated Drama", random.choice(CHAOTIC_EVENTS + RELATIONSHIP_EVENTS + CELEBRITY_EVENTS))
@generate.command(name="soft", description="Generate soft prompt")
async def generate_soft(interaction: discord.Interaction): await send(interaction, "Generated Soft Moment", random.choice(SOFT_EVENTS))
@timeline.command(name="add", description="Add timeline note")
async def timeline_add(interaction: discord.Interaction, text: str, category: str = "custom"):
    add_timeline(uid(interaction), text, category); await send(interaction, "Timeline Added", text)
@timeline.command(name="view", description="View timeline")
async def timeline_view(interaction: discord.Interaction):
    entries = load_data("timelines").get(uid(interaction), [])
    if not entries: await interaction.response.send_message("Timeline is empty.", ephemeral=True); return
    lines = [f"**{i+1}.** [{entry.get('category')}] {entry.get('text')}" for i, entry in enumerate(entries[-20:])]
    await send(interaction, "Timeline", "\n".join(lines))
@timeline.command(name="clear", description="Clear timeline")
async def timeline_clear(interaction: discord.Interaction):
    data = load_data("timelines"); data[uid(interaction)] = []; save_data("timelines", data); await send(interaction, "Timeline Cleared", "Timeline cleared.")
@settings.command(name="realism", description="Set realism")
@app_commands.choices(level=LEVEL_CHOICES)
async def settings_realism(interaction: discord.Interaction, level: app_commands.Choice[str]):
    data = load_data("settings"); data.setdefault(uid(interaction), DEFAULT_SETTINGS.copy()); data[uid(interaction)]["realism"] = level.value; save_data("settings", data); await send(interaction, "Realism Updated", f"Realism set to **{level.name}**.")
@settings.command(name="chaos", description="Set chaos")
@app_commands.choices(level=LEVEL_CHOICES)
async def settings_chaos(interaction: discord.Interaction, level: app_commands.Choice[str]):
    data = load_data("settings"); data.setdefault(uid(interaction), DEFAULT_SETTINGS.copy()); data[uid(interaction)]["chaos"] = level.value; save_data("settings", data); await send(interaction, "Chaos Updated", f"Chaos set to **{level.name}**.")

for group in [character, add_group, parent, doctor, medical, start, pregnancy, baby, relationship, celebrity, reaction, timeline, generate, settings]:
    bot.tree.add_command(group)

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Add BOT_TOKEN in Render Environment Variables.")
bot.run(TOKEN)
