import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import random
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data.json"

print("BOT IS STARTING...")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

if TOKEN is None:
    print("ERROR: BOT_TOKEN is missing.")
else:
    print("BOT_TOKEN found.")


def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)

    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_user(data, user_id):
    data.setdefault(user_id, {
        "characters": {},
        "babies": {},
        "timeline": []
    })
    return data[user_id]


GENRES = {
    "school": "School",
    "college": "College",
    "family": "Family",
    "slice_of_life": "Slice of Life",
    "teen_drama": "Teen Drama",
    "romance": "Romance",
    "celebrity": "Celebrity",
    "influencer": "Influencer",
    "medical": "Medical",
    "pregnancy": "Pregnancy",
    "hospital": "Hospital",
    "fantasy": "Fantasy",
    "supernatural": "Supernatural",
    "vampire": "Vampire",
    "werewolf": "Werewolf",
    "magic": "Witch / Magic",
    "royalty": "Royalty",
    "crime": "Crime",
    "mafia": "Mafia",
    "mystery": "Mystery",
    "apocalypse": "Apocalypse",
    "sci_fi": "Sci-Fi",
    "comedy": "Comedy",
    "parenthood": "Parenthood",
}

GENRE_CHOICES = [
    app_commands.Choice(name=label, value=value)
    for value, label in GENRES.items()
]

MOODS = [
    "soft", "tense", "chaotic", "emotional", "funny",
    "dramatic", "quiet", "romantic", "suspicious", "messy"
]

REACTIONS = [
    "They freeze for a second, clearly trying to process what just happened.",
    "They laugh nervously, but their eyes give away that they are bothered.",
    "They cross their arms and wait for an explanation.",
    "They pretend they are fine, but their voice comes out quieter than usual.",
    "They immediately change the subject, making everything feel more awkward.",
    "They step closer, lowering their voice so no one else hears.",
    "They look away, trying not to show how much it affected them.",
    "They get defensive fast, even though nobody accused them yet.",
    "They make a joke, but it lands heavier than they intended.",
    "They go completely silent, which says more than words could.",
    "They ask one simple question that makes the whole room tense.",
    "They smile like it is nothing, but their hands are shaking.",
    "They send a quick text under the table.",
    "They glance toward the exit like they need air.",
    "They soften immediately, realizing this is bigger than they thought."
]

