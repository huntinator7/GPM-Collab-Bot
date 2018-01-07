from __future__ import unicode_literals
import discord
import asyncio
import config as cfg
import youtube_dl as ytdl
from eyed3 import id3
from gmusicapi import Mobileclient
from gmusicapi import Musicmanager
from discord.ext.commands import Bot

api = Mobileclient()
api.login(cfg.hunter['username'], cfg.hunter['password'],
          Mobileclient.FROM_MAC_ADDRESS)

mm = Musicmanager()
mm.login()
bot = Bot(command_prefix="!")
tag = id3.Tag()
MUSICID = '306145575039008768'
DEVID = '319938734135050240'
STREAMSID = '337819803500806146'
CHANNEL = ''
GPMLINK = 'https://play.google.com/music/playlist/AMaBXylMI584mSlTif8d40WcRKSHpna8NHbGStz6WmyOGhiL9FqeSAVycCSqntQCyj21PZjlKt4q2otp_2JDjEKuLyVljZ9UCw%3D%3D'
XMASLINK = 'https://play.google.com/music/playlist/AMaBXymsmPFEwZCU-jkFiTXHw5jnIyL1M4DcaQ-rmmEnZg_DsmjtivO_WcP4xJk5-9OiekNY8nQjYNNqm8Lc4H5rPXJVQbWW-g%3D%3D'

songFilename = ''

# streamNums = {58460483: None, 23218163: None, 26832142: None,
#               26832258: None, 114241476: None, 125129097: None}
# splatterdodge: 58460483
# thederko: 23218163
# huntinator7: 26832142
# nicktend0: 26832258
# ztagger1911: 114241476
# mighty_moosen: 125129097

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
        msg = 'Moosen Mix: ' + GPMLINK + '\nChristmix: ' + XMASLINK
        await bot.send_message(message.channel, msg)
    elif message.content.startswith('!add') or message.content.startswith('!ad'):
        nid = message.content[message.content.find(
            '/m/') + 3:message.content.find('?t=')]
        msg = 'Could not add song'
        lists = api.get_all_playlists()
        for l in lists:
            print(l)
            if l['name'] == 'Moosen Mix':
                print(l)
                api.add_store_tracks(nid)
                allsongs = api.get_all_user_playlist_contents()
                alltracks = allsongs['tracks']
                for song in alltracks:
                    if song['track']['nid'] == nid and song['playlistId'] == "08d08171-1818-48a4-b587-d324090922e8":
                        msg = "That song is already on the playlist"
                        await bot.send_message(message.channel, msg)
                library = api.get_all_songs()
                for song in library:
                    if 'nid' in song:
                        if song['nid'] == nid:
                            print(song)
                            api.add_songs_to_playlist(l['id'], song['id'])
                            msg = 'Successfully added song to Moosen Mix! ' + GPMLINK    
        await bot.send_message(message.channel, msg)
    elif message.content.startswith('!xmas'):
        nid = message.content[message.content.find(
            '/m/') + 3:message.content.find('?t=')]
        msg = 'Could not add song'
        lists = api.get_all_playlists()
        for l in lists:
            if l['name'] == 'Christmix':
                api.add_store_tracks(nid)
                library = api.get_all_songs()
                for song in library:
                    if 'nid' in song:
                        if song['nid'] == nid:
                            api.add_songs_to_playlist(l['id'], song['id'])
                            msg = 'Successfully added song to Christmix! ' + XMASLINK
        await bot.send_message(message.channel, msg)
    elif message.content.startswith('!com'):
        msg = '!link to get link to the playlist\n!add to add a song'
        await bot.send_message(message.channel, msg)
    elif message.content.startswith('!upload'):
        msg = message.content[8:]
        info = msg.split(",")
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
            ydl.download([info[0].strip()])
        await bot.send_message(message.channel, "Downloaded to server")
        tag.parse(songFilename)
        tag.artist = info[1].strip()
        tag.title = info[2].strip()
        tag.album = "Moosen Media"
        tag.save()
        mm.upload(songFilename)
        await bot.send_message(message.channel, "Uploaded to GPM")
        lists = api.get_all_playlists()
        for l in lists:
            if l['name'] == 'Moosen Mix':
                library = api.get_all_songs()
                for song in library:
                    if song['title'] == info[2].strip() and song['artist'] == info[1].strip():
                            api.add_songs_to_playlist(l['id'], song['id'])
                            await bot.send_message(message.channel, "Added song to Moosen Mix")
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
        global songFilename
        songFilename = d['filename'][:-4]
        songFilename += "mp3"
        print(songFilename)
        # await bot.send_message(message.channel, "Uploaded to GPM")

bot.run(cfg.discord['key'])
