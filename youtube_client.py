import requests
import json
import youtube_dl
from time import sleep
from youtube_title_parse import get_artist_title
import magic_parser 



class YoutubeClient:

    def __init__(self):
        self.api_key = self.set_api_key()

    
    def set_api_key(self):
        with open("secrets.json") as f:
            return json.load(f)["api_key"]


    def playlist_items(self, playlist_id) -> list:
        page_token = ""
        items = []
       
        while (page_token is not None):
            query = f"?part=snippet&playlistId={playlist_id}&key={self.api_key}&pageToken={page_token}"
            url = f"https://www.googleapis.com/youtube/v3/playlistItems{query}"

            response = requests.get(
                url,
                headers={
                    "Accept": "application/json"
                })

            content = json.loads(response.content)

            if "error" in content:
                error_code = content["error"]["code"]
                message = content["error"]["message"]
                raise Exception(f"Error receiving playlist {error_code} {message}")

            for i in range(len(content["items"])):
                items.append(content["items"][i]["snippet"])

            if not "nextPageToken" in content:
                page_token = None
            else:
                page_token = content["nextPageToken"]

        return items
            

    @staticmethod
    def get_artist_track(song_title):
        clean_title = magic_parser.clean_songname(song_title)
        return get_artist_title(clean_title)


if __name__ == "__main__":
    client = YoutubeClient()
    # print(client.set_api_key())
    print("Receiving items....")
    song_arr = client.playlist_items("")

    print(f"Found {len(song_arr)} items ")
    sleep(2)
    for e in song_arr:
        print(client.get_artist_track(e["title"]))

if __name__ == "__main__1":
    YoutubeClient.get_artist_track("DOcHZjMKBL8")
