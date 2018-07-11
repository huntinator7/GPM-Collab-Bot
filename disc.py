from __future__ import unicode_literals
import discord
import asyncio
import config as cfg
import json
from gmusicapi import Mobileclient
from gmusicapi import Musicmanager
from discord.ext.commands import Bot

api = Mobileclient()
# api.login(cfg.hunter['username'], cfg.hunter['password'],
#           Mobileclient.FROM_MAC_ADDRESS)
mm = Musicmanager()
# mm.login()
bot = Bot(command_prefix="!")
MUSICID = '306145575039008768'
BANGERSID = '464450150027493377'
GPMLINK = 'https://play.google.com/music/playlist/AMaBXylMI584mSlTif8d40WcRKSHpna8NHbGStz6WmyOGhiL9FqeSAVycCSqntQCyj21PZjlKt4q2otp_2JDjEKuLyVljZ9UCw%3D%3D'
BANGERSLINK = 'https://play.google.com/music/playlist/AMaBXyn12klQIhyshDRuKbr1LHE61-P7FMr5ucw23ixBIZZ-ocHszlJRgcwZXv8Djcvvz_I6PtHs3e5xm8ZMNHdf00VQQ4wPPA%3D%3D'

songFilename = ''

TOTAL_USERS = 4
PERCENT_NECESSARY = 0.74

# splatterdodge: 58460483
# thederko: 23218163
# huntinator7: 26832142
# nicktend0: 26832258
# ztagger1911: 114241476
# mighty_moosen: 125129097


@bot.event
async def on_ready():
    print('bot logged in')


@bot.event
async def on_message(message):

    if message.author == bot.user:
            return
    if message.channel.id != BANGERSID and message.content.startswith('!add') or message.content.startswith('!ad'):    
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
                            print(song)
                            api.add_songs_to_playlist(l['id'], song['id'])
                            msg = 'Successfully added song to Moosen Mix! ' + GPMLINK
        await bot.send_message(message.channel, msg)
    elif message.channel.id == BANGERSID:
        if message.content.startswith('<:banger:462298646117875734>'):
            link = message.content[29:]

            songID = 'ERROR'
            listID = 'ERROR'
            songName = 'ERROR'
            nid = link[link.find(
                '/m/') + 3:link.find('?t=')]
            if nid.isalnum() and len(nid) == 27:
                lists = api.get_all_playlists()
                for l in lists:
                    if l['name'] == 'Bangers':
                        listID = l['id']
                        api.add_store_tracks(nid)
                        library = api.get_all_songs()
                        for song in library:
                            if 'nid' in song:
                                if song['nid'] == nid:
                                    print(song)
                                    songName = '{0} - {1}'.format(
                                        song['title'], song['artist'])
                                    songID = song['id']

            if songName == 'ERROR':
                await removeMsg(1.0, message)
                removed = await bot.send_message(message.channel, '{0} was not recognized as a proper link to a song'.format(link))
                await removeMsg(10.0, removed)
                return
            else:
                with open('bangers.json', 'r') as f:
                    data = json.load(f)
                found = list(filter(lambda x: x['nid'] == nid, data['songs']))
                if len(found) > 0:
                    msg = '{0} has already been added by {1}'.format(
                        songName, found[0]['user'])
                    await bot.send_message(message.channel, msg)
                    return
            numUsersReacted = 0
            usersReacted = dict()

            voting = await bot.send_message(message.channel, '[VOTE] {0} has voted to add {1} to the Bangers playlist'.format(message.author.nick, songName))
            await bot.add_reaction(voting, '<:upvote:464532537243467786>')
            usersReacted[message.author.id] = True

            def check(reaction, user):
                e = str(reaction.emoji)
                if not user.id in usersReacted:
                    voteStatus = True if e.startswith(
                        '<:upvote:464532537243467786>') else False
                    usersReacted[user.id] = voteStatus
                    return e.startswith(('<:upvote:464532537243467786>', '<:downvote:464532598643752970>'))

            while len(usersReacted) < TOTAL_USERS:
                res = await bot.wait_for_reaction(message=voting, check=check)
                numUsersReacted += 1
                recMsg = 'agrees <:upvote:464532537243467786>' if (str(
                    res.reaction.emoji) == '<:upvote:464532537243467786>') else 'disagrees {0}'.format(res.reaction.emoji)
                confirm = await bot.send_message(message.channel, '{0.user} {1} for {2}'.format(res, recMsg, songName))
                await removeMsg(10.0, confirm)


            agreeVotesCounter = 0

            for voteStatus in usersReacted:
                if voteStatus:
                    agreeVotesCounter += 1

            if agreeVotesCounter / TOTAL_USERS > PERCENT_NECESSARY:
                with open('bangers.json') as f:
                    data = json.load(f)
                with open('bangers.json.backup', 'a') as f:
                    f.write(json.dumps(data))
                found = list(filter(lambda x: x['nid'] == nid, data['songs']))
                data['songs'].append({'nid': nid, 'user': message.author.name})
                with open('bangers.json', 'w') as f:
                    f.write(json.dumps(data))
                msg = '{0} has been approved. Adding to bangers {1}'.format(
                    songName, BANGERSLINK)
                api.add_songs_to_playlist(listID, songID)
                approval = await bot.send_message(message.channel, msg)
                await removeMsg(1.0, voting)
                await removeMsg(600.0, approval)
        else:
            await removeMsg(1.0, message)

async def removeMsg(sec, msg):
    await asyncio.sleep(sec)
    bot.delete_message(msg)

bot.run(cfg.discord['key'])
