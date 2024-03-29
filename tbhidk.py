import asyncio
import os
import random

import discord
import youtube_dl

from discord.ext import commands
from discord.ext.commands import Bot
from discord.utils import get

from Token import token

BOT_PREFIX = '!'

bot: Bot = commands.Bot(command_prefix=BOT_PREFIX)
client = bot
voice = None
playlist = []


@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name + "\n")


@bot.command(pass_context=True, aliases=['8Ball', '8ball', 'q', 'Q', 'ask'])
async def _8ball(ctx, *, question):
    responses = ['idk', 'maybe', 'yes', 'no', 'im just a bot ok?', 'im not your mom', 'f"yolo"']
    await ctx.send(f'Answer: {random.choice(responses)}')


@bot.command(pass_context=True, aliases=['j', 'joi'])
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    await voice.disconnect()

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"The bot has connected to {channel}\n")

    await ctx.send(f"Joined {channel}")


@bot.command(pass_context=True, aliases=['l'])
async def leave(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"The bot has left {channel}")
    else:
        print("Bot was told to leave voice channel, but was not in one")
        await ctx.send("I'm not in a channel ;A;")


def play_done(ctx, loop, name):
    loop.create_task(ctx.send(f"Finished playing: {name[0]}"))
    play_next(ctx, loop)


def play_next(ctx, loop):
    if voice.is_playing():
        return
    elif len(playlist) == 0 :
        loop.create_task(ctx.send(f"Done playing"))
        print("Done playing\n")
        return

    file = playlist.pop()

    voice.play(discord.FFmpegPCMAudio(f"./music/{file}"), after=lambda e: play_done(ctx, loop, name))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

    name = file.rsplit("-", 2)

    loop.create_task(ctx.send(f"Playing: {name[0]}"))
    print(f"Playing: {name[0]}\n")


@bot.command(pass_context=True, aliases=['p'])
async def play(ctx, url: str):
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("ERROR: Music playing")
        return

    await ctx.send("Getting everything ready now")

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            playlist.append(file)
            print(playlist)
            try:
                os.renames(file, f"./music/{file}")
            except FileExistsError:
                os.remove(file)

    play_next(ctx, asyncio.get_event_loop())


@bot.command(pass_context=True, aliases=['pa'])
async def pause(ctx):
    global voice
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("paused")
        voice.pause()
        await ctx.send("Paused")
    else:
        await ctx.send("I'm not playing anything")


@bot.command(pass_context=True, aliases=['r', 're'])
async def resume(ctx):
    global voice
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("resuming")
        voice.resume()
        await ctx.send("Resuming")
    else:
        await ctx.send("Nothing is paused")


@bot.command(pass_context=True, aliases=['s', 'st'])
async def stop(ctx):
    global voice
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("stopping")
        voice.stop()


bot.run(token)
