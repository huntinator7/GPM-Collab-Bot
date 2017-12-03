from eyed3 import id3
tag = id3.Tag()

tag.parse('test.mp3')
print(tag.artist)