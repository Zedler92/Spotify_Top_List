from bs4 import BeautifulSoup
import requests
from requests_html import HTMLSession
import spotipy
from spotipy.oauth2 import SpotifyOAuth


chosen_date = input("Which year would you like to travel to? Type the date in this format: YYYY-MM-DD: \n")
year = chosen_date.split("-")[0]
WEB_PAGE = f"https://www.billboard.com/charts/hot-100/{chosen_date}/"
WEB_FILE = f"./data/100_top_of_{chosen_date}.html"

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="https://localhost:9021/callback/",
        client_id="78f2e8a1f39a4341af76bc9177ed1fec",
        client_secret="c8baedac7ff64648af9acfb0c0f6f4d4",
        show_dialog=True,
        cache_path="token.txt"
    )
)

user_id = sp.current_user()["id"]

# Using requests_html to render JavaScript
def get_web_page():
    # create an HTML Session object
    session = HTMLSession()
    # Use the object above to connect to needed webpage
    response = session.get(WEB_PAGE)
    # Run JavaScript code on webpage
    response.html.render()

    # Save web page to file
    with open(WEB_FILE, mode="w", encoding="utf-8") as fp:
        fp.write(response.html.html)

def read_web_file():
    try:
        open(WEB_FILE)
    except FileNotFoundError:
        get_web_page()
    finally:
        # Read the web page from file
        with open(WEB_FILE, mode="r", encoding="utf-8") as fp:
            content = fp.read()
        return BeautifulSoup(content, "html.parser")

#Getting the whole page
response = requests.get(url=f"https://www.billboard.com/charts/hot-100/{chosen_date}/")
response.raise_for_status()
content = response.text

soup = read_web_file()

titles = soup.find_all(name="h3", class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only")
artists = soup.find_all(name="span", class_='c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only')

song_titles = [title.getText().strip("\n\t") for title in titles]
artist_names = [name.getText().strip("\n\t") for name in artists]
print(len(song_titles))
print(len(artist_names))
song_and_artist = dict(zip(song_titles, artist_names))

print(song_and_artist)

#
songs_uris = []
for (song, artist) in song_and_artist.items():
    result = sp.search(q=f"track: {song} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        songs_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

top_100 = sp.user_playlist_create(user=user_id, name=f"{year} Billboard 100", public=False)

sp.playlist_add_items(playlist_id=top_100["id"], items=songs_uris)