EVENTS = {
    "school": [
        "A rumor starts spreading in the hallway.",
        "A teacher pulls someone aside after class.",
        "Someone finds a note they were not supposed to see.",
        "A group project gets assigned with the worst possible partner.",
        "Someone’s phone buzzes loudly during a quiet test.",
        "A locker is found open with something strange inside.",
        "A friend suddenly stops talking when they walk in.",
        "A school dance announcement causes unexpected tension.",
        "Someone gets called to the office with no explanation.",
        "A private conversation gets overheard near the bathrooms."
    ],
    "college": [
        "A roommate walks in at the worst possible moment.",
        "Someone gets paired with an ex for a class project.",
        "A professor asks a question that accidentally exposes something personal.",
        "A party invite causes tension between friends.",
        "Someone misses an important lecture and needs help.",
        "A dorm rumor starts moving way too fast.",
        "A late-night study session turns emotional.",
        "Someone’s scholarship or tuition situation becomes stressful.",
        "An old friend shows up on campus unexpectedly.",
        "A group chat message gets sent to the wrong person."
    ],
    "family": [
        "A family member walks in at the worst time.",
        "Someone overhears an argument they were never meant to hear.",
        "A family secret slips out during dinner.",
        "A parent asks a question that feels way too pointed.",
        "A sibling notices something nobody else caught.",
        "A family gathering gets tense after one comment.",
        "Someone brings up the past and the room changes instantly.",
        "An unexpected relative arrives without warning.",
        "A family member tries to control the situation.",
        "Someone finally says what everyone has been avoiding."
    ],
    "slice_of_life": [
        "A normal errand turns into an unexpectedly emotional moment.",
        "Someone runs into a person they were avoiding.",
        "A quiet morning gets interrupted by a surprising call.",
        "Plans fall apart, forcing everyone to improvise.",
        "A small act of kindness hits harder than expected.",
        "Someone forgets something important.",
        "A cozy hangout turns into a serious conversation.",
        "Rain traps everyone inside together.",
        "Someone finds an old photo or memory.",
        "A casual meal reveals something personal."
    ],
    "teen_drama": [
        "A screenshot starts circulating.",
        "Someone gets left out of plans and finds out online.",
        "A friend group starts acting weird.",
        "A crush gets exposed by accident.",
        "Someone lies about where they were.",
        "A parent finds something they were not supposed to see.",
        "A party gets messy fast.",
        "Someone makes a jealous comment in public.",
        "A secret relationship almost gets revealed.",
        "Someone posts something vague, and everyone knows who it is about."
    ],
    "romance": [
        "Their partner notices something is wrong.",
        "A soft confession happens at the worst possible time.",
        "Someone from the past texts unexpectedly.",
        "A jealous look says more than anyone wants to admit.",
        "They almost kiss, but someone interrupts.",
        "One person remembers a tiny detail the other thought they forgot.",
        "An argument turns into a vulnerable moment.",
        "A date gets ruined by bad timing.",
        "Someone admits they were scared of losing the other.",
        "A quiet touch changes the entire mood."
    ],
    "celebrity": [
        "A fan gets too close and starts asking personal questions.",
        "A private photo starts trending online.",
        "A publicist calls with bad news.",
        "A fake rumor hits social media.",
        "A red carpet question gets way too personal.",
        "An ex is seen at the same event.",
        "Someone leaks a private schedule.",
        "A fan account notices something suspicious.",
        "A manager demands damage control.",
        "A viral clip takes a moment completely out of context."
    ],
    "influencer": [
        "A comment section turns messy.",
        "A brand deal suddenly becomes complicated.",
        "Someone posts a shady story.",
        "A livestream catches something private.",
        "A follower recognizes someone in the background.",
        "A collab partner starts acting fake.",
        "An old post resurfaces.",
        "A DM causes unexpected drama.",
        "A sponsorship request feels uncomfortable.",
        "Someone’s online persona cracks for a second."
    ],
    "medical": [
        "The doctor walks in with a serious expression.",
        "A nurse urgently asks everyone to clear the room.",
        "A test result comes back earlier than expected.",
        "Someone refuses to admit how much pain they are in.",
        "A monitor starts beeping unexpectedly.",
        "A family member asks for the truth.",
        "A patient says something vulnerable while half-asleep.",
        "A doctor gives instructions that change the plan.",
        "Someone has to make a difficult decision.",
        "A quiet waiting room becomes emotionally heavy."
    ],
    "pregnancy": [
        "A sudden symptom makes the room go quiet.",
        "Someone notices a small detail and starts asking questions.",
        "A private appointment reminder pops up at the worst time.",
        "A craving hits at the most inconvenient moment.",
        "Someone gets emotional over something tiny.",
        "A family member starts making assumptions.",
        "A doctor asks a question that changes the mood.",
        "A baby name conversation gets unexpectedly serious.",
        "Someone worries quietly but tries not to show it.",
        "A sudden wave of nausea interrupts everything."
    ],
    "hospital": [
        "A waiting room announcement makes everyone tense.",
        "Someone comes back from triage looking worried.",
        "A nurse asks who the emergency contact is.",
        "A doctor says they need to run more tests.",
        "A loved one tries to stay calm but clearly is not.",
        "Someone gets lost trying to find the right room.",
        "A quiet hallway conversation turns emotional.",
        "A discharge plan changes unexpectedly.",
        "Someone receives a call from the hospital.",
        "A visitor shows up uninvited."
    ],
    "fantasy": [
        "The air suddenly feels strange, like magic is nearby.",
        "A glowing mark appears on someone’s skin.",
        "A creature watches quietly from the trees.",
        "An old prophecy is mentioned at the worst time.",
        "The ground hums with ancient energy.",
        "A hidden door reveals itself.",
        "Someone’s magic reacts without permission.",
        "A forbidden object starts glowing.",
        "A messenger arrives from another realm.",
        "The sky changes color for only a moment."
    ],
    "supernatural": [
        "The room temperature drops suddenly.",
        "A shadow moves where no one should be standing.",
        "Someone hears their name whispered.",
        "A mirror reflects something that is not there.",
        "A candle blows out on its own.",
        "Someone’s eyes flash unnaturally.",
        "An old symbol appears overnight.",
        "A dream feels too real to ignore.",
        "Something scratches at the door.",
        "A protective charm breaks without warning."
    ],
    "vampire": [
        "A heartbeat becomes impossible to ignore.",
        "Someone notices the lack of reflection.",
        "A drop of blood changes the whole atmosphere.",
        "An old hunger stirs at the worst time.",
        "A vampire recognizes a scent from the past.",
        "Someone asks why they never seem to age.",
        "A forbidden feeding almost happens.",
        "Sunlight becomes a sudden problem.",
        "A rival vampire sends a warning.",
        "Someone discovers bite marks."
    ],
    "werewolf": [
        "The moon feels too close tonight.",
        "Someone’s temper spikes without warning.",
        "A low growl slips out before they can stop it.",
        "A scent triggers an intense reaction.",
        "The pack senses something is wrong.",
        "Claws appear for half a second.",
        "Someone challenges authority.",
        "A protective instinct takes over.",
        "A transformation nearly happens in public.",
        "An old pack rival arrives."
    ],
    "magic": [
        "A spell backfires in a very inconvenient way.",
        "Someone’s emotions accidentally trigger magic.",
        "A charm reveals a hidden truth.",
        "A potion has unexpected side effects.",
        "A familiar reacts to danger before anyone else does.",
        "A magical object refuses to be touched.",
        "A curse starts showing symptoms.",
        "Someone senses another witch nearby.",
        "An old book opens by itself.",
        "A protective spell cracks."
    ],
    "royalty": [
        "A royal advisor delivers troubling news.",
        "A formal dinner becomes politically tense.",
        "Someone questions the heir’s choices.",
        "A secret relationship risks becoming public.",
        "A rival court sends a gift with a hidden warning.",
        "A coronation detail goes wrong.",
        "A guard overhears something dangerous.",
        "A marriage proposal becomes a political weapon.",
        "A royal sibling makes a bold move.",
        "A servant knows more than they should."
    ],
    "crime": [
        "Someone finds evidence that should not exist.",
        "A witness changes their story.",
        "A phone call warns them to stop asking questions.",
        "A hidden camera catches something important.",
        "Someone lies too quickly.",
        "A locked drawer is found open.",
        "A detective notices one detail everyone missed.",
        "A suspect knows information they should not know.",
        "A car follows too closely.",
        "Someone disappears before they can explain."
    ],
    "mafia": [
        "A boss calls for a private meeting.",
        "Someone walks into the room with blood on their sleeve.",
        "A debt comes due.",
        "A rival family sends a warning.",
        "A bodyguard refuses to leave someone alone.",
        "A deal goes wrong.",
        "Someone breaks a rule they cannot take back.",
        "An arranged marriage conversation starts.",
        "A secret alliance gets exposed.",
        "A trusted person may be a traitor."
    ],
    "mystery": [
        "A clue appears where nobody expected it.",
        "Someone’s alibi starts falling apart.",
        "A locked room is suddenly open.",
        "An anonymous note arrives.",
        "A missing item returns in the wrong place.",
        "Someone recognizes a symbol from the past.",
        "A witness remembers one strange detail.",
        "A recording cuts off at the worst moment.",
        "Someone lies about knowing the victim.",
        "A hidden passage is discovered."
    ],
    "apocalypse": [
        "A radio signal cuts through the static.",
        "Supplies go missing overnight.",
        "Someone spots movement beyond the fence.",
        "A stranger begs to be let in.",
        "The group has to decide who to trust.",
        "A safe zone rumor spreads.",
        "A storm forces everyone to shelter together.",
        "Someone hides an injury.",
        "The power flickers back on unexpectedly.",
        "A map reveals a dangerous shortcut."
    ],
    "sci_fi": [
        "The ship’s system gives a warning nobody recognizes.",
        "An android says something too human.",
        "A distress signal arrives from deep space.",
        "A lab door opens by itself.",
        "Someone’s memory file has been altered.",
        "A planet scan reveals life signs.",
        "A time glitch repeats the same moment.",
        "A device activates without permission.",
        "A crew member hides alien contamination.",
        "An AI refuses an order."
    ],
    "comedy": [
        "Someone dramatically misunderstands the situation.",
        "A serious moment gets ruined by the worst timing.",
        "Someone walks in holding something completely random.",
        "A plan works, but in the dumbest possible way.",
        "Someone tries to lie and fails immediately.",
        "A pet causes total chaos.",
        "A group chat message exposes everyone.",
        "Someone panics over a very fixable problem.",
        "A dramatic entrance goes wrong.",
        "Someone gives advice they absolutely should not give."
    ],
    "parenthood": [
        "A child asks a question nobody is ready for.",
        "Someone has a tiny meltdown over bedtime.",
        "A school call interrupts the day.",
        "A parent realizes they forgot something important.",
        "A kid repeats something they were not supposed to hear.",
        "A family outing turns chaotic.",
        "Someone gets protective fast.",
        "A quiet parenting moment becomes emotional.",
        "A child notices tension between adults.",
        "A bedtime story turns into a serious conversation."
    ],
    "default": [
        "Something unexpected happens.",
        "The room suddenly goes quiet.",
        "Someone receives a message that changes the mood.",
        "A small detail changes everything.",
        "Someone says the wrong thing at the wrong time."
    ]
}

