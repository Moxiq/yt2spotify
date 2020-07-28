import requests
import json

from spotify_client import SpotifyClient
from youtube_client import YoutubeClient


class YoutubeToSpotify:

    @staticmethod
    def get_secrets() :
        with open("secrets.json") as f:
            return json.load(f)




if __name__ == "__main__":
    secrets = YoutubeToSpotify.get_secrets()
    yt_client = YoutubeClient()
    spot_client = SpotifyClient()

    spot_client.authenticate_all()
    yt_playlist_id = input("Enter youtube playlist id:")

    song_arr = yt_client.playlist_items(yt_playlist_id)

    spot_playlist_id = spot_client.add_playlist()

    for i in range(len(song_arr)):
        if yt_client.get_artist_track(song_arr[i]["title"]) is None:
            song_arr[i] = song_arr[i]["title"] 
        else:
            song_arr[i] = yt_client.get_artist_track(song_arr[i]["title"])
    
    uri_list = []
    found_counter = 0
    for i in range(len(song_arr)):
        artist = song_arr[i][0]
        track = song_arr[i][1]
        uri = spot_client.search_song(artist, track)
        if uri is None:
            print(f"No song found for {artist} {track}")
        else:
            uri_list.append(uri)
            print(f"Found {artist} {track}")
            found_counter += 1

    print(f"Found {found_counter} out of {len(song_arr)} songs on spotify")

    # Make request to add 100 songs to playlist (max)
    request_lists = []
    start_i = 0
    end_i = 100

    for i in range(len(uri_list) // 100):
        request_lists.append(uri_list[start_i:end_i])
        start_i += 100
        end_i += 100
    
    end_i -= 100
    end_i += len(uri_list) % 100
    request_lists.append(uri_list[start_i:end_i])

    
    for request in request_lists:
        spot_client.add_songs(spot_playlist_id, request)

    print("Songs added")

    
