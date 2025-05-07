from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, USLT, APIC
song_name = 'Tujhe Dekha To Ye Jana Sanam - Lyrical ｜ Shah Rukh Khan ｜ Kajol ｜ DDLJ ｜ Lata Mangeshkar, Kumar Sanu [7JnKVPtRqVE].mp3'
audio = EasyID3(song_name)
audio['artist'] = 'Pink Floyd'
audio['album'] = 'The Wall'
audio['title'] = 'Another Brick in the Wall'
audio.save()

# Add Lyrics
tags = ID3(song_name)
tags.add(
    USLT(encoding=3, lang=u'eng', desc=u'desc', text=u'All in all you’re just another brick in the wall...')
)
tags.save()

# # Add Album Art
# with open("cover.jpg", 'rb') as albumart:
#     tags.add(
#         APIC(
#             encoding=3,
#             mime='image/jpeg',
#             type=3, desc=u'Cover',
#             data=albumart.read()
#         )
#     )
tags.save()
