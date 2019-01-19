from __future__ import unicode_literals
import config as cfg
import os
import time
import spotipy
import spotipy.util as util
from gmusicapi.clients import Mobileclient
from json.decoder import JSONDecodeError

spot_cid = '3fe8c6a713a542ed9a5e7f98f7fe72cd'
spot_csec = '2729428a61124b76a005c938ad39a997'
spot_redir = 'https://google.com'

print("Spotify username: ")
sp_un = input()
try:
    os.remove(f".cache-{sp_un}")
except FileNotFoundError:
    pass

scope = 'playlist-modify-private playlist-modify-public user-library-read playlist-read-private user-read-private user-library-modify'
try:
    token = util.prompt_for_user_token(
        sp_un, scope, spot_cid, spot_csec, spot_redir)
except (AttributeError, JSONDecodeError):
    os.remove(f".cache-{sp_un}")
    token = util.prompt_for_user_token(
        sp_un, scope, spot_cid, spot_csec, spot_redir)

sp = spotipy.Spotify(auth=token)

api = Mobileclient()
creds = api.perform_oauth()
# api.oauth_login(Mobileclient.FROM_MAC_ADDRESS)

gpm_playlists = api.get_all_playlists()

print('Here are your GPM playlists:')
for playlist in gpm_playlists:
    if not playlist['deleted']:
        print('\t' + playlist['name'])

print('Which playlist do you want?')
gpm_pl = input()

selected_gpm = next(iter(filter(lambda x: x['name'] == gpm_pl, gpm_playlists)), None)
print('You chose ' + selected_gpm['name'])

gpm_all_songs = api.get_all_songs()
sp_playlists = sp.current_user_playlists()

print('Here are your Spotify playlists:')

for playlist in sp_playlists['items']:
    print('\t' + playlist['name'])

print('Which playlist do you want?')
sp_pl = input()

selected_sp = next(iter(filter(lambda x: x['name'] == sp_pl, sp_playlists['items'])), None)
print('You chose ' + selected_sp['name'])

print(sp.current_user()['id'])
print(selected_sp['id'])

songs_to_transfer = next(iter(filter(lambda x: x['name'] == gpm_pl, api.get_all_user_playlist_contents())), None)
songs_to_add = []
missed_songs = []


def add_song(song):
    real_song = next(iter(filter(lambda x: x['id'] == song['trackId'], gpm_all_songs)), None)
    try:
        song_name = real_song['title']
        song_artist = real_song['artist']
    except TypeError:
        return
    print('Found song ' + song_name + ' by ' + song_artist)
    que = f'{song_name} {song_artist}'
    for c in '().&"':
        que = que.replace(c, "")
    res = sp.search(que, limit=1, type='track')
    try:
        print(
            'Adding equivalent song ' + res['tracks']['items'][0]['name'] + ' by ' +
            res['tracks']['items'][0]['artists'][0][
                'name'] + " to " + selected_sp['name'])
        songs_to_add.append(res['tracks']['items'][0]['uri'])
        if len(songs_to_add) >= 10:
            sp.user_playlist_add_tracks(sp.current_user()['uri'], selected_sp['uri'], songs_to_add)
            songs_to_add.clear()
            print('Adding 10 songs')
    except IndexError:
        print("error")
        print(res)
        missed_songs.append(que)


for songt in songs_to_transfer['tracks']:
    add_song(songt)
    time.sleep(0.5)

sp.user_playlist_add_tracks(sp.current_user()['uri'], selected_sp['uri'], songs_to_add)
print(missed_songs)
