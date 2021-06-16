import discord
from discord import guild
from discord.ext import commands, tasks
import asyncio
import os
import youtube_dl

client = commands.Bot(command_prefix= '+')

# Setting up YouTube-DL settings
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

# Tester code batch
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.idle, activity=discord.Game("with +help"))
    print("Mista is online.")

@client.command(name="ping")
async def ping(ctx):
    #Just addding this since heroku is a <REDACTED>
    await ctx.send(f"🏓 Pong with {str(round(client.latency, 2))}.")


@client.command(name="whoami")
async def whoami(ctx):
    await ctx.send(f"Mista says your username's {ctx.message.author.name}.")

@client.command()
async def clear(ctx, amount=3):
    await ctx.channel.purge(limit=amount)

# Actual music playing code
# Actual music playing code
@client.command(name="join", help="Mista joins the party!")
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("Mista thinks {} is not connected to a voice channel! :(".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
        await ctx.send(f"Connecting to {channel}")
    await channel.connect()

@client.command(name="play", help="Mista starts playing! #play 'song_url'")
async def play(ctx, url : str):
    voice_channel = discord.utils.get(ctx.guild.voice_channels)
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice is None:
        await ctx.send(f"Mista is connecting... {str(voice_channel)}")
        await join(ctx)
    else:
        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=client.loop)
            voice.play(discord.FFmpegPCMAudio(filename))
        await ctx.send('**Now playing:** {}'.format(filename))


@client.command(name="leave", help="Mista leaves...")
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send("Mista was never in the voice channel...")

@client.command(name="pause", help="Mista pauses song!")
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Mista can't pause a non-existent song...")

@client.command(name="resume", help="Mista resumes song!")
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("Mista can't resume a non-existent song...")

@client.command(name="stop", help="Mista stops!")
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()

if __name__ == "__main__":
    # FOR LOCAL TESTING
    # f = open("mista_token.txt", "r")
    # token = f.read()
    #client.run('')

    #HEROKU
    client.run(os.environ['TOKEN'])

