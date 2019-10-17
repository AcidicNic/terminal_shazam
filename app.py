''' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    brew install ffmpeg for this to work!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! '''

# record audio (.wav)
import pyaudio
import wave
# converts the .wav to .mp3
from pydub import AudioSegment
# remove audio files after processing.
from os import remove
# sends requests to audd api
import requests
# spotify api
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
# open spotify webplayer
import webbrowser
# json for api
import json
# import base64 # converts .mp3 to base64 encoded file
'''
WAVE_OUTPUT_FILENAME = "temp_snippet.wav"
MP3_OUTPUT_FILENAME = "snippet.mp3"
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 64000
CHUNK = 1024
RECORD_SECONDS = 3

p = pyaudio.PyAudio()

# print(p.get_default_input_device_info())
# print(p.get_device_count())

stream = p.open(format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            input_device_index=0)

# records audio for
print("* recording")
frames = []
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

# stops recording
print("* done recording")
stream.stop_stream()
stream.close()
p.terminate()

# save .wav file
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

# convert .wav to .mp3
sound = AudioSegment.from_file(WAVE_OUTPUT_FILENAME)
sound.export(MP3_OUTPUT_FILENAME, format="mp3", bitrate="64k")
'''

# convert .mp3 to base64 encoded file, for the audd api
# sound = AudioSegment.from_mp3(MP3_OUTPUT_FILENAME)
# raw_data = sound._data
# b = base64.b64encode(raw_data)

# remove wav and mp3 files
# remove(WAVE_OUTPUT_FILENAME)
# remove(MP3_OUTPUT_FILENAME)

'''
# audd api
files = {'file': open(MP3_OUTPUT_FILENAME, 'rb')}
data = {
'return': 'timecode,apple_music,deezer,spotify',
'api_token': '44e5472ccd1035d6bb88608992c2a878'
}
r = requests.post('https://api.audd.io/', data=data, files=files)
result = r.json()

if result["status"] == 'error':
    print(f"ERROR {str(result['error']['error_code'])}: {result['error']['error_message']}")
if result['status'] == 'success':
    print(result)
    result = result['result']
'''
# converting audd api results to json object
with open('test.json', 'r') as f:
    audd_results = json.load(f)

# dict of important info
user_track = {
    'id': [audd_results['result']['spotify']['id']],
    'title': audd_results['result']['title'],
    'artist': audd_results['result']['artist'],
    'album': audd_results['result']['album']
}

print(f"\nSong Detected: {user_track['title']} by {user_track['artist']} album: {user_track['album']}\n")

# spotipy api
client_credentials_manager = SpotifyClientCredentials(client_id='c7db96da8a3c4b47846afacf7f838740', client_secret='1cdc68e99a464a6cb671ac9d9dbbd332')
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
results = spotify.recommendations(seed_tracks=user_track['id'], country='US', limit=5)

# spotipy results to array of track dictionaries
tracks = []
for track in results['tracks']:
    tracks.append({
        'id': track['id'],
        'url': track['external_urls']['spotify'],
        'title': track['name'],
        'artist': track['artists'][0]['name'],
        'album': track['album']['name']
    })

print(f"~~~~~~~~~~~~~~~ Suggested Tracks ~~~~~~~~~~~~~~~")
print(f"~~~~~~~~~~~~~~~ Title, by Artist ~~~~~~~~~~~~~~~")

for i in range(len(tracks)):
    print(f"[{str(i)}] | {tracks[i]['title']}, by {tracks[i]['artist']}")

def select_char():
    input("choose a song to play: ")

# print(url)
# webbrowser.open_new_tab(url)
# result = results.json()
