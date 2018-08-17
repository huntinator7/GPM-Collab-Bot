from __future__ import unicode_literals
import asyncio
import config as cfg
import re
from gmusicapi import Mobileclient
from gmusicapi import Musicmanager
from discord.ext.commands import Bot
import pymysql

if hasattr(cfg, 'db'):
    print("HAS PASSWORD")
    mydb = pymysql.connect(
        host="localhost",
        user="root",
        passwd=cfg.db['pass'],
        database="bangerbot"
    )
else:
    print("DOES NOT HAVE PASSWD")
    mydb = pymysql.connect(
        host="localhost",
        user="root",
        database="bangerbot"
    )

api = Mobileclient()
api.login(cfg.hunter['username'], cfg.hunter['password'],
          Mobileclient.FROM_MAC_ADDRESS)
mm = Musicmanager()
mm.login()
bot = Bot(command_prefix='!')
MUSICID = 306145575039008768
BANGERSID = 466453653084176384
GPMLINK = 'https://play.google.com/music/playlist/AMaBXylMI584mSlTif8d40WcRKSHpna8NHbGStz6WmyOGhiL9FqeSAVycCSqntQCyj21PZjlKt4q2otp_2JDjEKuLyVljZ9UCw%3D%3D'
BANGERSLINK = 'https://play.google.com/music/playlist/AMaBXyn12klQIhyshDRuKbr1LHE61-P7FMr5ucw23ixBIZZ-ocHszlJRgcwZXv8Djcvvz_I6PtHs3e5xm8ZMNHdf00VQQ4wPPA%3D%3D'
UPVOTE = None
DOWNVOTE = None

TOTAL_USERS = 5
UPVOTES_NEEDED = 5


# splatterdodge: 58460483
# thederko: 23218163
# huntinator7: 26832142
# nicktend0: 26832258
# ztagger1911: 114241476
# mighty_moosen: 125129097


@bot.event
async def on_ready():
    print('bot logged in')
    global UPVOTE
    global DOWNVOTE
    UPVOTE = bot.get_emoji(464532537243467786)
    DOWNVOTE = bot.get_emoji(464532598643752970)


@bot.event
async def on_message(message):
    global UPVOTE
    global DOWNVOTE
    author = message.author
    guild = message.guild
    channel = message.channel
    content = message.content
    if author == bot.user:
        return
    if channel.id == MUSICID:
        msg_arr = content.split()
        if not (msg_arr[0] == '!add' or msg_arr[0] == '!ad'):
            return
        try:
            nid = msg_arr[1][msg_arr[1].find(
                '/m/') + 3:msg_arr[1].find('?t=')]
            list_id, song_id, song_name = do_gpm(nid, "Moosen_Mix", True)
            print(list_id + song_id + song_name)
            msg = 'Successfully added song to {0}! {1}'.format("Moosen_Mix", GPMLINK)
        except TypeError:
            print("Error with song")
            msg = 'Could not add song'
        await channel.send(msg)
    elif channel.id == BANGERSID:
        if not content.startswith('<:banger:462298646117875734>'):
            await message.delete()
            return
        try:
            link = re.search('http\S+', content[29:])[0]
        except TypeError:
            print("Song is not valid")
            await message.delete()
            removed = await channel.send('{0} was not recognized as a proper link to a song'.format(content[29:]))
            asyncio.ensure_future(remove_msg(10.0, removed))
            return
        nid = link[link.find(
            '/m/') + 3:link.find('?t=')]
        api.add_store_tracks(nid)
        try:
            list_id, song_id, song_name = do_gpm(nid, "Bangers", False)
        except TypeError:
            print("Error with song")
            await message.delete()
            return
        found = await query_db("SELECT status, userid FROM songs WHERE nid = %s", str(nid))
        if len(found) > 0:
            who_rejected = await query_db("SELECT user_id, is_up from song_user WHERE song_id = %s", str(nid))
            user_result = ""
            for result in who_rejected:
                if (found[0][0] == 'rejected' and not result[1]) or (
                        found[0][0] == 'accepted' and result[1]):
                    user_result += '{0} '.format(guild.get_member(int(result[0])).nick)
            msg = '{0} has already been put to vote by {1}. It was {2} by {3}'.format(
                song_name, guild.get_member(int(found[0][1])).nick, found[0][0], user_result)
            already_added = await channel.send(msg)
            asyncio.ensure_future(remove_msg(30.0, already_added))
            await message.delete()
            return
        voting = await channel.send('[VOTE] {0} has voted to add {1} to the Bangers playlist\n<{2}>'.format(
            author.mention, song_name, link))
        asyncio.ensure_future(query_db("INSERT INTO songs (name, nid, userid, status, up, down, link) values (%s, %s, "
                                       "%s, 'pending', 1, 0, %s)", (song_name, str(nid), author.id, link)))
        await message.delete()
        await asyncio.sleep(1)
        await voting.add_reaction(UPVOTE)


@bot.event
async def on_raw_reaction_remove(obj):
    emoji = obj.emoji
    channel = bot.get_channel(obj.channel_id)
    message = await channel.get_message(obj.message_id)
    author = message.author
    guild = bot.get_guild(obj.guild_id)
    reactor = bot.get_user(obj.user_id)
    # Exit if not in bangers or it was the bot's reaction
    if channel.id != BANGERSID:
        return
    if not reactor.bot:
        print("orrr action")
        # loc = message.content.find(str(reactor.id))
        # print(message.content[:loc - 50])
        # print(re.sub(r'<.+>', '', message.content[loc - 50:loc + 30]))
        # print(message.content[loc + 30:])
        # await message.edit(content='{0}{1}{2}'.format(message.content[:loc - 50],
        #                                               re.sub(r'<.+>', '', message.content[loc - 50:loc + 30]),
        #                                               message.content[loc + 30:]))


