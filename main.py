import discord
from discord import app_commands
from discord.ext import commands, tasks
import datetime
import asyncio
from webserver import keep_alive
import os

# --- Intents i bot ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

# --- Čuvanje stanja ---
afk_users = {}  # {user_id: join_time}
kds = {}        # {user_id: "kills/deaths/assists"}
SILENT_FILE = "silent.mp3"

# --- Task za održavanje VC alive ---
@tasks.loop(seconds=10)
async def keep_vc_alive():
    for vc in bot.voice_clients:
        if not vc.is_connected():
            await vc.disconnect()
        elif not vc.is_playing():
            vc.play(discord.FFmpegPCMAudio(SILENT_FILE))

# --- on_ready event ---
@bot.event
async def on_ready():
    print(f"{bot.user} je online!")
    keep_alive()  # Start Flask server
    print("Webserver startovan!")
    keep_vc_alive.start()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Greška pri sync komandi: {e}")

# --- Helper za crni sok reminder ---
async def crni_task(channel, tip, minutes):
    await asyncio.sleep(minutes * 60)
    await channel.send(f"Milisav 🔥 Reminder: Vreme je za crni sok iz {tip}a!")

# ----------------- SLASH KOMANDE -----------------

# /miliafk
@bot.tree.command(name="miliafk", description="Uđi AFK u kanal")
async def miliafk(interaction: discord.Interaction):
    if interaction.user.voice and interaction.user.voice.channel:
        channel = interaction.user.voice.channel
        vc = await channel.connect()
        afk_users[interaction.user.id] = datetime.datetime.now()

        # Odmah odgovor na interaction
        await interaction.response.send_message(f"Milisav 🔥 {interaction.user.name} je sada AFK u {channel.name}!")

        # Pokreni AFK loop u pozadinskom tasku
        async def afk_loop():
            while interaction.user.id in afk_users:
                if not vc.is_playing():
                    vc.play(discord.FFmpegPCMAudio(SILENT_FILE))
                await asyncio.sleep(10)

        asyncio.create_task(afk_loop())
    else:
        await interaction.response.send_message("Milisav 🔥 Morate biti u voice-u da biste koristili ovu komandu.")
# /milileave
@bot.tree.command(name="milileave", description="Izađi iz AFK kanala")
async def milileave(interaction: discord.Interaction):
    if interaction.user.id in afk_users:
        afk_users.pop(interaction.user.id)
        if interaction.user.voice and interaction.user.voice.channel:
            vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
            if vc:
                await vc.disconnect()
        await interaction.response.send_message("Milisav 🔥 Izasao iz kanala!")
    else:
        await interaction.response.send_message("Milisav 🔥 Nije u kanalu.")

# /militime
@bot.tree.command(name="militime", description="Vreme provedeno u AFK")
async def militime(interaction: discord.Interaction):
    if interaction.user.id in afk_users:
        delta = datetime.datetime.now() - afk_users[interaction.user.id]
        await interaction.response.send_message(f"Milisav 🔥 je proveo {str(delta).split('.')[0]} u kanalu!")
    else:
        await interaction.response.send_message("Milisav 🔥 Niste u AFK modu.")

# /kd
@bot.tree.command(name="kd", description="Prikaz K/D/A")
async def kd(interaction: discord.Interaction):
    if not kds:
        await interaction.response.send_message("Milisav 🔥 Nema postavljenih K/D/A.")
        return
    msg = "K/D/A članova:\n"
    for user_id, stats in kds.items():
        try:
            user = await bot.fetch_user(user_id)
            msg += f"{user.name}: {stats}\n"
        except:
            continue
    await interaction.response.send_message(msg)

# /setkd
@bot.tree.command(name="setkd", description="Postavi K/D/A nekome")
@app_commands.describe(member="Kome postavljate K/D/A", kd="Format: kills/deaths/assists")
async def setkd(interaction: discord.Interaction, member: discord.Member, kd: str):
    kds[member.id] = kd
    await interaction.response.send_message(f"Milisav 🔥 Postavljen K/D/A za {member.name} na {kd}!")

# /kojepedofil
@bot.tree.command(name="kojepedofil", description="Tajne informacije")
async def kojepedofil(interaction: discord.Interaction):
    await interaction.response.send_message("👧 Milisav 🔥 Rade je pedofil")

# /crnisok
@bot.tree.command(name="crnisok", description="Reminder crni sok")
@app_commands.describe(tip="frizider ili zamrzivac")
async def crnisok(interaction: discord.Interaction, tip: str):
    tip_lower = tip.lower()
    if tip_lower == "frizider":
        await interaction.response.send_message("Milisav 🔥 Postavljen Reminder: crni sok izvaditi iz frizidera za 150 minuta!")
        asyncio.create_task(crni_task(interaction.channel, "frizider", 150))
    elif tip_lower == "zamrzivac":
        await interaction.response.send_message("Milisav 🔥 Postavljen Reminder: crni sok izvaditi iz zamrzivaca za 80 minuta!")
        asyncio.create_task(crni_task(interaction.channel, "zamrzivac", 80))
    else:
        await interaction.response.send_message("Milisav 🔥 Nevalidan tip, koristi frizider ili zamrzivac.")

# /mili
@bot.tree.command(name="mili", description="Prikaz komandi")
async def mili(interaction: discord.Interaction):
    komande = "/miliafk, /milileave, /militime, /kd, /setkd, /kojepedofil, /crnisok, /mili"
    await interaction.response.send_message(f"Milisav 🔥 Komande: {komande}")

# ----------------- START BOTA -----------------
import os
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)

