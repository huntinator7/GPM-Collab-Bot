from gmusicapi import Mobileclient
import config as cfg

api = Mobileclient()
api.login(cfg.hunter['username'], cfg.hunter['password'],
          Mobileclient.FROM_MAC_ADDRESS)

library = api.get_all_songs()
for song in library:
    if song['title'] == 'hold_on':
        print(song)
    # print(song['title'] + ' - ' + song['artist'])