@bot.event
async def on_raw_reaction_add(obj):
    global UPVOTE
    global DOWNVOTE
    # Define variables based on obj props
    emoji = obj.emoji
    channel = bot.get_channel(obj.channel_id)
    message = await channel.get_message(obj.message_id)
    author = message.author
    guild = bot.get_guild(obj.guild_id)
    reactor = bot.get_user(obj.user_id)

    # Exit if not in bangers or it was the bot's reaction
    if channel.id != BANGERSID or len(message.raw_mentions) < 1:
        print("wrong channel")
        return
    # Define vote proposer
    try:
        proposer = bot.get_user(message.raw_mentions[0])
    except IndexError:
        print("no proposer")
        proposer = author
    # Remove emoji if it isn't a vote
    if not (emoji.id == UPVOTE.id or emoji.id == DOWNVOTE.id):
        print("wrong emoji")
        await message.remove_reaction(emoji, reactor)
        return
    # If reactor is the one who proposed the song, remove their reaction.
    if reactor.id == proposer.id:
        print("proposer is reactor")
        await message.remove_reaction(emoji, reactor)
        return
    # If reactor has already reacted to a message
    if reactor.id in message.raw_mentions:
        # Remove the voter's other vote
        # and update the message to reflect the change
        print("reactor has reacted")
        opp_emoji = UPVOTE if emoji.id == DOWNVOTE.id else DOWNVOTE
        await message.remove_reaction(opp_emoji, reactor)
        loc = message.content.find(str(reactor.id))
        await message.edit(content='{0}{1}{2}'.format(message.content[:loc - 50],
                                                      re.sub(r'<.+>', str(emoji), message.content[loc - 50:loc]),
                                                      message.content[loc:]))
        message = await channel.get_message(obj.message_id)
    elif reactor.id == bot.user.id:
        await message.edit(content='{0}\n{1} {2}'.format(message.content, emoji, proposer.mention))
    elif author.id == bot.user.id:
        await message.edit(content='{0}\n{1} {2}'.format(message.content, emoji, reactor.mention))
    # Action to take if there are enough votes on a message
    tot_upvotes = sum(x.count for x in message.reactions if x.emoji.id == UPVOTE.id)
    tot_downvotes = sum(x.count for x in message.reactions if x.emoji.id == DOWNVOTE.id)
    print("up: " + str(tot_upvotes))
    print("down: " + str(tot_downvotes))

    if tot_upvotes >= 4 or tot_downvotes >= 2:
        nid = message.content[message.content.find('/m/') + 3:message.content.find('?t=')]
        await add_song_users_to_db(message, nid, True if tot_upvotes >= 4 else False, tot_upvotes, tot_downvotes)
        list_id, song_id, song_name = do_gpm(nid, "Bangers", False)
        if tot_upvotes >= 4:
            api.add_songs_to_playlist(list_id, song_id)
            approval = await channel.send('{0} has been approved. Adding to bangers {1}'.format(
                song_name, BANGERSLINK))
            status = "accepted"
        else:
            approval = await channel.send('Sorry, {0} did not receive enough upvotes'.format(song_name))
            status = "rejected"
        asyncio.ensure_future(add_song_users_to_db(message, nid, status, tot_upvotes, tot_downvotes))
        await message.delete()
        asyncio.ensure_future(remove_msg(3600.0, approval))


def do_gpm(nid, name, add):
    print(nid)
    print(name)
    api.add_store_tracks(nid)
    lists = api.get_all_playlists()
    for l in lists:
        print(l['name'])
        if l['name'] == name:
            library = api.get_all_songs()
            for song in library:
                if 'nid' in song:
                    if song['nid'] == nid:
                        print(l['id'] + '\n' + song['id'] + '\n' + '{0} - {1}'.format(song['title'], song['artist']))
                        if add:
                            api.add_songs_to_playlist(l['id'], song['id'])
                        return l['id'], song['id'], '{0} - {1}'.format(song['title'], song['artist'])
    print("did not find song")
    return


async def add_song_users_to_db(message, nid, status, up, down):
    for r in message.reactions:
        vote_status = True if r.emoji.id == UPVOTE.id else False
        print(vote_status)
        async for u in r.users():
            print(u, r.emoji.name)
            if not u.bot:
                print("INSERT INTO song_user ({0}, {1}, {2})".format(u.id, str(nid), vote_status))
                asyncio.ensure_future(query_db("INSERT INTO song_user (user_id, song_id, is_up) VALUES (%s, %s, %s)",
                                               (u.id, str(nid), vote_status)))
    asyncio.ensure_future(
        query_db("UPDATE songs SET status = %s, up = %s, down = %s WHERE nid = %s",
                 (status, up, down, str(nid))))


async def remove_msg(sec, msg_to_remove):
    await asyncio.sleep(sec)
    await msg_to_remove.delete()


async def send_and_remove(msg, channel, sec):
    message = await channel.send(msg)
    await asyncio.sleep(sec)
    await message.delete()


async def query_db(sql, data):
    try:
        with mydb.cursor() as cursor:
            # Create a new record
            cursor.execute(sql, data)
            # connection is not autocommit by default. So you must commit to save
            # your changes.
            mydb.commit()
            await asyncio.sleep(1)
            return cursor.fetchall()
    finally:
        mydb.close()


bot.run(cfg.discord['key'])
