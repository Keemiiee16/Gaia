
"""
Gaia RP Bot — Full Single-File JSON Version
Includes:
- JSON storage
- cross-server user memory
- /character create with 3-genre dropdown + popup form
- baby temperament fixed as /baby temperament roll/view/change/reveal
- pregnancy, baby, parent, school, celebrity, medical, relationship, event, reaction, timeline, generation, settings systems

requirements.txt:
discord.py

Render Environment Variable:
BOT_TOKEN = your token

Start command:
python bot.py
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


# ============================================================
# CONFIG
# ============================================================

TOKEN = os.getenv("BOT_TOKEN")

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

FILES = {
    "characters": DATA_DIR / "characters.json",
    "babies": DATA_DIR / "babies.json",
    "parents": DATA_DIR / "parents.json",
    "pregnancies": DATA_DIR / "pregnancies.json",
    "relationships": DATA_DIR / "relationships.json",
    "timelines": DATA_DIR / "timelines.json",
    "settings": DATA_DIR / "settings.json",
}

DEFAULT_SETTINGS = {
    "tone": "dramatic",
    "genre": "slice_of_life",
    "privacy": "private",
    "realism": "medium",
    "chaos": "medium",
}

GENRE_SELECT_OPTIONS = [
    discord.SelectOption(label="Slice of Life", value="slice_of_life"),
    discord.SelectOption(label="School Drama", value="school_drama"),
    discord.SelectOption(label="Celebrity Drama", value="celebrity_drama"),
    discord.SelectOption(label="Romance", value="romance"),
    discord.SelectOption(label="Family Drama", value="family_drama"),
    discord.SelectOption(label="Medical Drama", value="medical_drama"),
    discord.SelectOption(label="Fantasy", value="fantasy"),
    discord.SelectOption(label="Chaotic RP", value="chaotic_rp"),
]

GENRE_CHOICES = [
    app_commands.Choice(name="Slice of Life", value="slice_of_life"),
    app_commands.Choice(name="School Drama", value="school_drama"),
    app_commands.Choice(name="Celebrity Drama", value="celebrity_drama"),
    app_commands.Choice(name="Romance", value="romance"),
    app_commands.Choice(name="Family Drama", value="family_drama"),
    app_commands.Choice(name="Medical Drama", value="medical_drama"),
    app_commands.Choice(name="Fantasy", value="fantasy"),
    app_commands.Choice(name="Chaotic RP", value="chaotic_rp"),
]

TONE_CHOICES = [
    app_commands.Choice(name="Soft", value="soft"),
    app_commands.Choice(name="Dramatic", value="dramatic"),
    app_commands.Choice(name="Chaotic", value="chaotic"),
]

LEVEL_CHOICES = [
    app_commands.Choice(name="Low", value="low"),
    app_commands.Choice(name="Medium", value="medium"),
    app_commands.Choice(name="High", value="high"),
]

PRIVACY_CHOICES = [
    app_commands.Choice(name="Private", value="private"),
    app_commands.Choice(name="Public", value="public"),
]


# ============================================================
# STORAGE HELPERS
# ============================================================

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_file(name: str) -> None:
    path = FILES[name]
    if not path.exists():
        path.write_text("{}", encoding="utf-8")


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


def get_user_bucket(name: str, user_id: str) -> Dict[str, Any]:
    data = load_data(name)
    data.setdefault(user_id, {})
    save_data(name, data)
    return data[user_id]


def set_user_bucket(name: str, user_id: str, bucket: Dict[str, Any]) -> None:
    data = load_data(name)
    data[user_id] = bucket
    save_data(name, data)


def add_timeline(user_id: str, text: str, category: str = "general") -> None:
    data = load_data("timelines")
    data.setdefault(user_id, [])
    data[user_id].append({
        "id": make_id("timeline"),
        "category": category,
        "text": text,
        "time": utc_now(),
    })
    save_data("timelines", data)


def find_item(bucket: Dict[str, Any], item_id_or_name: str) -> Optional[tuple[str, Dict[str, Any]]]:
    target = item_id_or_name.lower().strip()
    if item_id_or_name in bucket:
        return item_id_or_name, bucket[item_id_or_name]
    for item_id, item in bucket.items():
        names = [
            str(item.get("name", "")),
            str(item.get("character", "")),
            str(item.get("character_one", "")),
            str(item.get("character_two", "")),
            str(item.get("title", "")),
        ]
        if any(n.lower() == target for n in names):
            return item_id, item
    return None


def make_embed(title: str, description: str, color: int = 0xE8A2C8) -> discord.Embed:
    embed = discord.Embed(title=title, description=description[:4000], color=color)
    embed.set_footer(text="Gaia RP Bot")
    return embed


async def send_embed(interaction: discord.Interaction, title: str, text: str, ephemeral: bool = False):
    if len(text) <= 3900:
        await interaction.response.send_message(embed=make_embed(title, text), ephemeral=ephemeral)
    else:
        await interaction.response.send_message(embed=make_embed(title, text[:3900]), ephemeral=ephemeral)


def short_list(bucket: Dict[str, Any], empty: str) -> str:
    if not bucket:
        return empty
    lines = []
    for item_id, item in bucket.items():
        name = item.get("name") or item.get("character") or item.get("title") or item_id
        extra = []
        if "age" in item:
            extra.append(f"age {item['age']}")
        if "status" in item:
            extra.append(str(item["status"]))
        if "weeks" in item:
            extra.append(f"{item.get('weeks', 0)}w {item.get('days', 0)}d")
        tail = f" — {', '.join(extra)}" if extra else ""
        lines.append(f"`{item_id}`: **{name}**{tail}")
    return "\n".join(lines)


def set_setting(user_id: str, key: str, value: str) -> None:
    data = load_data("settings")
    current = DEFAULT_SETTINGS.copy()
    current.update(data.get(user_id, {}))
    current[key] = value
    data[user_id] = current
    save_data("settings", data)


# ============================================================
# RANDOM CONTENT
# ============================================================

BABY_TEMPERAMENTS = ["calm", "clingy", "chaotic", "playful", "shy", "sensitive", "curious", "dramatic"]

REACTIONS = {
    "random": [
        "looks shocked and needs a second to process it.",
        "goes quiet, clearly hurt but trying to stay calm.",
        "gets defensive and immediately starts arguing.",
        "softens and offers comfort instead of judgment.",
        "panics, pacing like they do not know what to do.",
    ],
    "parent": [
        "freezes, then demands the truth immediately.",
        "is disappointed but still tries to protect them.",
        "starts asking too many questions because something feels off.",
        "gets emotional and says they only want them safe.",
    ],
    "partner": [
        "becomes protective and asks what they need.",
        "gets overwhelmed and goes quiet.",
        "reacts with jealousy before they can stop themselves.",
        "softly says they are not going anywhere.",
    ],
    "sibling": ["immediately gets defensive on their behalf.", "starts teasing, then realizes it is serious.", "warns them not to lie again."],
    "bestfriend": ["grabs their hand and says they will figure it out together.", "gasps loudly and asks for every detail.", "starts planning damage control immediately."],
    "rival": ["smirks like they just found new ammunition.", "pretends to be innocent while clearly enjoying the drama.", "spreads just enough information to cause chaos."],
    "teacher": ["pulls them aside and asks what is really going on.", "notices the behavior change immediately.", "offers a nurse pass and a quiet warning."],
    "doctor": ["keeps their voice calm while explaining the situation.", "orders another checkup to be safe.", "asks direct questions that make the room tense."],
    "fan": ["posts a dramatic theory online within minutes.", "defends them fiercely in the comments.", "turns one tiny moment into a viral thread."],
    "paparazzi": ["keeps snapping photos even when asked to stop.", "shouts a question designed to get a reaction.", "posts a blurry picture with a messy caption."],
    "stranger": ["stares for too long and makes the moment awkward.", "steps in to help without asking too many questions.", "whispers to someone nearby."],
    "crowd": ["goes silent all at once.", "starts whispering from every direction.", "erupts into gasps and phone cameras."],
}

BABY_EVENTS = [
    "The baby refuses to sleep and keeps everyone awake.",
    "The baby throws food everywhere during mealtime.",
    "The baby starts crying as soon as the room gets quiet.",
    "The baby laughs uncontrollably at the worst possible moment.",
    "The baby reaches for one parent and ignores everyone else.",
]

PREGNANCY_SYMPTOMS = ["morning sickness", "fatigue", "dizziness", "mood swings", "food aversions", "back pain", "cravings", "heartburn", "emotional crying", "baby kicks"]
PREGNANCY_CRAVINGS = ["pickles", "ice cream", "spicy noodles", "burgers", "sour candy", "fruit", "chips", "chocolate milk", "fries", "cereal at midnight"]
PREGNANCY_EVENTS = [
    "Morning sickness hits unexpectedly.",
    "A sudden craving becomes impossible to ignore.",
    "Someone notices a small behavior change and starts asking questions.",
    "A parent becomes suspicious after connecting the dots.",
    "A rumor starts spreading before anyone confirms anything.",
    "The baby kicks for the first time during an emotional conversation.",
    "A private appointment almost gets exposed.",
]
PREGNANCY_COMPLICATIONS = ["fainting episode", "false labor", "hospital monitoring scare", "stress-related symptoms", "high blood pressure scare", "early contractions", "severe dizziness"]

SCHOOL_EVENTS = {
    "event": ["A normal school day turns messy when a rumor spreads fast.", "A teacher notices tension between two students.", "Someone gets called to the office at the worst time."],
    "class": ["A class discussion gets personal and awkward.", "Someone gets paired with the person they are avoiding.", "A teacher asks a question that accidentally exposes drama."],
    "lunch": ["Lunch gets tense when someone brings up last night.", "A table goes silent when the wrong person walks up.", "Someone overhears a secret near the vending machines."],
    "hallway": ["The hallway erupts in whispers as someone walks by.", "Two people almost collide while avoiding eye contact.", "A locker note gets found by the wrong person."],
    "teacher": ["A teacher pulls them aside with concern.", "A teacher catches suspicious behavior and asks questions.", "A teacher warns them that people are starting to notice."],
    "rumor": ["A rumor mutates into something worse by third period.", "Someone claims they have proof, even though they do not.", "Screenshots start circulating in a group chat."],
    "fight": ["A fight nearly breaks out before staff intervene.", "Someone shoves past another person and the hallway freezes.", "A verbal argument turns loud enough for teachers to hear."],
    "detention": ["Detention gets assigned after someone talks back.", "Two rivals end up stuck in detention together.", "A detention note gets sent home."],
    "nurse": ["The nurse notices symptoms that do not add up.", "Someone gets sent to the nurse after looking pale.", "The nurse quietly asks if there is anything they need to talk about."],
    "exam": ["An exam becomes stressful enough to trigger a breakdown.", "Someone blanks out during a test.", "A bad grade causes a bigger argument at home."],
    "secret": ["A secret almost slips during class.", "Someone finds out something they were never supposed to know.", "A hidden truth becomes one conversation away from exposure."],
}

CELEBRITY_EVENTS = {
    "event": ["A public appearance goes wrong in a way nobody expected.", "A private moment gets caught on camera.", "A small mistake becomes a trending topic."],
    "fan": ["Fans start defending them fiercely online.", "A fan theory gets way too close to the truth.", "A fan notices a tiny detail in a photo."],
    "paparazzi": ["Paparazzi corner them outside a restaurant.", "A blurry photo gets posted with a messy headline.", "A paparazzi question hits a nerve."],
    "interview": ["An interview question turns painfully personal.", "They dodge a question, but everyone notices.", "A quote gets taken out of context."],
    "scandal": ["A scandal breaks right before a major event.", "Old footage resurfaces and causes chaos.", "A rumor becomes headline-level drama."],
    "rumor": ["A celebrity gossip page posts a suspicious blind item.", "Fans connect dots that were supposed to stay hidden.", "A rumor spreads faster than the team can deny it."],
    "livestream": ["A livestream catches something in the background.", "A comment section spirals while they are still live.", "Someone says the wrong thing on livestream."],
    "viral": ["A clip goes viral for all the wrong reasons.", "A soft moment becomes an overnight fan edit.", "A messy reaction becomes a meme."],
    "security": ["Security has to step in when the crowd gets too close.", "A tense moment happens backstage.", "A security guard quietly warns them to leave now."],
}

MEDICAL_EVENTS = {
    "visit": ["The visit starts routine but the doctor asks more questions than expected.", "A waiting room moment turns awkward.", "Someone comes along for support but makes things more tense."],
    "checkup": ["The checkup is mostly fine, but one detail needs follow-up.", "The doctor gives reassurance, but also a serious warning.", "Vitals are checked twice just to be safe."],
    "injury": ["A sprained ankle ruins the day.", "A minor concussion scare sends everyone into panic mode.", "A cut looks worse than it is, but the reaction is dramatic."],
    "sickness": ["A fever keeps getting worse.", "Nausea hits at the worst possible time.", "Someone tries to hide that they are sick."],
    "surgery": ["A minor surgery gets scheduled.", "The waiting room feels heavier than expected.", "Someone tries to act brave before the procedure."],
    "results": ["Results come back and make the room go quiet.", "The doctor says the results are not bad, but not nothing.", "Someone opens the results before they are ready."],
    "followup": ["A follow-up gets scheduled after a concerning detail.", "The doctor wants to monitor things a little longer.", "Someone forgets the appointment and causes stress."],
    "emergency": ["An emergency visit turns the whole night upside down.", "Someone collapses and everyone panics.", "The hospital lights make everything feel too real."],
    "hospital": ["The hospital stay makes everyone emotional.", "A family argument happens in the hallway.", "Someone refuses to leave the bedside."],
    "recovery": ["Recovery is slow, frustrating, and emotional.", "Someone overdoes it and gets scolded.", "A soft care-taking moment happens during recovery."],
}

RELATIONSHIP_EVENTS = {
    "argument": ["A small disagreement explodes into a real argument.", "Old feelings get dragged into a new fight.", "Someone says something they instantly regret."],
    "jealousy": ["Jealousy shows before they can hide it.", "A harmless conversation gets misread.", "Someone asks, 'Why were they looking at you like that?'"],
    "soft": ["A quiet moment turns tender.", "Someone reaches for their hand without saying anything.", "They share a look that says more than words."],
    "breakup": ["The breakup conversation starts with too much silence.", "Someone walks away before hearing the full truth.", "A relationship cracks under pressure."],
    "proposal": ["A proposal moment arrives unexpectedly.", "Someone rehearses a speech and forgets every word.", "The room holds its breath."],
    "secret": ["A relationship secret nearly comes out.", "Someone finds a message they should not have seen.", "One person knows more than they are admitting."],
    "reaction": ["The reaction is softer than expected.", "The reaction is worse than feared.", "Someone tries to stay calm but fails."],
}

GENERAL_EVENTS = {
    "random": ["Something unexpected interrupts the day.", "A tiny detail turns into a much bigger issue.", "The wrong person shows up at the worst time."],
    "family": ["A family dinner turns tense.", "A parent asks a question nobody wants to answer.", "A sibling reveals something at the worst possible moment."],
    "public": ["A public scene draws attention.", "Strangers start staring.", "Someone records before anyone can stop them."],
    "drama": ["A secret gets exposed.", "A text gets sent to the wrong person.", "Two people finally confront each other."],
    "soft": ["A quiet moment gives everyone room to breathe.", "Someone offers comfort without needing an explanation.", "A small act of care means more than expected."],
    "chaotic": ["Everything goes wrong at once.", "Someone screams, someone laughs, and someone leaves.", "The situation spirals before anyone can fix it."],
    "emergency": ["An emergency pulls everyone into action.", "A phone call changes the entire mood.", "Someone has to make a decision immediately."],
}

GENERATION_PROMPTS = {
    "scene": ["Write a scene where a secret almost comes out in public.", "Write a scene where two characters have to pretend everything is fine.", "Write a scene where the room gets tense after one question."],
    "drama": ["Generate drama involving a rumor, a secret, and a bad time to be honest.", "Generate messy family drama with emotional consequences.", "Generate a public confrontation that changes the story."],
    "soft": ["Generate a soft comfort moment after a hard day.", "Generate a quiet scene where someone finally feels safe.", "Generate a tender moment between two characters."],
    "conflict": ["Generate a conflict where both people think they are right.", "Generate an argument caused by fear, not hate.", "Generate tension between loyalty and honesty."],
    "secret": ["Generate a secret that would change how everyone sees the character.", "Generate a hidden truth that is close to being exposed.", "Generate a private message that should never be found."],
    "twist": ["Generate a twist that makes the current storyline messier.", "Generate a reveal nobody expected.", "Generate a consequence from an old decision."],
    "dialogue": ['"Tell me the truth. Not the pretty version."', '"I was trying to protect you, but I think I made it worse."', '"You do not get to disappear and come back like nothing happened."'],
    "starter": ["Starter: The hallway went quiet the second they walked in.", "Starter: The phone buzzed once, and suddenly everything felt different.", "Starter: Nobody was supposed to see them there."],
    "consequence": ["Consequence: Someone loses trust.", "Consequence: The rumor reaches a parent or authority figure.", "Consequence: A relationship changes permanently."],
}


# ============================================================
# BOT SETUP
# ============================================================

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
        print(f"Slash command sync failed: {e}")
    print(f"Gaia is online as {bot.user}.")


# ============================================================
# COMMAND GROUPS
# ============================================================

character = app_commands.Group(name="character", description="Character system")
baby = app_commands.Group(name="baby", description="Baby system")
baby_temperament_group = app_commands.Group(name="temperament", description="Baby temperament commands")
parent = app_commands.Group(name="parent", description="Parent system")
school = app_commands.Group(name="school", description="School RP system")
celebrity = app_commands.Group(name="celebrity", description="Celebrity RP system")
medical = app_commands.Group(name="medical", description="Medical RP system")
relationship = app_commands.Group(name="relationship", description="Relationship system")
event = app_commands.Group(name="event", description="Event system")
reaction = app_commands.Group(name="reaction", description="Reaction system")
timeline = app_commands.Group(name="timeline", description="Timeline system")
generate = app_commands.Group(name="generate", description="Generation system")
settings = app_commands.Group(name="settings", description="Settings system")
pregnancy = app_commands.Group(name="pregnancy", description="Pregnancy system")


# ============================================================
# CHARACTER SYSTEM WITH DROPDOWN + FORM
# ============================================================

class CharacterCreateModal(discord.ui.Modal, title="Create Character"):
    def __init__(self, genres: List[str]):
        super().__init__()
        self.genres = genres

        self.character_name = discord.ui.TextInput(label="Name", placeholder="Character name", max_length=100, required=True)
        self.character_age = discord.ui.TextInput(label="Age", placeholder="Character age", max_length=20, required=True)
        self.character_gender = discord.ui.TextInput(label="Gender", placeholder="Character gender", max_length=80, required=True)
        self.character_appearance = discord.ui.TextInput(label="Appearance", placeholder="Describe their look, style, hair, features, etc.", style=discord.TextStyle.paragraph, max_length=1000, required=True)
        self.character_backstory = discord.ui.TextInput(label="Backstory", placeholder="Describe their history, family, struggles, goals, etc.", style=discord.TextStyle.paragraph, max_length=2000, required=True)

        self.add_item(self.character_name)
        self.add_item(self.character_age)
        self.add_item(self.character_gender)
        self.add_item(self.character_appearance)
        self.add_item(self.character_backstory)

    async def on_submit(self, interaction: discord.Interaction):
        user = uid(interaction)
        bucket = get_user_bucket("characters", user)
        cid = make_id("char")

        name = str(self.character_name.value)
        age = str(self.character_age.value)
        gender = str(self.character_gender.value)
        appearance = str(self.character_appearance.value)
        backstory = str(self.character_backstory.value)

        bucket[cid] = {
            "name": name,
            "age": age,
            "gender": gender,
            "appearance": appearance,
            "backstory": backstory,
            "genres": self.genres,
            "genre": ", ".join(self.genres),
            "personality": "",
            "notes": "",
            "selected": False,
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }

        set_user_bucket("characters", user, bucket)
        add_timeline(user, f"Created character {name}.", "character")

        text = (
            f"**{name}** has been created.\n"
            f"ID: `{cid}`\n"
            f"Age: **{age}**\n"
            f"Gender: **{gender}**\n"
            f"Genres: **{', '.join(self.genres)}**\n\n"
            f"**Appearance:** {appearance[:900]}\n\n"
            f"**Backstory:** {backstory[:900]}"
        )
        await interaction.response.send_message(embed=make_embed("Character Created", text))


class CharacterGenreSelect(discord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Pick up to 3 genres for this character...",
            min_values=1,
            max_values=3,
            options=GENRE_SELECT_OPTIONS,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CharacterCreateModal(self.values))


class CharacterGenreView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(CharacterGenreSelect())


@character.command(name="create", description="Create a character with genre dropdown and form")
async def character_create(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Choose up to **3 genres** for your character. Then Gaia will open the character form.",
        view=CharacterGenreView(),
        ephemeral=True,
    )


@character.command(name="edit", description="Edit a character")
async def character_edit(interaction: discord.Interaction, character_id_or_name: str, name: Optional[str] = None, age: Optional[str] = None, gender: Optional[str] = None, appearance: Optional[str] = None, backstory: Optional[str] = None, personality: Optional[str] = None):
    user = uid(interaction)
    bucket = get_user_bucket("characters", user)
    found = find_item(bucket, character_id_or_name)
    if not found:
        await interaction.response.send_message("Character not found.", ephemeral=True)
        return
    cid, item = found
    updates = {"name": name, "age": age, "gender": gender, "appearance": appearance, "backstory": backstory, "personality": personality}
    for key, value in updates.items():
        if value is not None:
            item[key] = value
    item["updated_at"] = utc_now()
    bucket[cid] = item
    set_user_bucket("characters", user, bucket)
    add_timeline(user, f"Edited character {item.get('name', cid)}.", "character")
    await interaction.response.send_message(embed=make_embed("Character Updated", f"Updated **{item.get('name', cid)}**."))


@character.command(name="delete", description="Delete a character")
async def character_delete(interaction: discord.Interaction, character_id_or_name: str):
    user = uid(interaction)
    bucket = get_user_bucket("characters", user)
    found = find_item(bucket, character_id_or_name)
    if not found:
        await interaction.response.send_message("Character not found.", ephemeral=True)
        return
    cid, item = found
    name = item.get("name", cid)
    del bucket[cid]
    set_user_bucket("characters", user, bucket)
    add_timeline(user, f"Deleted character {name}.", "character")
    await interaction.response.send_message(embed=make_embed("Character Deleted", f"Deleted **{name}**."))


@character.command(name="list", description="List your characters")
async def character_list(interaction: discord.Interaction):
    await send_embed(interaction, "Characters", short_list(get_user_bucket("characters", uid(interaction)), "No characters found."))


@character.command(name="profile", description="View character profile")
async def character_profile(interaction: discord.Interaction, character_id_or_name: str):
    bucket = get_user_bucket("characters", uid(interaction))
    found = find_item(bucket, character_id_or_name)
    if not found:
        await interaction.response.send_message("Character not found.", ephemeral=True)
        return
    cid, item = found
    genres = item.get("genre") or ", ".join(item.get("genres", [])) or "N/A"
    text = (
        f"ID: `{cid}`\n"
        f"Name: **{item.get('name', 'Unknown')}**\n"
        f"Age: {item.get('age', 'Unknown')}\n"
        f"Gender: {item.get('gender', 'N/A')}\n"
        f"Genres: {genres}\n\n"
        f"**Personality:** {item.get('personality', 'N/A') or 'N/A'}\n\n"
        f"**Appearance:** {item.get('appearance', 'N/A')}\n\n"
        f"**Backstory:** {item.get('backstory', 'N/A')}\n\n"
        f"**Notes:** {item.get('notes', 'None') or 'None'}"
    )
    await interaction.response.send_message(embed=make_embed("Character Profile", text))


@character.command(name="notes", description="Update character notes")
async def character_notes(interaction: discord.Interaction, character_id_or_name: str, notes: str):
    user = uid(interaction)
    bucket = get_user_bucket("characters", user)
    found = find_item(bucket, character_id_or_name)
    if not found:
        await interaction.response.send_message("Character not found.", ephemeral=True)
        return
    cid, item = found
    item["notes"] = notes
    bucket[cid] = item
    set_user_bucket("characters", user, bucket)
    await interaction.response.send_message(embed=make_embed("Notes Updated", f"Notes updated for **{item.get('name', cid)}**."))


@character.command(name="select", description="Select active character")
async def character_select(interaction: discord.Interaction, character_id_or_name: str):
    user = uid(interaction)
    bucket = get_user_bucket("characters", user)
    found = find_item(bucket, character_id_or_name)
    if not found:
        await interaction.response.send_message("Character not found.", ephemeral=True)
        return
    selected_id, selected = found
    for item in bucket.values():
        item["selected"] = False
    selected["selected"] = True
    bucket[selected_id] = selected
    set_user_bucket("characters", user, bucket)
    await interaction.response.send_message(embed=make_embed("Character Selected", f"Now selected: **{selected.get('name', selected_id)}**."))


@character.command(name="share", description="Share character profile")
async def character_share(interaction: discord.Interaction, character_id_or_name: str):
    bucket = get_user_bucket("characters", uid(interaction))
    found = find_item(bucket, character_id_or_name)
    if not found:
        await interaction.response.send_message("Character not found.", ephemeral=True)
        return
    _, item = found
    genres = item.get("genre") or ", ".join(item.get("genres", [])) or "N/A"
    text = (
        f"**{item.get('name', 'Unknown')}**, age {item.get('age', 'Unknown')}\n"
        f"**Gender:** {item.get('gender', 'N/A')}\n"
        f"**Genres:** {genres}\n"
        f"**Appearance:** {item.get('appearance', 'N/A')}\n"
        f"**Backstory:** {item.get('backstory', 'N/A')}"
    )
    await interaction.response.send_message(embed=make_embed("Shared Character", text))


# ============================================================
# BABY SYSTEM
# ============================================================

@baby.command(name="create", description="Create a baby")
async def baby_create(interaction: discord.Interaction, name: str, parent_one: str, parent_two: Optional[str] = None):
    user = uid(interaction)
    bucket = get_user_bucket("babies", user)
    bid = make_id("baby")
    temperament = random.choice(BABY_TEMPERAMENTS)
    bucket[bid] = {
        "name": name,
        "age": "newborn",
        "parent_one": parent_one,
        "parent_two": parent_two or "unknown",
        "temperament": temperament,
        "temperament_hidden": False,
        "profile": "",
        "created_at": utc_now(),
    }
    set_user_bucket("babies", user, bucket)
    add_timeline(user, f"Baby {name} was created.", "baby")
    await interaction.response.send_message(embed=make_embed("Baby Created", f"**{name}** created.\nTemperament: **{temperament}**\nID: `{bid}`"))


@baby.command(name="profile", description="View baby profile")
async def baby_profile(interaction: discord.Interaction, baby_id_or_name: str):
    bucket = get_user_bucket("babies", uid(interaction))
    found = find_item(bucket, baby_id_or_name)
    if not found:
        await interaction.response.send_message("Baby not found.", ephemeral=True)
        return
    bid, item = found
    temper = "Hidden" if item.get("temperament_hidden") else item.get("temperament", "unknown")
    text = f"ID: `{bid}`\nName: **{item.get('name')}**\nAge: {item.get('age')}\nParents: {item.get('parent_one')} + {item.get('parent_two')}\nTemperament: **{temper}**\nProfile: {item.get('profile') or 'N/A'}"
    await interaction.response.send_message(embed=make_embed("Baby Profile", text))


@baby.command(name="delete", description="Delete baby")
async def baby_delete(interaction: discord.Interaction, baby_id_or_name: str):
    user = uid(interaction)
    bucket = get_user_bucket("babies", user)
    found = find_item(bucket, baby_id_or_name)
    if not found:
        await interaction.response.send_message("Baby not found.", ephemeral=True)
        return
    bid, item = found
    del bucket[bid]
    set_user_bucket("babies", user, bucket)
    add_timeline(user, f"Deleted baby {item.get('name', bid)}.", "baby")
    await interaction.response.send_message(embed=make_embed("Baby Deleted", f"Deleted **{item.get('name', bid)}**."))


@baby.command(name="age", description="Update baby age")
async def baby_age(interaction: discord.Interaction, baby_id_or_name: str, age: str):
    user = uid(interaction)
    bucket = get_user_bucket("babies", user)
    found = find_item(bucket, baby_id_or_name)
    if not found:
        await interaction.response.send_message("Baby not found.", ephemeral=True)
        return
    bid, item = found
    item["age"] = age
    bucket[bid] = item
    set_user_bucket("babies", user, bucket)
    add_timeline(user, f"{item.get('name')} is now {age}.", "baby")
    await interaction.response.send_message(embed=make_embed("Baby Age Updated", f"**{item.get('name')}** is now **{age}**."))


@baby.command(name="update", description="Update baby profile")
async def baby_update(interaction: discord.Interaction, baby_id_or_name: str, profile: str):
    user = uid(interaction)
    bucket = get_user_bucket("babies", user)
    found = find_item(bucket, baby_id_or_name)
    if not found:
        await interaction.response.send_message("Baby not found.", ephemeral=True)
        return
    bid, item = found
    item["profile"] = profile
    bucket[bid] = item
    set_user_bucket("babies", user, bucket)
    await interaction.response.send_message(embed=make_embed("Baby Updated", f"Updated **{item.get('name')}**."))


@baby.command(name="event", description="Generate baby event")
async def baby_event(interaction: discord.Interaction):
    text = random.choice(BABY_EVENTS)
    add_timeline(uid(interaction), text, "baby")
    await interaction.response.send_message(embed=make_embed("Baby Event", text))


@baby.command(name="reaction", description="Generate baby reaction")
async def baby_reaction(interaction: discord.Interaction):
    text = random.choice([
        "The baby reaches up and refuses to let go.",
        "The baby cries when the room gets too loud.",
        "The baby giggles at someone being dramatic.",
        "The baby hides their face against their parent.",
    ])
    add_timeline(uid(interaction), text, "baby")
    await interaction.response.send_message(embed=make_embed("Baby Reaction", text))


@baby_temperament_group.command(name="roll", description="Roll a random baby temperament")
async def baby_temperament_roll(interaction: discord.Interaction):
    await interaction.response.send_message(embed=make_embed("Baby Temperament", random.choice(BABY_TEMPERAMENTS)))


@baby_temperament_group.command(name="view", description="View baby temperament")
async def baby_temperament_view(interaction: discord.Interaction, baby_id_or_name: str):
    bucket = get_user_bucket("babies", uid(interaction))
    found = find_item(bucket, baby_id_or_name)
    if not found:
        await interaction.response.send_message("Baby not found.", ephemeral=True)
        return
    _, item = found
    temper = "Hidden" if item.get("temperament_hidden") else item.get("temperament", "unknown")
    await interaction.response.send_message(embed=make_embed("Temperament", f"**{item.get('name')}**: {temper}"))


@baby_temperament_group.command(name="change", description="Change baby temperament")
async def baby_temperament_change(interaction: discord.Interaction, baby_id_or_name: str, temperament: str):
    user = uid(interaction)
    bucket = get_user_bucket("babies", user)
    found = find_item(bucket, baby_id_or_name)
    if not found:
        await interaction.response.send_message("Baby not found.", ephemeral=True)
        return
    bid, item = found
    item["temperament"] = temperament
    item["temperament_hidden"] = False
    bucket[bid] = item
    set_user_bucket("babies", user, bucket)
    await interaction.response.send_message(embed=make_embed("Temperament Changed", f"**{item.get('name')}** is now **{temperament}**."))


@baby_temperament_group.command(name="reveal", description="Reveal baby temperament")
async def baby_temperament_reveal(interaction: discord.Interaction, baby_id_or_name: str):
    user = uid(interaction)
    bucket = get_user_bucket("babies", user)
    found = find_item(bucket, baby_id_or_name)
    if not found:
        await interaction.response.send_message("Baby not found.", ephemeral=True)
        return
    bid, item = found
    item["temperament_hidden"] = False
    bucket[bid] = item
    set_user_bucket("babies", user, bucket)
    await interaction.response.send_message(embed=make_embed("Temperament Revealed", f"**{item.get('name')}** is **{item.get('temperament')}**."))


baby.add_command(baby_temperament_group)


# ============================================================
# PARENT SYSTEM
# ============================================================

@parent.command(name="add", description="Add parent")
async def parent_add(interaction: discord.Interaction, name: str, relationship_to_character: str, personality: str):
    user = uid(interaction)
    bucket = get_user_bucket("parents", user)
    pid = make_id("parent")
    bucket[pid] = {"name": name, "relationship_to_character": relationship_to_character, "personality": personality, "support": 50, "suspicion": 0, "created_at": utc_now()}
    set_user_bucket("parents", user, bucket)
    await interaction.response.send_message(embed=make_embed("Parent Added", f"Added **{name}**.\nID: `{pid}`"))


@parent.command(name="edit", description="Edit parent")
async def parent_edit(interaction: discord.Interaction, parent_id_or_name: str, personality: Optional[str] = None, support: Optional[int] = None, suspicion: Optional[int] = None):
    user = uid(interaction)
    bucket = get_user_bucket("parents", user)
    found = find_item(bucket, parent_id_or_name)
    if not found:
        await interaction.response.send_message("Parent not found.", ephemeral=True)
        return
    pid, item = found
    if personality is not None:
        item["personality"] = personality
    if support is not None:
        item["support"] = support
    if suspicion is not None:
        item["suspicion"] = suspicion
    bucket[pid] = item
    set_user_bucket("parents", user, bucket)
    await interaction.response.send_message(embed=make_embed("Parent Updated", f"Updated **{item.get('name')}**."))


@parent.command(name="delete", description="Delete parent")
async def parent_delete(interaction: discord.Interaction, parent_id_or_name: str):
    user = uid(interaction)
    bucket = get_user_bucket("parents", user)
    found = find_item(bucket, parent_id_or_name)
    if not found:
        await interaction.response.send_message("Parent not found.", ephemeral=True)
        return
    pid, item = found
    del bucket[pid]
    set_user_bucket("parents", user, bucket)
    await interaction.response.send_message(embed=make_embed("Parent Deleted", f"Deleted **{item.get('name', pid)}**."))


@parent.command(name="list", description="List parents")
async def parent_list(interaction: discord.Interaction):
    await send_embed(interaction, "Parents", short_list(get_user_bucket("parents", uid(interaction)), "No parents found."))


@parent.command(name="profile", description="View parent profile")
async def parent_profile(interaction: discord.Interaction, parent_id_or_name: str):
    bucket = get_user_bucket("parents", uid(interaction))
    found = find_item(bucket, parent_id_or_name)
    if not found:
        await interaction.response.send_message("Parent not found.", ephemeral=True)
        return
    pid, item = found
    text = f"ID: `{pid}`\nName: **{item.get('name')}**\nRelation: {item.get('relationship_to_character')}\nPersonality: {item.get('personality')}\nSupport: {item.get('support')}\nSuspicion: {item.get('suspicion')}"
    await interaction.response.send_message(embed=make_embed("Parent Profile", text))


async def parent_random(interaction: discord.Interaction, title: str):
    text = random.choice(REACTIONS["parent"])
    add_timeline(uid(interaction), text, "parent")
    await interaction.response.send_message(embed=make_embed(title, text))


@parent.command(name="event")
async def parent_event(interaction: discord.Interaction): await parent_random(interaction, "Parent Event")
@parent.command(name="reaction")
async def parent_reaction(interaction: discord.Interaction): await parent_random(interaction, "Parent Reaction")
@parent.command(name="suspicion")
async def parent_suspicion(interaction: discord.Interaction): await parent_random(interaction, "Parent Suspicion")
@parent.command(name="confrontation")
async def parent_confrontation(interaction: discord.Interaction): await parent_random(interaction, "Parent Confrontation")
@parent.command(name="support")
async def parent_support(interaction: discord.Interaction):
    text = random.choice(["A parent chooses support over punishment.", "A parent quietly says, 'I am upset, but I love you.'", "A parent steps in to protect them from the fallout.", "A parent offers help, even though they are scared too."])
    add_timeline(uid(interaction), text, "parent")
    await interaction.response.send_message(embed=make_embed("Parent Support", text))


# ============================================================
# SIMPLE EVENT HELPERS
# ============================================================

async def send_random_event(interaction: discord.Interaction, title: str, category: str, pool: List[str]):
    text = random.choice(pool)
    add_timeline(uid(interaction), text, category)
    await interaction.response.send_message(embed=make_embed(title, text))


# School commands
@school.command(name="event")
async def school_event(interaction: discord.Interaction): await send_random_event(interaction, "School Event", "school", SCHOOL_EVENTS["event"])
@school.command(name="class")
async def school_class(interaction: discord.Interaction): await send_random_event(interaction, "Class Event", "school", SCHOOL_EVENTS["class"])
@school.command(name="lunch")
async def school_lunch(interaction: discord.Interaction): await send_random_event(interaction, "Lunch Event", "school", SCHOOL_EVENTS["lunch"])
@school.command(name="hallway")
async def school_hallway(interaction: discord.Interaction): await send_random_event(interaction, "Hallway Event", "school", SCHOOL_EVENTS["hallway"])
@school.command(name="teacher")
async def school_teacher(interaction: discord.Interaction): await send_random_event(interaction, "Teacher Event", "school", SCHOOL_EVENTS["teacher"])
@school.command(name="rumor")
async def school_rumor(interaction: discord.Interaction): await send_random_event(interaction, "School Rumor", "school", SCHOOL_EVENTS["rumor"])
@school.command(name="fight")
async def school_fight(interaction: discord.Interaction): await send_random_event(interaction, "School Fight", "school", SCHOOL_EVENTS["fight"])
@school.command(name="detention")
async def school_detention(interaction: discord.Interaction): await send_random_event(interaction, "Detention", "school", SCHOOL_EVENTS["detention"])
@school.command(name="nurse")
async def school_nurse(interaction: discord.Interaction): await send_random_event(interaction, "School Nurse", "school", SCHOOL_EVENTS["nurse"])
@school.command(name="exam")
async def school_exam(interaction: discord.Interaction): await send_random_event(interaction, "School Exam", "school", SCHOOL_EVENTS["exam"])
@school.command(name="secret")
async def school_secret(interaction: discord.Interaction): await send_random_event(interaction, "School Secret", "school", SCHOOL_EVENTS["secret"])

# Celebrity commands
@celebrity.command(name="event")
async def celebrity_event(interaction: discord.Interaction): await send_random_event(interaction, "Celebrity Event", "celebrity", CELEBRITY_EVENTS["event"])
@celebrity.command(name="fan")
async def celebrity_fan(interaction: discord.Interaction): await send_random_event(interaction, "Fan Event", "celebrity", CELEBRITY_EVENTS["fan"])
@celebrity.command(name="paparazzi")
async def celebrity_paparazzi(interaction: discord.Interaction): await send_random_event(interaction, "Paparazzi Event", "celebrity", CELEBRITY_EVENTS["paparazzi"])
@celebrity.command(name="interview")
async def celebrity_interview(interaction: discord.Interaction): await send_random_event(interaction, "Interview Event", "celebrity", CELEBRITY_EVENTS["interview"])
@celebrity.command(name="scandal")
async def celebrity_scandal(interaction: discord.Interaction): await send_random_event(interaction, "Scandal Event", "celebrity", CELEBRITY_EVENTS["scandal"])
@celebrity.command(name="rumor")
async def celebrity_rumor(interaction: discord.Interaction): await send_random_event(interaction, "Celebrity Rumor", "celebrity", CELEBRITY_EVENTS["rumor"])
@celebrity.command(name="livestream")
async def celebrity_livestream(interaction: discord.Interaction): await send_random_event(interaction, "Livestream Event", "celebrity", CELEBRITY_EVENTS["livestream"])
@celebrity.command(name="viral")
async def celebrity_viral(interaction: discord.Interaction): await send_random_event(interaction, "Viral Event", "celebrity", CELEBRITY_EVENTS["viral"])
@celebrity.command(name="security")
async def celebrity_security(interaction: discord.Interaction): await send_random_event(interaction, "Security Event", "celebrity", CELEBRITY_EVENTS["security"])

# Medical commands
@medical.command(name="visit")
async def medical_visit(interaction: discord.Interaction): await send_random_event(interaction, "Medical Visit", "medical", MEDICAL_EVENTS["visit"])
@medical.command(name="checkup")
async def medical_checkup(interaction: discord.Interaction): await send_random_event(interaction, "Medical Checkup", "medical", MEDICAL_EVENTS["checkup"])
@medical.command(name="injury")
async def medical_injury(interaction: discord.Interaction): await send_random_event(interaction, "Medical Injury", "medical", MEDICAL_EVENTS["injury"])
@medical.command(name="sickness")
async def medical_sickness(interaction: discord.Interaction): await send_random_event(interaction, "Medical Sickness", "medical", MEDICAL_EVENTS["sickness"])
@medical.command(name="surgery")
async def medical_surgery(interaction: discord.Interaction): await send_random_event(interaction, "Medical Surgery", "medical", MEDICAL_EVENTS["surgery"])
@medical.command(name="results")
async def medical_results(interaction: discord.Interaction): await send_random_event(interaction, "Medical Results", "medical", MEDICAL_EVENTS["results"])
@medical.command(name="followup")
async def medical_followup(interaction: discord.Interaction): await send_random_event(interaction, "Medical Follow-up", "medical", MEDICAL_EVENTS["followup"])
@medical.command(name="emergency")
async def medical_emergency(interaction: discord.Interaction): await send_random_event(interaction, "Medical Emergency", "medical", MEDICAL_EVENTS["emergency"])
@medical.command(name="hospital")
async def medical_hospital(interaction: discord.Interaction): await send_random_event(interaction, "Hospital Event", "medical", MEDICAL_EVENTS["hospital"])
@medical.command(name="recovery")
async def medical_recovery(interaction: discord.Interaction): await send_random_event(interaction, "Medical Recovery", "medical", MEDICAL_EVENTS["recovery"])


# Relationship commands
@relationship.command(name="add", description="Add relationship")
async def relationship_add(interaction: discord.Interaction, character_one: str, character_two: str, status: str):
    user = uid(interaction)
    bucket = get_user_bucket("relationships", user)
    rid = make_id("rel")
    bucket[rid] = {"name": f"{character_one} + {character_two}", "character_one": character_one, "character_two": character_two, "status": status, "affection": 50, "trust": 50, "jealousy": 0, "created_at": utc_now()}
    set_user_bucket("relationships", user, bucket)
    add_timeline(user, f"Relationship added: {character_one} + {character_two} ({status}).", "relationship")
    await interaction.response.send_message(embed=make_embed("Relationship Added", f"ID: `{rid}`\n**{character_one} + {character_two}** — {status}"))


@relationship.command(name="edit", description="Edit relationship")
async def relationship_edit(interaction: discord.Interaction, relationship_id_or_name: str, status: Optional[str] = None, affection: Optional[int] = None, trust: Optional[int] = None, jealousy: Optional[int] = None):
    user = uid(interaction)
    bucket = get_user_bucket("relationships", user)
    found = find_item(bucket, relationship_id_or_name)
    if not found:
        await interaction.response.send_message("Relationship not found.", ephemeral=True)
        return
    rid, item = found
    if status is not None: item["status"] = status
    if affection is not None: item["affection"] = affection
    if trust is not None: item["trust"] = trust
    if jealousy is not None: item["jealousy"] = jealousy
    bucket[rid] = item
    set_user_bucket("relationships", user, bucket)
    await interaction.response.send_message(embed=make_embed("Relationship Updated", f"Updated `{rid}`."))


@relationship.command(name="status", description="View relationship status")
async def relationship_status(interaction: discord.Interaction, relationship_id_or_name: str):
    bucket = get_user_bucket("relationships", uid(interaction))
    found = find_item(bucket, relationship_id_or_name)
    if not found:
        await interaction.response.send_message("Relationship not found.", ephemeral=True)
        return
    rid, item = found
    text = f"ID: `{rid}`\nPair: **{item.get('character_one')} + {item.get('character_two')}**\nStatus: {item.get('status')}\nAffection: {item.get('affection')}\nTrust: {item.get('trust')}\nJealousy: {item.get('jealousy')}"
    await interaction.response.send_message(embed=make_embed("Relationship Status", text))


async def rel_event(interaction: discord.Interaction, key: str): await send_random_event(interaction, f"Relationship {key.title()}", "relationship", RELATIONSHIP_EVENTS[key])
@relationship.command(name="argument")
async def relationship_argument(interaction: discord.Interaction): await rel_event(interaction, "argument")
@relationship.command(name="jealousy")
async def relationship_jealousy(interaction: discord.Interaction): await rel_event(interaction, "jealousy")
@relationship.command(name="soft")
async def relationship_soft(interaction: discord.Interaction): await rel_event(interaction, "soft")
@relationship.command(name="breakup")
async def relationship_breakup(interaction: discord.Interaction): await rel_event(interaction, "breakup")
@relationship.command(name="proposal")
async def relationship_proposal(interaction: discord.Interaction): await rel_event(interaction, "proposal")
@relationship.command(name="secret")
async def relationship_secret(interaction: discord.Interaction): await rel_event(interaction, "secret")
@relationship.command(name="reaction")
async def relationship_reaction(interaction: discord.Interaction): await rel_event(interaction, "reaction")


# Event system
async def general_event(interaction: discord.Interaction, key: str): await send_random_event(interaction, f"{key.title()} Event", key, GENERAL_EVENTS[key])
@event.command(name="random")
async def event_random(interaction: discord.Interaction): await general_event(interaction, "random")
@event.command(name="school")
async def event_school(interaction: discord.Interaction): await send_random_event(interaction, "School Event", "school", SCHOOL_EVENTS["event"])
@event.command(name="celebrity")
async def event_celebrity(interaction: discord.Interaction): await send_random_event(interaction, "Celebrity Event", "celebrity", CELEBRITY_EVENTS["event"])
@event.command(name="medical")
async def event_medical(interaction: discord.Interaction): await send_random_event(interaction, "Medical Event", "medical", MEDICAL_EVENTS["visit"])
@event.command(name="relationship")
async def event_relationship(interaction: discord.Interaction): await send_random_event(interaction, "Relationship Event", "relationship", RELATIONSHIP_EVENTS["argument"])
@event.command(name="family")
async def event_family(interaction: discord.Interaction): await general_event(interaction, "family")
@event.command(name="public")
async def event_public(interaction: discord.Interaction): await general_event(interaction, "public")
@event.command(name="drama")
async def event_drama(interaction: discord.Interaction): await general_event(interaction, "drama")
@event.command(name="soft")
async def event_soft(interaction: discord.Interaction): await general_event(interaction, "soft")
@event.command(name="chaotic")
async def event_chaotic(interaction: discord.Interaction): await general_event(interaction, "chaotic")
@event.command(name="emergency")
async def event_emergency(interaction: discord.Interaction): await general_event(interaction, "emergency")


# Reaction system
async def reaction_send(interaction: discord.Interaction, key: str, title: str):
    real_key = "random" if key == "npc" else key
    text = random.choice(REACTIONS.get(real_key, REACTIONS["random"]))
    add_timeline(uid(interaction), text, "reaction")
    await interaction.response.send_message(embed=make_embed(title, text))

@reaction.command(name="random")
async def reaction_random(interaction: discord.Interaction): await reaction_send(interaction, "random", "Random Reaction")
@reaction.command(name="npc")
async def reaction_npc(interaction: discord.Interaction): await reaction_send(interaction, "npc", "NPC Reaction")
@reaction.command(name="parent")
async def reaction_parent(interaction: discord.Interaction): await reaction_send(interaction, "parent", "Parent Reaction")
@reaction.command(name="partner")
async def reaction_partner(interaction: discord.Interaction): await reaction_send(interaction, "partner", "Partner Reaction")
@reaction.command(name="sibling")
async def reaction_sibling(interaction: discord.Interaction): await reaction_send(interaction, "sibling", "Sibling Reaction")
@reaction.command(name="bestfriend")
async def reaction_bestfriend(interaction: discord.Interaction): await reaction_send(interaction, "bestfriend", "Best Friend Reaction")
@reaction.command(name="rival")
async def reaction_rival(interaction: discord.Interaction): await reaction_send(interaction, "rival", "Rival Reaction")
@reaction.command(name="teacher")
async def reaction_teacher(interaction: discord.Interaction): await reaction_send(interaction, "teacher", "Teacher Reaction")
@reaction.command(name="doctor")
async def reaction_doctor(interaction: discord.Interaction): await reaction_send(interaction, "doctor", "Doctor Reaction")
@reaction.command(name="fan")
async def reaction_fan(interaction: discord.Interaction): await reaction_send(interaction, "fan", "Fan Reaction")
@reaction.command(name="paparazzi")
async def reaction_paparazzi(interaction: discord.Interaction): await reaction_send(interaction, "paparazzi", "Paparazzi Reaction")
@reaction.command(name="stranger")
async def reaction_stranger(interaction: discord.Interaction): await reaction_send(interaction, "stranger", "Stranger Reaction")
@reaction.command(name="crowd")
async def reaction_crowd(interaction: discord.Interaction): await reaction_send(interaction, "crowd", "Crowd Reaction")


# Timeline system
@timeline.command(name="add", description="Add timeline entry")
async def timeline_add(interaction: discord.Interaction, text: str, category: str = "custom"):
    add_timeline(uid(interaction), text, category)
    await interaction.response.send_message(embed=make_embed("Timeline Added", text))

@timeline.command(name="view", description="View timeline")
async def timeline_view(interaction: discord.Interaction):
    entries = load_data("timelines").get(uid(interaction), [])
    if not entries:
        await interaction.response.send_message("Timeline is empty.", ephemeral=True)
        return
    lines = [f"**{i+1}.** [{e.get('category')}] {e.get('text')}" for i, e in enumerate(entries[-20:])]
    await send_embed(interaction, "Timeline", "\n".join(lines))

@timeline.command(name="delete", description="Delete timeline entry by number")
async def timeline_delete(interaction: discord.Interaction, entry_number: int):
    user = uid(interaction)
    data = load_data("timelines")
    entries = data.get(user, [])
    idx = entry_number - 1
    if idx < 0 or idx >= len(entries):
        await interaction.response.send_message("Timeline entry not found.", ephemeral=True)
        return
    removed = entries.pop(idx)
    data[user] = entries
    save_data("timelines", data)
    await interaction.response.send_message(embed=make_embed("Timeline Deleted", removed.get("text", "Deleted.")))

@timeline.command(name="clear", description="Clear timeline")
async def timeline_clear(interaction: discord.Interaction):
    data = load_data("timelines")
    data[uid(interaction)] = []
    save_data("timelines", data)
    await interaction.response.send_message(embed=make_embed("Timeline Cleared", "Your timeline has been cleared."))

@timeline.command(name="recent", description="Recent timeline")
async def timeline_recent(interaction: discord.Interaction):
    entries = load_data("timelines").get(uid(interaction), [])[-5:]
    if not entries:
        await interaction.response.send_message("No recent timeline entries.", ephemeral=True)
        return
    await interaction.response.send_message(embed=make_embed("Recent Timeline", "\n".join([f"[{e.get('category')}] {e.get('text')}" for e in entries])))


# Generation system
async def generate_send(interaction: discord.Interaction, key: str):
    text = random.choice(GENERATION_PROMPTS[key])
    add_timeline(uid(interaction), text, "generation")
    await interaction.response.send_message(embed=make_embed(f"Generated {key.title()}", text))

@generate.command(name="scene")
async def generate_scene(interaction: discord.Interaction): await generate_send(interaction, "scene")
@generate.command(name="drama")
async def generate_drama(interaction: discord.Interaction): await generate_send(interaction, "drama")
@generate.command(name="soft")
async def generate_soft(interaction: discord.Interaction): await generate_send(interaction, "soft")
@generate.command(name="conflict")
async def generate_conflict(interaction: discord.Interaction): await generate_send(interaction, "conflict")
@generate.command(name="secret")
async def generate_secret(interaction: discord.Interaction): await generate_send(interaction, "secret")
@generate.command(name="twist")
async def generate_twist(interaction: discord.Interaction): await generate_send(interaction, "twist")
@generate.command(name="dialogue")
async def generate_dialogue(interaction: discord.Interaction): await generate_send(interaction, "dialogue")
@generate.command(name="starter")
async def generate_starter(interaction: discord.Interaction): await generate_send(interaction, "starter")
@generate.command(name="consequence")
async def generate_consequence(interaction: discord.Interaction): await generate_send(interaction, "consequence")


# Settings
@settings.command(name="tone", description="Set tone")
@app_commands.choices(tone=TONE_CHOICES)
async def settings_tone(interaction: discord.Interaction, tone: app_commands.Choice[str]):
    set_setting(uid(interaction), "tone", tone.value)
    await interaction.response.send_message(embed=make_embed("Tone Updated", f"Tone set to **{tone.name}**."))

@settings.command(name="genre", description="Set genre")
@app_commands.choices(genre=GENRE_CHOICES)
async def settings_genre(interaction: discord.Interaction, genre: app_commands.Choice[str]):
    set_setting(uid(interaction), "genre", genre.value)
    await interaction.response.send_message(embed=make_embed("Genre Updated", f"Genre set to **{genre.name}**."))

@settings.command(name="privacy", description="Set privacy")
@app_commands.choices(privacy=PRIVACY_CHOICES)
async def settings_privacy(interaction: discord.Interaction, privacy: app_commands.Choice[str]):
    set_setting(uid(interaction), "privacy", privacy.value)
    await interaction.response.send_message(embed=make_embed("Privacy Updated", f"Privacy set to **{privacy.name}**."))

@settings.command(name="realism", description="Set realism")
@app_commands.choices(level=LEVEL_CHOICES)
async def settings_realism(interaction: discord.Interaction, level: app_commands.Choice[str]):
    set_setting(uid(interaction), "realism", level.value)
    await interaction.response.send_message(embed=make_embed("Realism Updated", f"Realism set to **{level.name}**."))

@settings.command(name="chaos", description="Set chaos")
@app_commands.choices(level=LEVEL_CHOICES)
async def settings_chaos(interaction: discord.Interaction, level: app_commands.Choice[str]):
    set_setting(uid(interaction), "chaos", level.value)
    await interaction.response.send_message(embed=make_embed("Chaos Updated", f"Chaos set to **{level.name}**."))

@settings.command(name="reset", description="Reset settings")
async def settings_reset(interaction: discord.Interaction):
    data = load_data("settings")
    data[uid(interaction)] = DEFAULT_SETTINGS.copy()
    save_data("settings", data)
    await interaction.response.send_message(embed=make_embed("Settings Reset", "Your Gaia settings have been reset."))


# Pregnancy system
@pregnancy.command(name="create", description="Create pregnancy storyline")
async def pregnancy_create(interaction: discord.Interaction, character: str, partner: str, weeks: int = 1, hidden: bool = False):
    user = uid(interaction)
    bucket = get_user_bucket("pregnancies", user)
    pid = make_id("preg")
    bucket[pid] = {
        "character": character,
        "partner": partner,
        "weeks": weeks,
        "days": 0,
        "hidden": hidden,
        "status": "active",
        "symptoms": [random.choice(PREGNANCY_SYMPTOMS)],
        "cravings": [random.choice(PREGNANCY_CRAVINGS)],
        "due_date": "not set",
        "created_at": utc_now(),
    }
    set_user_bucket("pregnancies", user, bucket)
    add_timeline(user, f"{character} started a pregnancy storyline with {partner}.", "pregnancy")
    await interaction.response.send_message(embed=make_embed("Pregnancy Created", f"**{character}** pregnancy storyline created.\nID: `{pid}`\nHidden: **{hidden}**"))

@pregnancy.command(name="status", description="View pregnancy status")
async def pregnancy_status(interaction: discord.Interaction, pregnancy_id_or_character: Optional[str] = None):
    bucket = get_user_bucket("pregnancies", uid(interaction))
    if not bucket:
        await interaction.response.send_message("No pregnancies found.", ephemeral=True)
        return
    if pregnancy_id_or_character:
        found = find_item(bucket, pregnancy_id_or_character)
        if not found:
            await interaction.response.send_message("Pregnancy not found.", ephemeral=True)
            return
        items = [found]
    else:
        items = list(bucket.items())
    lines = [f"`{pid}` — **{item.get('character')}** + {item.get('partner')} | {item.get('weeks')}w {item.get('days')}d | Hidden: {item.get('hidden')} | Due: {item.get('due_date')}" for pid, item in items]
    await interaction.response.send_message(embed=make_embed("Pregnancy Status", "\n".join(lines)))

@pregnancy.command(name="symptoms")
async def pregnancy_symptoms(interaction: discord.Interaction):
    text = random.choice(PREGNANCY_SYMPTOMS)
    add_timeline(uid(interaction), f"Pregnancy symptom: {text}.", "pregnancy")
    await interaction.response.send_message(embed=make_embed("Pregnancy Symptoms", text))

@pregnancy.command(name="craving")
async def pregnancy_craving(interaction: discord.Interaction):
    text = random.choice(PREGNANCY_CRAVINGS)
    add_timeline(uid(interaction), f"Pregnancy craving: {text}.", "pregnancy")
    await interaction.response.send_message(embed=make_embed("Pregnancy Craving", text))

@pregnancy.command(name="appointment")
async def pregnancy_appointment(interaction: discord.Interaction):
    await send_random_event(interaction, "Pregnancy Appointment", "pregnancy", ["The appointment is routine, but someone is nervous the whole time.", "The doctor asks careful questions and schedules a follow-up.", "Someone comes to the appointment for support and emotions rise."])

@pregnancy.command(name="ultrasound")
async def pregnancy_ultrasound(interaction: discord.Interaction):
    await send_random_event(interaction, "Ultrasound", "pregnancy", ["The ultrasound makes everything feel real for the first time.", "A tiny heartbeat fills the room and everyone goes quiet.", "The ultrasound tech smiles, but someone is overwhelmed."])

@pregnancy.command(name="event")
async def pregnancy_event(interaction: discord.Interaction):
    text = random.choice(PREGNANCY_EVENTS)
    react = random.choice(REACTIONS["random"])
    add_timeline(uid(interaction), text, "pregnancy")
    await interaction.response.send_message(embed=make_embed("Pregnancy Event", f"{text}\n\n**Reaction:** {react}"))

@pregnancy.command(name="complication")
async def pregnancy_complication(interaction: discord.Interaction):
    comp = random.choice(PREGNANCY_COMPLICATIONS)
    react = random.choice(REACTIONS["doctor"])
    add_timeline(uid(interaction), f"Pregnancy complication: {comp}.", "medical")
    await interaction.response.send_message(embed=make_embed("Pregnancy Complication", f"**{comp}**\n\nDoctor reaction: {react}"))

@pregnancy.command(name="labor")
async def pregnancy_labor(interaction: discord.Interaction):
    await send_random_event(interaction, "Labor Event", "pregnancy", ["Labor starts suddenly and nobody feels prepared.", "False alarm or not, everyone ends up at the hospital.", "The room becomes emotional as labor begins."])

@pregnancy.command(name="due_date")
async def pregnancy_due_date(interaction: discord.Interaction, pregnancy_id_or_character: str, due_date: str):
    user = uid(interaction)
    bucket = get_user_bucket("pregnancies", user)
    found = find_item(bucket, pregnancy_id_or_character)
    if not found:
        await interaction.response.send_message("Pregnancy not found.", ephemeral=True)
        return
    pid, item = found
    item["due_date"] = due_date
    bucket[pid] = item
    set_user_bucket("pregnancies", user, bucket)
    await interaction.response.send_message(embed=make_embed("Due Date Set", f"Due date set to **{due_date}** for **{item.get('character')}**."))

@pregnancy.command(name="reveal")
async def pregnancy_reveal(interaction: discord.Interaction, pregnancy_id_or_character: str):
    user = uid(interaction)
    bucket = get_user_bucket("pregnancies", user)
    found = find_item(bucket, pregnancy_id_or_character)
    if not found:
        await interaction.response.send_message("Pregnancy not found.", ephemeral=True)
        return
    pid, item = found
    item["hidden"] = False
    bucket[pid] = item
    set_user_bucket("pregnancies", user, bucket)
    add_timeline(user, f"{item.get('character')}'s pregnancy was revealed.", "pregnancy")
    await interaction.response.send_message(embed=make_embed("Pregnancy Revealed", f"**{item.get('character')}**'s pregnancy is no longer hidden."))

@pregnancy.command(name="hide")
async def pregnancy_hide(interaction: discord.Interaction, pregnancy_id_or_character: str):
    user = uid(interaction)
    bucket = get_user_bucket("pregnancies", user)
    found = find_item(bucket, pregnancy_id_or_character)
    if not found:
        await interaction.response.send_message("Pregnancy not found.", ephemeral=True)
        return
    pid, item = found
    item["hidden"] = True
    bucket[pid] = item
    set_user_bucket("pregnancies", user, bucket)
    await interaction.response.send_message(embed=make_embed("Pregnancy Hidden", f"**{item.get('character')}**'s pregnancy is now hidden."))

@pregnancy.command(name="reaction")
async def pregnancy_reaction(interaction: discord.Interaction): await reaction_send(interaction, "random", "Pregnancy Reaction")
@pregnancy.command(name="partner")
async def pregnancy_partner(interaction: discord.Interaction): await reaction_send(interaction, "partner", "Partner Pregnancy Reaction")
@pregnancy.command(name="parent")
async def pregnancy_parent(interaction: discord.Interaction): await reaction_send(interaction, "parent", "Parent Pregnancy Reaction")
@pregnancy.command(name="rumor")
async def pregnancy_rumor(interaction: discord.Interaction):
    await send_random_event(interaction, "Pregnancy Rumor", "pregnancy", ["Someone at school starts whispering that they know what is going on.", "A rumor spreads before the character is ready to tell anyone.", "Someone posts a vague message and everyone assumes the worst."])
@pregnancy.command(name="hospital")
async def pregnancy_hospital(interaction: discord.Interaction):
    await send_random_event(interaction, "Pregnancy Hospital", "medical", ["A hospital visit turns emotional fast.", "Everyone waits for updates in a tense hallway.", "The doctor says they want to monitor things just to be safe."])
@pregnancy.command(name="babykick")
async def pregnancy_babykick(interaction: discord.Interaction):
    await send_random_event(interaction, "Baby Kick", "pregnancy", ["The baby kicks during a quiet moment and everything softens.", "A baby kick interrupts an argument and leaves both people speechless.", "Someone feels the baby kick for the first time and starts crying."])
@pregnancy.command(name="names")
async def pregnancy_names(interaction: discord.Interaction):
    names = random.sample(["Amara", "Nova", "Milo", "Sienna", "Kai", "Elena", "Roman", "Luna", "Noah", "Isla", "Mateo", "Gia", "Zion", "Ari", "Celeste", "Ezra"], 5)
    await interaction.response.send_message(embed=make_embed("Baby Name Ideas", ", ".join(names)))
@pregnancy.command(name="mood")
async def pregnancy_mood(interaction: discord.Interaction):
    text = random.choice(["overwhelmed and emotional", "quietly excited", "irritable and exhausted", "soft and sentimental", "anxious but trying to stay calm", "protective of their peace"])
    add_timeline(uid(interaction), f"Pregnancy mood: {text}.", "pregnancy")
    await interaction.response.send_message(embed=make_embed("Pregnancy Mood", text))
@pregnancy.command(name="emergency")
async def pregnancy_emergency(interaction: discord.Interaction):
    await send_random_event(interaction, "Pregnancy Emergency", "emergency", ["A sudden pain sends everyone into emergency mode.", "Someone faints and the room erupts into panic.", "The hospital says to come in immediately."])
@pregnancy.command(name="timeline")
async def pregnancy_timeline(interaction: discord.Interaction, note: str):
    add_timeline(uid(interaction), note, "pregnancy")
    await interaction.response.send_message(embed=make_embed("Pregnancy Timeline Added", note))
@pregnancy.command(name="delete")
async def pregnancy_delete(interaction: discord.Interaction, pregnancy_id_or_character: str):
    user = uid(interaction)
    bucket = get_user_bucket("pregnancies", user)
    found = find_item(bucket, pregnancy_id_or_character)
    if not found:
        await interaction.response.send_message("Pregnancy not found.", ephemeral=True)
        return
    pid, item = found
    name = item.get("character", pid)
    del bucket[pid]
    set_user_bucket("pregnancies", user, bucket)
    add_timeline(user, f"Deleted pregnancy storyline for {name}.", "pregnancy")
    await interaction.response.send_message(embed=make_embed("Pregnancy Deleted", f"Deleted pregnancy storyline for **{name}**."))


# ============================================================
# REGISTER COMMAND GROUPS
# ============================================================

for group in [
    character, baby, parent, school, celebrity, medical, relationship,
    event, reaction, timeline, generate, settings, pregnancy
]:
    bot.tree.add_command(group)


# ============================================================
# RUN
# ============================================================

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Add BOT_TOKEN in Render Environment Variables.")

bot.run(TOKEN)
