from __future__ import unicode_literals
import discord
import asyncio
import config as cfg
import youtube_dl as ytdl
from twitch import TwitchClient
from gmusicapi import Mobileclient
from gmusicapi import Musicmanager
from discord.ext.commands import Bot

api = Mobileclient()
api.login(cfg.hunter['username'], cfg.hunter['password'],
          Mobileclient.FROM_MAC_ADDRESS)

mm = Musicmanager()
mm.login()
bot = Bot(command_prefix="!")
tw_client = TwitchClient(client_id='yrtnfgu5t6f1wxdrzszwh1h0awn9iy')
MUSICID = '306145575039008768'
DEVID = '319938734135050240'
STREAMSID = '337819803500806146'
CHANNEL = ''
GPMLINK = 'https://play.google.com/music/playlist/AMaBXylMI584mSlTif8d40WcRKSHpna8NHbGStz6WmyOGhiL9FqeSAVycCSqntQCyj21PZjlKt4q2otp_2JDjEKuLyVljZ9UCw%3D%3D'

streamNums = {58460483: None, 23218163: None, 26832142: None,
              26832258: None, 114241476: None, 125129097: None}
# splatterdodge: 58460483
# thederko: 23218163
# huntinator7: 26832142
# nicktend0: 26832258
# ztagger1911: 114241476
# mighty_moosen: 125129097


# async def my_background_task():
#    await bot.wait_until_ready()
#    counter = 0
#    while not bot.is_closed:
#        counter += 1
#        await check_start()
#        await asyncio.sleep(600)  # task runs every 60 seconds

# bot.loop.create_task(my_background_task())


# async def check_start():
#    for num in streamNums.keys():
#        tf = tw_client.streams.get_stream_by_user(num)
#        if streamNums[num] is None:
#            if tf is not None:
#                streamNums[num] = tf
#                await stream_alert(tf)
#        else:
#            if tf is None:
#                streamNums[num] = tf


# async def stream_alert(stream):
#    msg = '@here Come watch ' + stream.channel.name + \
#          ' stream ' + stream.channel.game + \
#          ' over at ' + stream.channel.url
#    channels = bot.get_all_channels()
#    for channel in channels:
#        if channel.name == 'streams':
#            await bot.send_message(channel, msg)


@bot.event
async def on_read():
    print('Client logged in')


@bot.event
async def on_message(message):
    # we do not want the bot to reply to itself
    # if message.channel.id == MUSICID
    if message.author == bot.user:
        return

    if message.content.startswith('!hello'):
        msg = 'Hello ' + message.server.id
        for channel in message.server.channels:
            if channel.name == 'dev-test':
                await bot.send_message(channel, msg)
    elif message.content.startswith('!link'):
        msg = "Here's the link to the playlist for listening " + GPMLINK
        await bot.send_message(message.channel, msg)
    elif message.content.startswith('!add'):
        nid = message.content[message.content.find(
            '/m/') + 3:message.content.find('?t=')]
        msg = 'Could not add song'
        lists = api.get_all_playlists()
        for l in lists:
            if l['name'] == 'Moosen Mix':
                api.add_store_tracks(nid)
                library = api.get_all_songs()
                for song in library:
                    if 'nid' in song:
                        if song['nid'] == nid:
                            api.add_songs_to_playlist(l['id'], song['id'])
                            msg = 'Successfully added song!'
        await bot.send_message(message.channel, msg)
    elif message.content.startswith('!ad'):
        nid = message.content[message.content.find(
            '/m/') + 3:message.content.find('?t=')]
        msg = 'Could not add song'
        lists = api.get_all_playlists()
        for l in lists:
            if l['name'] == 'Moosen Mix':
                api.add_store_tracks(nid)
                library = api.get_all_songs()
                for song in library:
                    if 'nid' in song:
                        if song['nid'] == nid:
                            api.add_songs_to_playlist(l['id'], song['id'])
                            msg = 'Nick you suck at typing. I shouldn\'t have, but I added the song anyways.'
        await bot.send_message(message.channel, msg)
    elif message.content.startswith('!com'):
        msg = '!link to get link to the playlist\n!add to add a song'
        await bot.send_message(message.channel, msg)
    elif message.content.startswith('!upload'):
        url = message.content[8:]
        ydl_opts = {
            'forcejson': 'true',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [my_hook]
        }
        with ytdl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        await bot.send_message(message.channel, "Downloaded to server")
        # mm.upload('test.mp3')
        # mm.upload('test2.mp3')
        # await bot.send_message(message.channel, "Uploaded to GPM")
    elif message.content.startswith('!test'):
        nid = message.content[message.content.find(
            '/m/') + 3:message.content.find('?t=')]
        msg = 'Song is not in playlist'
        lists = api.get_all_playlists()
        for l in lists:
            if l['name'] == 'Moosen Mix':
                api.add_store_tracks(nid)
                library = api.get_all_songs()
                for song in library:
                    if song['nid'] == nid:
                        api.add_songs_to_playlist(l['id'], song['id'])
                        msg = 'Successfully added song!'
        await bot.send_message(message.channel, msg)

def my_hook(d):
    if d['status'] == 'finished':
        print(d)
        # await bot.send_message(message.channel, "Uploaded to GPM")

bot.run(cfg.discord['key'])