BABY_TEMPERAMENTS = [
    "calm", "fussy", "clingy", "dramatic",
    "sleepy", "curious", "playful", "sensitive"
]

BABY_EVENTS = {
    "calm": [
        "The baby softly whimpers but stays mostly calm.",
        "The baby watches everyone quietly with sleepy eyes.",
        "The baby relaxes when someone gently rocks them.",
        "The baby blinks slowly, completely unbothered by the chaos."
    ],
    "fussy": [
        "The baby starts crying hard and kicking their little legs.",
        "The baby refuses to settle, no matter what anyone tries.",
        "The baby squirms and fusses until someone changes positions.",
        "The baby gets upset the second the room gets too loud."
    ],
    "clingy": [
        "The baby cries the second they are put down.",
        "The baby reaches out immediately, wanting to be held again.",
        "The baby calms only when pressed close to someone’s chest.",
        "The baby grips onto a shirt like they have no plans to let go."
    ],
    "dramatic": [
        "The baby gives one tiny whine, then completely loses it.",
        "The baby throws their little arms up like the world has ended.",
        "The baby pauses mid-cry to check if everyone is watching.",
        "The baby acts deeply betrayed by a minor inconvenience."
    ],
    "sleepy": [
        "The baby rubs their face and fights sleep.",
        "The baby dozes off for two seconds, then wakes up offended.",
        "The baby yawns dramatically but refuses to close their eyes.",
        "The baby melts into someone’s arms, almost asleep."
    ],
    "curious": [
        "The baby reaches for something and fusses when they cannot grab it.",
        "The baby stares at everything like they are studying the room.",
        "The baby turns toward every sound with wide eyes.",
        "The baby tries to grab someone’s necklace, hair, or sleeve."
    ],
    "playful": [
        "The baby babbles happily and wants attention.",
        "The baby squeals and kicks happily when someone smiles at them.",
        "The baby starts laughing at absolutely nothing.",
        "The baby plays with their own hands like it is the funniest thing ever."
    ],
    "sensitive": [
        "The baby startles and begins crying softly.",
        "The baby gets overwhelmed and needs a quiet moment.",
        "The baby’s little lip trembles before they start crying.",
        "The baby calms when the room gets softer and quieter."
    ]
}


