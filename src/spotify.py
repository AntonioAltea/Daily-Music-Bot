import os
import random
from unittest import result
import spotipy

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
PLAYLIST_IDS = os.getenv("PLAYLIST_IDS")

MAX_TRACKS = 100

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
)


def get_playlist_tracks(playlist_id):

    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks


def getSpotifyLink():

    track_link_list = []
    for playlist_link in PLAYLIST_IDS.split(","):
        tracks_in_playlist = get_playlist_tracks(playlist_link)

        if tracks_in_playlist is not None:
            for _, item in enumerate(tracks_in_playlist):
                try:
                    track_link_list.append(item['track']['external_urls']['spotify'])
                except KeyError:
                    pass

    # the si parameter is required so the link is opened with the andorid app,
    # but it wont show metadata in webapp, no idea why
    random_link = ""
    random_link = random.choice(track_link_list)  # + "?si=0"

    return random_link


if __name__ == '__main__':
    getSpotifyLink()
