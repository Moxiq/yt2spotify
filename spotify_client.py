import json
import base64
import requests
import webbrowser
import urllib.parse



class SpotifyClient:

    def __init__(self):
        self.auth_code = None
        self.auth_token = None
        self.secrets = None
        self.settings = None

        self.playlist_name = None
        self.playlist_id = None

        self.load_settings()
        self.load_secrets()

    def authenticate_all(self):
        self.authenticate_user()
        self.set_auth_code(input("Enter the authentication token from the redirected page \n"))
        self.request_token()

    # Scopes are set to playlist-modify-private and playlist-modify-public
    def authenticate_user(self):
        redirect_uri = urllib.parse.quote("https://www.google.com/")
        client_id = self.secrets["client_id"]
        url = f"https://accounts.spotify.com/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope=playlist-modify-private%20playlist-modify-public"
        webbrowser.open(url)

    def set_auth_code(self, auth_code):
        self.auth_code = auth_code

    def request_token(self):
        client_id = self.secrets["client_id"]
        client_secret = self.secrets["client_secret"]
        base64_string = base64.b64encode("{}:{}".format(client_id, client_secret).encode("utf-8")).decode("utf-8")
        if (self.auth_code):
            url = "https://accounts.spotify.com/api/token"
            response = requests.post(
                url,
                headers={
                    "Authorization": f"Basic {base64_string}"
                },
                data={
                    "grant_type": "authorization_code",
                    "code": self.auth_code,
                    "redirect_uri": "https://www.google.com/"
                }
            )

            if response.status_code == 200:
                self.auth_token = response.json()["access_token"]
            else:
                raise Exception (f"Couldn't access token, ERROR CODE:{response.status_code}")
    
    def load_secrets(self):
        with open("secrets.json") as f:
            self.secrets = json.load(f)

    def load_settings(self):
        with open("user_settings.json") as f:
            self.settings = json.load(f)

    #Returns tuple(True/False, playlist_id)
    def playlist_exists(self):
        url = "https://api.spotify.com/v1/me/playlists"
        response = requests.get(
            url, 
            headers={
                "Authorization": f"Bearer {self.auth_token}"
            }
        )
        if response.status_code > 300:
            raise Exception (f"Error getting playlists {response.status_code}")
            # raise Exception (f"Error getting playlists, ERROR CODE {response.status_code}")
        else: 
            content = response.json()
            playlist_counter = len(content["items"])
            for i in range(playlist_counter):
                if content["items"][i]["name"] == self.playlist_name:
                    return True, content["items"][i]["id"]

            return False, -1

    def search_song(self, artist, track) -> str:
        query = urllib.parse.quote(f'{artist} {track}')
        type_ = "track"
        url = f"https://api.spotify.com/v1/search?q={query}&type={type_}"
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.auth_token}"
            }
        )
        content = response.json()

        if response.status_code == 401:
            raise Exception("Invalid token")

        results = content["tracks"]["items"]
        
        if results:
            return "spotify:track:" + results[0]["id"]
        else:
            return None

    def add_playlist(self) -> str:
        request_body = json.dumps({
            "name": self.settings["playlist_name"],
            "description": "Youtube playlist to Spotify playlist"
        })
        query = "https://api.spotify.com/v1/users/{}/playlists".format(self.settings["user_id"])
        response = requests.post(
            query, 
            data=request_body,
            headers={
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
             })
        
        content = response.json()

        if response.status_code == 201:
            return content["id"]
        else:
            raise Exception (f"Failed creating playlist {response.status_code} \n {response.content}")

    #MAXIMUM OF 100 SONGS PER CALL
    def add_songs(self, playlist_id, songs: list):
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        request_body = json.dumps({
            "uris": songs
        })
        
        response = requests.post(
            url,
            data=request_body,
            headers={
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
        )

        content = response.json()
        if "error" in content:
            error_code = content["error"]["status"]
            message = content["error"]["message"]
            raise Exception (f"Error adding songs {error_code} {message}")

    # TODO: Reverse order of a user's playlist
    def reverse_playlist(self):
        pass
        



if __name__ == "__main__":
    #Authentication stuff
    client = SpotifyClient()
    client.authenticate_all()

    #Adding songs to a current yt2spotify playlist or create a new one if it doesn't exist
    song_arr = []
    song = client.search_song("2Pac", "It ain't easy")
    song2 = client.search_song("Abba", "Dancing queen")
    song_arr.append(song)
    song_arr.append(song2)

    playlist_exists, playlist_idd = client.playlist_exists()
    if playlist_exists:
        client.add_songs(playlist_idd, song_arr)
    else:
        playlist_idd = client.add_playlist()
        client.add_songs(playlist_idd, song_arr)