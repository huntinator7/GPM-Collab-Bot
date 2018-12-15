from __future__ import unicode_literals
import asyncio
import config as cfg
import re
import json
import spotipy
import spotipy.util as util
from gmusicapi import Mobileclient
from gmusicapi import Musicmanager

# export SPOTIPY_CLIENT_ID = '3fe8c6a713a542ed9a5e7f98f7fe72cd'
# export SPOTIPY_CLIENT_SECRET='2729428a61124b76a005c938ad39a997'
# export SPOTIPY_REDIRECT_URI='https://google.com'

# print("GPM UN: ")
# un = input()
# print("GPM Pass: ")
# passwd = input()
# print("Spotify username: ")
# sp_un = input()

token = util.prompt_for_user_token(
    username=cfg.hunter['spotify'], scope=None)

sp = spotipy.Spotify(auth=token)

api = Mobileclient()
api.login(cfg.hunter['username'], cfg.hunter['password'],
          Mobileclient.FROM_MAC_ADDRESS)
mm = Musicmanager()
mm.login()

library = api.get_all_songs()
for song in library:
    req = song['title'] + " " + song['artist']
    print(req)
    res = sp.search(req, limit=1, type='track')
    print(res)
