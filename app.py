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


def record_audio(seconds=15, filename='snippet', remove_wav=True):
    """  """
    wav_filename = filename + ".wav"
    mp3_filename = filename + ".mp3"
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 64000
    CHUNK = 1024

    p = pyaudio.PyAudio()
    # print(p.get_default_input_device_info())
    # print(p.get_device_count())

    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=0)

    # records audio
    print("* recording\n")
    ph = " " * 9
    print(ph)

    frames = []
    for i in range(int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK)
        frames.append(data)
        if i % 60 == 0:
            print(f"\r({str(int(i/60))} / {str(seconds)})                ")
    print("* done recording")
    stream.stop_stream()
    stream.close()
    p.terminate()

    # save .wav file
    wf = wave.open(wav_filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    # convert .wav to .mp3
    sound = AudioSegment.from_file(wav_filename)
    sound.export(mp3_filename, format="mp3", bitrate="64k")

    # convert .mp3 to base64 encoded file, for the audd api
    # sound = AudioSegment.from_mp3(mp3_filename)
    # raw_data = sound._data
    # b = base64.b64encode(raw_data)

    # remove wav and mp3 files
    if remove_wav:
        remove(wav_filename)
    return


def audd_api(mp3_filename):
    """  """
    mp3_filename += '.mp3'
    # sending the request
    files = {'file': open(mp3_filename, 'rb')}
    data = {'return': 'timecode,deezer,spotify', 'api_token': '44e5472ccd1035d6bb88608992c2a878'}
    r = requests.post('https://api.audd.io/', data=data, files=files)
    result = r.json()

    # checking result status
    audd_results = None
    if result["status"] == 'error':
        print(f"ERROR {str(result['error']['error_code'])}: {result['error']['error_message']}")
    elif result['status'] == 'success':
        audd_results = result['result']
        # TODO: remove(mp3_filename)

    ''' test! 
    # with open('test.json', 'r') as f:
    #     audd_results = json.load(f)
    '''

    # audd_results is None if audd couldn't find anything
    if audd_results is not None:
        # dict of important info
        user_track = {
            'id': [audd_results['spotify']['id']],
            'title': audd_results['title'],
            'artist': audd_results['artist'],
            'album': audd_results['album']
        }
        print(f"\nSong Detected: {user_track['title']} by {user_track['artist']} album: {user_track['album']}\n")
    else:
        user_track = None
        print(f"No song recognized.")
    return user_track


def spotipy_api(user_track):
    """  """
    client_credentials_manager = SpotifyClientCredentials(client_id='c7db96da8a3c4b47846afacf7f838740',
                                                          client_secret='1cdc68e99a464a6cb671ac9d9dbbd332')
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    results = spotify.recommendations(seed_tracks=user_track['id'], country='US', limit=5)
    return results


def process_spotify(results):
    """ spotipy results to array of track dictionaries """
    tracks = []
    for track in results['tracks']:
        tracks.append({
            'id': track['id'],
            'url': track['external_urls']['spotify'],
            'title': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name']
        })
    return tracks


def print_tracks(tracks):
    """  """
    print(f"~~~~~~~~~~~~~~~ Suggested Tracks ~~~~~~~~~~~~~~~")
    print(f"~~~~~~~~~~~~~~~ Title, by Artist ~~~~~~~~~~~~~~~")

    for i in range(len(tracks)):
        print(f"[{str(i)}] | {tracks[i]['title']}, by {tracks[i]['artist']}")


def int_input(prompt, limit):
    ''' helper functions '''
    user_int = input(f"{prompt}: ")
    while int(user_int) >= limit and not int(user_int) == 0:
        user_int = input(f"{prompt}: ")
    return int(user_int)


def str_input(prompt):
    ''' helper functions '''
    user_str = input(f"{prompt}: ")
    while not type(user_str) == str:
        user_str = input(f"{prompt}: ")
    return user_str


def select_option(prompt, commands):
    while True:
        option = str_input(f"{prompt}: ").lower()
        if option in commands:
            return option
        else:
            print(f'Choose one of the following: {", ".join(commands).upper()}')


def open_url(track):
    print(f"Opening '{track['title']}' by {track['artist']}... ")
    webbrowser.open_new_tab(track['url'])


def begining_prints():
    print("--> R to begin")
    print("--> T to begin with test.mp3")
    print("--> C to select .mp3 filename to pull from")


commands = ['r', 't', 'c']
ask_again = True

while ask_again:
    begining_prints()
    sel = select_option('Select a letter', commands)

    if sel == 'r':
        filename = "snippet"
        record_audio(15, filename)
        ask_again = False
    elif sel == 't':
        filename = "test"
        ask_again = False
    elif sel == 'c':
        filename = str_input("Enter mp3 filename. {filename}.mp3")

user_track = audd_api(filename)
if user_track is not None:
    results = spotipy_api(user_track)
    tracks = process_spotify(results)
    print_tracks(tracks)
    track_index = int_input(f"Select a song to play by choosing 0 - {str(len(tracks)-1)}", len(tracks))
    open_url(tracks[track_index])
