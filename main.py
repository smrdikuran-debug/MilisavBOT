import discord
from discord.ext import commands, tasks
import datetime
import asyncio
from webserver import keep_alive

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

# Čuvanje AFK stanja i vremena
afk_users = {}  # {user_id: join_time}
kds = {}        # {user_id: "kills/deaths/assists"}

SILENT_FILE = "silent.mp3"

@bot.event
async def on_ready():
    print(f"{bot.user} je online!")
    keep_alive()  # Start Flask server
    print("Webserver startovan!")

# --- /kirkafk ---
@bot.slash_command(name="kirkafk", description="Uđi AFK u kanal")
async def kirkafk(ctx: discord.ApplicationContext):
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        vc = await channel.connect()
        afk_users[ctx.author.id] = datetime.datetime.now()

        await ctx.respond(f"We are Charlie Kirk ✊ {ctx.author.name} je sada AFK u {channel.name}!")

        # Pokreni silent zvuk ciklično
        while ctx.author.id in afk_users:
            vc.play(discord.FFmpegPCMAudio(SILENT_FILE))
            await asyncio.sleep(10)  # 10 sekundi
    else:
        await ctx.respond(f"We are Charlie Kirk ✊ Morate biti u glasovnom kanalu da biste koristili ovu komandu.")

# --- /kirkleave ---
@bot.slash_command(name="kirkleave", description="Izađi iz AFK kanala")
async def kirkleave(ctx: discord.ApplicationContext):
    if ctx.author.id in afk_users:
        afk_users.pop(ctx.author.id)
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        await ctx.respond("We are Charlie Kirk ✊ Izlazite iz AFK!")
    else:
        await ctx.respond("We are Charlie Kirk ✊ Niste u AFK modu.")

# --- /kirktime ---
@bot.slash_command(name="kirktime", description="Vreme provedeno u AFK")
async def kirktime(ctx: discord.ApplicationContext):
    if ctx.author.id in afk_users:
        delta = datetime.datetime.now() - afk_users[ctx.author.id]
        await ctx.respond(f"We are Charlie Kirk ✊ Proveli ste {str(delta).split('.')[0]} u kanalu!")
    else:
        await ctx.respond("We are Charlie Kirk ✊ Niste u AFK modu.")

# --- /kd ---
@bot.slash_command(name="kd", description="Prikaz K/D/A")
async def kd(ctx: discord.ApplicationContext):
    msg = "We are Charlie Kirk ✊ K/D/A članova:\n"
    for user_id, stats in kds.items():
        user = await bot.fetch_user(user_id)
        msg += f"{user.name}: {stats}\n"
    await ctx.respond(msg)

# --- /setkd ---
@bot.slash_command(name="setkd", description="Postavi K/D/A nekome")
async def setkd(ctx: discord.ApplicationContext, member: discord.Member, kd: str):
    kds[member.id] = kd
    await ctx.respond(f"We are Charlie Kirk ✊ Postavljen K/D/A za {member.name} na {kd}!")

# --- /kojepedofil ---
@bot.slash_command(name="kojepedofil", description="Tajne informacije")
async def kojepedofil(ctx: discord.ApplicationContext):
    await ctx.respond("We are Charlie Kirk ✊ Rade je pedofil")

# --- /crnisok ---
@bot.slash_command(name="crnisok", description="Reminder crni sok")
async def crnisok(ctx: discord.ApplicationContext, tip: str):
    if tip.lower() == "frizider":
        await ctx.respond("We are Charlie Kirk ✊ Reminder: crni sok u frizideru za 150 minuta!")
        await asyncio.sleep(150*60)
        await ctx.channel.send("We are Charlie Kirk ✊ Vrijeme je za crni sok iz frizidera!")
    elif tip.lower() == "zamrzivac":
        await ctx.respond("We are Charlie Kirk ✊ Reminder: crni sok u zamrzivacu za 80 minuta!")
        await asyncio.sleep(80*60)
        await ctx.channel.send("We are Charlie Kirk ✊ Vrijeme je za crni sok iz zamrzivaca!")
    else:
        await ctx.respond("We are Charlie Kirk ✊ Nevalidan tip, koristi frizider ili zamrzivac.")

# --- /kirk ---
@bot.slash_command(name="kirk", description="Prikaz komandi")
async def kirk(ctx: discord.ApplicationContext):
    komande = "/kirkafk, /kirkleave, /kirktime, /kd, /setkd, /kojepedofil, /crnisok, /kirk"
    await ctx.respond(f"We are Charlie Kirk ✊ Komande: {komande}")

# --- Start bota ---
import os
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
