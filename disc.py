from __future__ import unicode_literals
import asyncio
import config as cfg
import re
from gmusicapi import Mobileclient
from gmusicapi import Musicmanager
from discord.ext.commands import Bot
import pymysql

mydb = pymysql.connect(
    host="localhost",
    user="root",
    passwd="raspberry",
    database="bangerbot"
)

api = Mobileclient()
api.login(cfg.hunter['username'], cfg.hunter['password'],
          Mobileclient.FROM_MAC_ADDRESS)
mm = Musicmanager()
mm.login()
bot = Bot(command_prefix='!')
MUSICID = '306145575039008768'
BANGERSID = '466453653084176384'
GPMLINK = 'https://play.google.com/music/playlist/AMaBXylMI584mSlTif8d40WcRKSHpna8NHbGStz6WmyOGhiL9FqeSAVycCSqntQCyj21PZjlKt4q2otp_2JDjEKuLyVljZ9UCw%3D%3D'
BANGERSLINK = 'https://play.google.com/music/playlist/AMaBXyn12klQIhyshDRuKbr1LHE61-P7FMr5ucw23ixBIZZ-ocHszlJRgcwZXv8Djcvvz_I6PtHs3e5xm8ZMNHdf00VQQ4wPPA%3D%3D'

songfilename = ''

TOTAL_USERS = 5
PERCENT_NECESSARY = 0.81


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
            link = re.match('http\S+', message.content[29:])
            if not link:
                link = 'ERROR'
            else:
                link = link.group(0)
            song_id = 'ERROR'
            list_id = 'ERROR'
            song_name = 'ERROR'
            nid = link[link.find(
                '/m/') + 3:link.find('?t=')]
            if nid.isalnum() and len(nid) == 27:
                lists = api.get_all_playlists()
                for l in lists:
                    if l['name'] == 'Bangers':
                        list_id = l['id']
                        api.add_store_tracks(nid)
                        library = api.get_all_songs()
                        for song in library:
                            if 'nid' in song:
                                if song['nid'] == nid:
                                    print(song)
                                    song_name = '{0} - {1}'.format(
                                        song['title'], song['artist'])
                                    song_id = song['id']

            if song_name == 'ERROR':
                await remove_msg(1.0, message)
                removed = await bot.send_message(message.channel,
                                                 '{0} was not recognized as a proper link to a song'.format(link))
                await remove_msg(10.0, removed)
                return
            else:
                found = await query_db("SELECT * FROM songs WHERE nid = %s", nid)
                if found > 0:
                    who_rejected = await query_db("SELECT user_id, is_up from song_user WHERE song_id = %s", nid)
                    user_result = ""
                    for result in who_rejected:
                        if (found[0]['status'] == 'rejected' and not result['is_up']) or (
                                found[0]['status'] == 'accepted' and result['is_up']):
                            user_result += '{0} '.format(message.server.get_member(result['user_id']).nick)
                    msg = '{0} has already been put to vote by {1}. It was {2} by {3}'.format(
                        song_name, found[0]['user'], found[0]['status'], user_result)
                    already_added = await bot.send_message(message.channel, msg)
                    await remove_msg(10.0, already_added)
                    await remove_msg(1.0, message)
                    return
            num_users_reacted = 0
            users_reacted = dict()

            voting = await bot.send_message(message.channel,
                                            '[VOTE] {0} has voted to add {1} to the Bangers playlist\n<{2}>'.format(
                                                message.author.nick, song_name, link))
            await query_db("INSERT INTO songs (name, nid, userid, status, up, down, link) values (%s, %s, %s, "
                           "'pending', 1, 0, %s)", (song_name, nid, message.author.id, link))
            await remove_msg(1.0, message)
            await bot.add_reaction(voting, 'upvote:464532537243467786')

            async def check(reaction, user):
                print(user.id)
                print(message.author.id)
                print(message.author.id == user.id)
                if user.id == message.author.id:
                    print("Here")
                    await bot.remove_reaction(message, reaction.emoji, message.author)
                    return False
                e = str(reaction.emoji)
                if user.id not in users_reacted:
                    vote_status = True if e.startswith(
                        '<:upvote:464532537243467786>') else False
                    users_reacted[user.id] = vote_status
                    if vote_status:
                        query_db("UPDATE songs SET up = up + 1 WHERE nid = %s", nid)
                    else:
                        query_db("UPDATE songs SET down = down + 1 WHERE nid = %s", nid)
                    query_db("INSERT INTO song_user (user_id, song_id, is_up) VALUES (%s, %s, %s)",
                             (user.id, nid, vote_status))
                    return e.startswith(('<:upvote:464532537243467786>', '<:downvote:464532598643752970>'))

            while len(users_reacted) < TOTAL_USERS:
                res = await bot.wait_for_reaction(message=voting, check=check)
                num_users_reacted += 1
                if res.user != bot.user:
                    rec_msg = 'agrees <:upvote:464532537243467786>' if (str(
                        res.reaction.emoji) == '<:upvote:464532537243467786>') else 'disagrees {0}'.format(
                        res.reaction.emoji)
                    confirm = await bot.send_message(message.channel,
                                                     '{0.user} {1} for {2}'.format(res, rec_msg, song_name))
                    await remove_msg(10.0, confirm)

            num_agree_votes = 0

            for vote_agree_status in users_reacted:
                if vote_agree_status:
                    num_agree_votes += 1

            if num_agree_votes / TOTAL_USERS > PERCENT_NECESSARY:
                await query_db("UPDATE songs SET status = 'accepted' WHERE nid = %s", nid)
                msg = '{0} has been approved. Adding to bangers {1}'.format(
                    song_name, BANGERSLINK)
                api.add_songs_to_playlist(list_id, song_id)
                approval = await bot.send_message(message.channel, msg)
                await remove_msg(1.0, voting)
                await remove_msg(120.0, approval)
            else:
                approval = await bot.send_message(message.channel,
                                                  'Sorry, {0} did not receive enough upvotes'.format(song_name))
                await query_db("UPDATE songs SET status = 'rejected' WHERE nid = %s", nid)
                await remove_msg(1.0, voting)
                await remove_msg(120.0, approval)
        else:
            await remove_msg(1.0, message)


async def remove_msg(sec, msg_to_remove):
    await asyncio.sleep(sec)
    await bot.delete_message(msg_to_remove)


async def query_db(sql, data):
    cursor = mydb.cursor()
    await cursor.execute(sql, data)
    await mydb.commit()
    return cursor.fetchall()


bot.run(cfg.discord['key'])
