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

if TOKEN is None:
    print("ERROR: BOT_TOKEN is missing.")
else:
    print("BOT_TOKEN found.")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


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


GENRE_CHOICES = [
    app_commands.Choice(name="School", value="school"),
    app_commands.Choice(name="College", value="college"),
    app_commands.Choice(name="Family", value="family"),
    app_commands.Choice(name="Slice of Life", value="slice_of_life"),
    app_commands.Choice(name="Teen Drama", value="teen_drama"),
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

temperaments = [
    "calm", "fussy", "clingy", "dramatic",
    "sleepy", "curious", "playful", "sensitive"
]

events = {
    "school": [
        "A rumor starts spreading in the hallway.",
        "A teacher pulls someone aside after class.",
        "Someone finds a note they were not supposed to see."
    ],
    "celebrity": [
        "A fan gets too close and starts asking personal questions.",
        "A private photo starts trending online.",
        "A publicist calls with bad news."
    ],
    "medical": [
        "The doctor walks in with a serious expression.",
        "A nurse urgently asks everyone to clear the room.",
        "A test result comes back earlier than expected."
    ],
    "romance": [
        "Their partner notices something is wrong.",
        "A soft confession happens at the worst possible time.",
        "Someone from the past texts unexpectedly."
    ],
    "family": [
        "A family member walks in at the worst time.",
        "Someone overhears an argument they were never meant to hear.",
        "A family secret slips out during dinner."
    ],
    "fantasy": [
        "The air suddenly feels strange, like magic is nearby.",
        "A glowing mark appears on someone’s skin.",
        "A creature watches quietly from the trees."
    ],
    "default": [
        "Something unexpected happens.",
        "The room suddenly goes quiet.",
        "Someone receives a message that changes the mood."
    ]
}

baby_events = {
    "calm": [
        "The baby softly whimpers but stays mostly calm.",
        "The baby watches everyone quietly with sleepy eyes."
    ],
    "fussy": [
        "The baby starts crying hard and kicking their little legs.",
        "The baby refuses to settle, no matter what anyone tries."
    ],
    "clingy": [
        "The baby cries the second they are put down.",
        "The baby reaches out immediately, wanting to be held again."
    ],
    "dramatic": [
        "The baby gives one tiny whine, then completely loses it.",
        "The baby throws their little arms up like the world has ended."
    ],
    "sleepy": [
        "The baby rubs their face and fights sleep.",
        "The baby dozes off for two seconds, then wakes up offended."
    ],
    "curious": [
        "The baby reaches for something and fusses when they cannot grab it.",
        "The baby stares at everything like they are studying the room."
    ],
    "playful": [
        "The baby babbles happily and wants attention.",
        "The baby squeals and kicks happily when someone smiles at them."
    ],
    "sensitive": [
        "The baby startles and begins crying softly.",
        "The baby gets overwhelmed and needs a quiet moment."
    ]
}


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
            content=f"✅ Character **{self.character_data['name']}** created!",
            view=None
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="❌ Cancelled.",
            view=None
        )


class CharacterCreateModal(discord.ui.Modal, title="Create Character"):
    def __init__(self, genre):
        super().__init__()
        self.genre = genre

    name = discord.ui.TextInput(label="Name", required=True)
    age = discord.ui.TextInput(label="Age", required=True)
    gender = discord.ui.TextInput(label="Gender", required=True)
    notes = discord.ui.TextInput(
        label="Notes",
        required=False,
        style=discord.TextStyle.paragraph
    )

    async def on_submit(self, interaction: discord.Interaction):
        character_data = {
            "name": str(self.name),
            "age": str(self.age),
            "gender": str(self.gender),
            "genre": self.genre,
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


character = app_commands.Group(
    name="character",
    description="Character commands"
)

baby = app_commands.Group(
    name="baby",
    description="Baby commands"
)

event = app_commands.Group(
    name="event",
    description="Event commands"
)

timeline = app_commands.Group(
    name="timeline",
    description="Timeline commands"
)


@bot.tree.command(name="ping", description="Test Gaia")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! Gaia is working.")


@character.command(name="create", description="Create a character")
@app_commands.choices(genre=GENRE_CHOICES)
async def character_create(
    interaction: discord.Interaction,
    genre: app_commands.Choice[str]
):
    await interaction.response.send_modal(CharacterCreateModal(genre.value))


@character.command(name="list", description="List your characters")
async def character_list(interaction: discord.Interaction):
    data = load_data()
    user = get_user(data, str(interaction.user.id))

    if not user["characters"]:
        await interaction.response.send_message(
            "No characters yet.",
            ephemeral=True
        )
        return

    msg = "\n".join(
        [
            f"- **{c['name']}** | {c['age']} | {c['gender']} | {c['genre']}"
            for c in user["characters"].values()
        ]
    )

    await interaction.response.send_message(f"**Your Characters:**\n{msg}")


@baby.command(name="create", description="Create a baby")
async def baby_create(
    interaction: discord.Interaction,
    name: str,
    age: str = "newborn",
    parent: str = "unknown"
):
    data = load_data()
    user = get_user(data, str(interaction.user.id))

    temp = random.choice(temperaments)

    user["babies"][name.lower()] = {
        "name": name,
        "age": age,
        "parent": parent,
        "temperament": temp,
        "revealed": False
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
        await interaction.response.send_message(
            "Baby not found.",
            ephemeral=True
        )
        return

    temperament = baby_data["temperament"]
    chosen_event = random.choice(
        baby_events.get(temperament, baby_events["calm"])
    )

    await interaction.response.send_message(
        f"**{baby_data['name']}**\n\n{chosen_event}"
    )


@baby.command(name="reveal", description="Reveal baby temperament")
async def baby_reveal(interaction: discord.Interaction, name: str):
    data = load_data()
    user = get_user(data, str(interaction.user.id))
    baby_data = user["babies"].get(name.lower())

    if not baby_data:
        await interaction.response.send_message(
            "Baby not found.",
            ephemeral=True
        )
        return

    baby_data["revealed"] = True
    save_data(data)

    await interaction.response.send_message(
        f"👀 **{baby_data['name']}** temperament is **{baby_data['temperament']}**."
    )


@event.command(name="generate", description="Generate RP event")
@app_commands.choices(genre=GENRE_CHOICES)
async def event_generate(
    interaction: discord.Interaction,
    genre: app_commands.Choice[str]
):
    pool = events.get(genre.value, events["default"])

    await interaction.response.send_message(
        f"**{genre.name} Event:**\n{random.choice(pool)}"
    )


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
        await interaction.response.send_message(
            "Timeline is empty.",
            ephemeral=True
        )
        return

    msg = "\n".join(
        [
            f"- {t['date']}: {t['note']}"
            for t in user["timeline"][-10:]
        ]
    )

    await interaction.response.send_message(f"**Timeline:**\n{msg}")


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