import os
import random
import spotipy

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
PLAYLIST_IDS = os.getenv("PLAYLIST_IDS")

MAX_TRACKS = 100


def getSpotifyLink():
    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
    )

    track_link_list = []
    for playlist_link in PLAYLIST_IDS.split(","):
        tracks_in_playlist = sp.playlist_tracks(playlist_id=playlist_link)

        if tracks_in_playlist is not None:
            track_link_list += [item['track']['external_urls']['spotify']
                                for _, item in enumerate(tracks_in_playlist['items'])]

    # the si parameter is required so the link is opened with the andorid app,
    # but it wont show metadata in webapp, no idea why
    random_link = ""
    random_link = random.choice(track_link_list)  # + "?si=0"

    return random_link


if __name__ == '__main__':
    getSpotifyLink()