def build_rp_event(genres):
    genre = random.choice(genres) if genres else "default"
    genre_name = GENRES.get(genre, "General")
    event_text = random.choice(EVENTS.get(genre, EVENTS["default"]))
    mood = random.choice(MOODS)
    reaction = random.choice(REACTIONS)

    return (
        f"**{genre_name} RP Event**\n"
        f"**Mood:** {mood.title()}\n\n"
        f"{event_text}\n\n"
        f"**Reaction:** {reaction}"
    )


class ConfirmCharacterView(discord.ui.View):
    def __init__(self, character_data):
        super().__init__(timeout=120)
        self.character_data = character_data

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        user = get_user(data, str(interaction.user.id))

        user["characters"][self.character_data["name"].lower()] = self.character_data
        save_data(data)

        await interaction.response.edit_message(
            content=f"✅ Character **{self.character_data['name']}** created and saved!",
            view=None
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="❌ Character creation cancelled.",
            view=None
        )


class CharacterCreateModal(discord.ui.Modal, title="Create Character"):
    def __init__(self, genres):
        super().__init__()
        self.genres = genres

    name = discord.ui.TextInput(
        label="Character Name",
        placeholder="Example: Emmy Nelson",
        required=True,
        max_length=100
    )

    age = discord.ui.TextInput(
        label="Age",
        placeholder="Example: 17, 21, immortal, unknown",
        required=True,
        max_length=50
    )

    gender = discord.ui.TextInput(
        label="Gender",
        placeholder="Example: Female, Male, Nonbinary",
        required=True,
        max_length=100
    )

    face_claim = discord.ui.TextInput(
        label="Face Claim / Appearance",
        placeholder="Example: Zendaya inspired, brown curls, soft glam",
        required=False,
        max_length=200
    )

    notes = discord.ui.TextInput(
        label="Personality / Backstory / Notes",
        placeholder="Add personality, family, secrets, RP details, etc.",
        required=False,
        style=discord.TextStyle.paragraph,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        genre_names = [GENRES.get(g, g) for g in self.genres]

        character_data = {
            "name": str(self.name),
            "age": str(self.age),
            "gender": str(self.gender),
            "face_claim": str(self.face_claim),
            "genres": self.genres,
            "notes": str(self.notes),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        msg = (
            f"Create this character?\n\n"
            f"**Name:** {character_data['name']}\n"
            f"**Age:** {character_data['age']}\n"
            f"**Gender:** {character_data['gender']}\n"
            f"**Genres:** {', '.join(genre_names)}\n"
            f"**Face Claim / Appearance:** {character_data['face_claim'] or 'None'}\n"
            f"**Notes:** {character_data['notes'] or 'None'}"
        )

        await interaction.response.send_message(
            msg,
            view=ConfirmCharacterView(character_data),
            ephemeral=True
        )


class GenreSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=label, value=value)
            for value, label in GENRES.items()
        ]

        super().__init__(
            placeholder="Pick 1 to 3 genres for this character",
            min_values=1,
            max_values=3,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CharacterCreateModal(self.values))


class GenreSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(GenreSelect())


character = app_commands.Group(name="character", description="Character commands")
baby = app_commands.Group(name="baby", description="Baby commands")
event = app_commands.Group(name="event", description="Event commands")
timeline = app_commands.Group(name="timeline", description="Timeline commands")


@bot.tree.command(name="ping", description="Test Gaia")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! Gaia is working.")


@character.command(name="create", description="Create a character")
async def character_create(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Choose up to **3 genres** for your character:",
        view=GenreSelectView(),
        ephemeral=True
    )


@character.command(name="list", description="List your characters")
async def character_list(interaction: discord.Interaction):
    data = load_data()
    user = get_user(data, str(interaction.user.id))

    if not user["characters"]:
        await interaction.response.send_message("No characters yet.", ephemeral=True)
        return

    lines = []

    for c in user["characters"].values():
        saved_genres = c.get("genres", [])

        if not saved_genres and "genre" in c:
            saved_genres = [c["genre"]]

        genre_names = [GENRES.get(g, g) for g in saved_genres]

        lines.append(
            f"- **{c['name']}** | {c['age']} | {c['gender']} | {', '.join(genre_names)}"
        )

    await interaction.response.send_message(
        f"**Your Characters:**\n" + "\n".join(lines),
        ephemeral=True
    )


@character.command(name="view", description="View one character")
async def character_view(interaction: discord.Interaction, name: str):
    data = load_data()
    user = get_user(data, str(interaction.user.id))
    character_data = user["characters"].get(name.lower())

    if not character_data:
        await interaction.response.send_message("Character not found.", ephemeral=True)
        return

    saved_genres = character_data.get("genres", [])

    if not saved_genres and "genre" in character_data:
        saved_genres = [character_data["genre"]]

    genre_names = [GENRES.get(g, g) for g in saved_genres]

    msg = (
        f"**{character_data['name']}**\n\n"
        f"**Age:** {character_data['age']}\n"
        f"**Gender:** {character_data['gender']}\n"
        f"**Genres:** {', '.join(genre_names)}\n"
        f"**Face Claim / Appearance:** {character_data.get('face_claim') or 'None'}\n"
        f"**Notes:** {character_data.get('notes') or 'None'}"
    )

    await interaction.response.send_message(msg, ephemeral=True)


@character.command(name="event", description="Generate an event for one character")
async def character_event(interaction: discord.Interaction, name: str):
    data = load_data()
    user = get_user(data, str(interaction.user.id))
    character_data = user["characters"].get(name.lower())

    if not character_data:
        await interaction.response.send_message("Character not found.", ephemeral=True)
        return

    genres = character_data.get("genres", [])
    result = build_rp_event(genres)

    await interaction.response.send_message(
        f"**For {character_data['name']}:**\n\n{result}"
    )


