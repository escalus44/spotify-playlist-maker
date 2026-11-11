"""Beginner Spotify playlist maker (Spotify Web API, November 2026).
Requires: pip install spotipy requests
Environment: SPOTIPY_CLIENT_ID and SPOTIPY_REDIRECT_URI
"""
import os
import re
import sys
import requests
from spotipy.oauth2 import SpotifyPKCE

API = "https://api.spotify.com/v1"
SCOPES = "playlist-modify-private"


def request(method, path, token, **kwargs):
    response = requests.request(
        method, API + path,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
        **kwargs,
    )
    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After", "unknown")
        raise RuntimeError(
            f"Spotify rate limit reached. Try again later (Retry-After: {retry_after} seconds). "
            "Your selections have NOT been published."
        )
    if response.status_code == 401:
        raise RuntimeError("Spotify authentication expired. Re-run to sign in again.")
    if response.status_code == 403:
        raise RuntimeError("Spotify denied access (403). Check Spotify Premium, app settings, and account permissions.")
    try:
        response.raise_for_status()
    except requests.HTTPError as error:
        raise RuntimeError(f"Spotify API error: {response.status_code} {response.text[:400]}") from error
    return response.json() if response.content else {}


def main():
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback")
    if not client_id:
        sys.exit("Set SPOTIPY_CLIENT_ID in your terminal first.")

    auth = SpotifyPKCE(client_id=client_id, redirect_uri=redirect_uri, scope=SCOPES, open_browser=True)
    token_data = auth.get_access_token()
    token = token_data.get("access_token") if isinstance(token_data, dict) else token_data
    if not isinstance(token, str) or not token:
        sys.exit("Spotify did not return a usable access token.")

    picks = []
    seen = set()
    print("\nSPOTIFY PLAYLIST MAKER")
    print("Search, choose track numbers, and press Enter on a blank search to finish.\n")

    while True:
        query = input("Search for a song or artist (blank = finish): ").strip()
        if not query:
            break
        result = request("GET", "/search", token, params={"q": query, "type": "track", "limit": 10})
        tracks = result.get("tracks", {}).get("items", [])
        if not tracks:
            print("No results. Try another search.\n")
            continue
        for index, track in enumerate(tracks, start=1):
            artist = ", ".join(a["name"] for a in track.get("artists", []))
            print(f"{index:>2}. {track['name']} — {artist} ({track['album']['name']})")
        raw = input("Numbers to add (example: 1,3,5; blank = skip): ").strip()
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            if not re.fullmatch(r"\d+", part) or not 1 <= int(part) <= len(tracks):
                print(f"Skipping invalid number: {part}")
                continue
            track = tracks[int(part) - 1]
            uri = track["uri"]
            if uri not in seen:
                picks.append(track)
                seen.add(uri)
        print(f"Selected so far: {len(picks)} unique tracks.\n")

    if not picks:
        print("No tracks selected. Nothing was created.")
        return

    print("\nYOUR TRACKS:")
    for index, track in enumerate(picks, start=1):
        print(f"{index:>3}. {track['name']} — {track['artists'][0]['name']}")
    name = input("\nPlaylist name: ").strip()
    if not name:
        print("No name entered. Nothing was created.")
        return
    if input(f"Create PRIVATE playlist '{name}' with {len(picks)} songs? Type CREATE: ").strip() != "CREATE":
        print("Canceled. Nothing was created.")
        return

    created = request("POST", "/me/playlists", token, json={"name": name, "public": False,
        "description": "Created with the RootNotebook beginner Spotify API playlist maker."})
    playlist_id = created["id"]
    uri_list = [track["uri"] for track in picks]
    try:
        for start in range(0, len(uri_list), 100):
            request("POST", f"/playlists/{playlist_id}/items", token, json={"uris": uri_list[start:start+100]})
    except RuntimeError:
        print(f"Playlist was created but adding songs was interrupted. Check: {created['external_urls']['spotify']}")
        raise
    print(f"\nDone! Your playlist: {created['external_urls']['spotify']}")
    print(f"Added {len(picks)} unique tracks in your selected order.")


if __name__ == "__main__":
    try:
        main()
    except (requests.RequestException, RuntimeError) as error:
        sys.exit(f"ERROR: {error}")
