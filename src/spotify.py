import os
import pysondb
import random
import spotipy

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
PLAYLIST_IDS = os.getenv("PLAYLIST_IDS")
SONG_DATABASE = os.getenv("SONG_DATABASE")

MAX_TRACKS = 100


songdb = pysondb.getDb(SONG_DATABASE)

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    ),
    retries=3
)


def get_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks


def getSpotifyLinkList():

    track_link_list = []
    for playlist_link in PLAYLIST_IDS.split(","):
        try:
            tracks_in_playlist = get_playlist_tracks(playlist_link)
        except spotipy.SpotifyException as e:
            if e.http_status == 429:
                return []
            print(playlist_link + " playlist_not valid")
            continue

        if tracks_in_playlist is not None:
            for _, item in enumerate(tracks_in_playlist):
                try:
                    track_link_list.append(
                        item['track']['external_urls']['spotify'])
                except KeyError:
                    pass

    return list(set(track_link_list))


def saveSongs():
    song_link_list = getSpotifyLinkList()
    if song_link_list != []:
        for song_link in song_link_list:
            songdb.add({"spotify_link": song_link})


def getRandomSong():
    songs = songdb.getAll()
    if songs != []:
        return random.choice([song["spotify_link"] for song in songs])
    else:
        return None


if __name__ == '__main__':
    random.choice(getSpotifyLinkList())