@baby.command(name="create", description="Create a baby")
async def baby_create(
    interaction: discord.Interaction,
    name: str,
    age: str = "newborn",
    parent: str = "unknown"
):
    data = load_data()
    user = get_user(data, str(interaction.user.id))

    temp = random.choice(BABY_TEMPERAMENTS)

    user["babies"][name.lower()] = {
        "name": name,
        "age": age,
        "parent": parent,
        "temperament": temp,
        "revealed": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    save_data(data)

    await interaction.response.send_message(
        f"👶 Baby **{name}** created. Temperament is **hidden**."
    )


@baby.command(name="event", description="Generate baby event")
async def baby_event(interaction: discord.Interaction, name: str):
    data = load_data()
    user = get_user(data, str(interaction.user.id))
    baby_data = user["babies"].get(name.lower())

    if not baby_data:
        await interaction.response.send_message("Baby not found.", ephemeral=True)
        return

    temperament = baby_data["temperament"]
    chosen_event = random.choice(BABY_EVENTS.get(temperament, BABY_EVENTS["calm"]))
    reaction = random.choice(REACTIONS)

    await interaction.response.send_message(
        f"**{baby_data['name']} Baby Event**\n\n"
        f"{chosen_event}\n\n"
        f"**Adult Reaction:** {reaction}"
    )


@baby.command(name="reveal", description="Reveal baby temperament")
async def baby_reveal(interaction: discord.Interaction, name: str):
    data = load_data()
    user = get_user(data, str(interaction.user.id))
    baby_data = user["babies"].get(name.lower())

    if not baby_data:
        await interaction.response.send_message("Baby not found.", ephemeral=True)
        return

    baby_data["revealed"] = True
    save_data(data)

    await interaction.response.send_message(
        f"👀 **{baby_data['name']}** temperament is **{baby_data['temperament']}**."
    )


@baby.command(name="list", description="List your babies")
async def baby_list(interaction: discord.Interaction):
    data = load_data()
    user = get_user(data, str(interaction.user.id))

    if not user["babies"]:
        await interaction.response.send_message("No babies yet.", ephemeral=True)
        return

    lines = []

    for b in user["babies"].values():
        temp = b["temperament"] if b.get("revealed") else "hidden"
        lines.append(
            f"- **{b['name']}** | Age: {b['age']} | Parent: {b['parent']} | Temperament: {temp}"
        )

    await interaction.response.send_message(
        f"**Your Babies:**\n" + "\n".join(lines),
        ephemeral=True
    )


@event.command(name="generate", description="Generate RP event by genre")
@app_commands.choices(genre=GENRE_CHOICES)
async def event_generate(interaction: discord.Interaction, genre: app_commands.Choice[str]):
    result = build_rp_event([genre.value])
    await interaction.response.send_message(result)


@event.command(name="random", description="Generate a random RP event")
async def event_random(interaction: discord.Interaction):
    genre = random.choice(list(GENRES.keys()))
    result = build_rp_event([genre])
    await interaction.response.send_message(result)


@timeline.command(name="add", description="Add to timeline")
async def timeline_add(interaction: discord.Interaction, note: str):
    data = load_data()
    user = get_user(data, str(interaction.user.id))

    user["timeline"].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "note": note
    })

    save_data(data)

    await interaction.response.send_message("✅ Added to timeline.")


@timeline.command(name="view", description="View timeline")
async def timeline_view(interaction: discord.Interaction):
    data = load_data()
    user = get_user(data, str(interaction.user.id))

    if not user["timeline"]:
        await interaction.response.send_message("Timeline is empty.", ephemeral=True)
        return

    msg = "\n".join(
        [
            f"- {t['date']}: {t['note']}"
            for t in user["timeline"][-10:]
        ]
    )

    await interaction.response.send_message(
        f"**Timeline:**\n{msg}",
        ephemeral=True
    )


bot.tree.add_command(character)
bot.tree.add_command(baby)
bot.tree.add_command(event)
bot.tree.add_command(timeline)


@bot.event
async def on_ready():
    try:
        print(f"Logged in as {bot.user}")

        synced = await bot.tree.sync()

        print(f"Synced {len(synced)} global commands")
        print("Slash commands are ready.")

    except Exception as e:
        print(f"Sync failed: {e}")


if TOKEN:
    bot.run(TOKEN)
else:
    print("Bot cannot run because BOT_TOKEN is missing.")