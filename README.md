RootNotebook - Build a Spotify Playlist With Python

1. Install Python 3 (python.org) and extract these files.
2. Open PowerShell inside this folder.
3. Run: py -m venv .venv
4. Run: .\.venv\Scripts\Activate.ps1
   If activation is blocked:
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
5. Run: python -m pip install -r requirements.txt
6. Create an app at https://developer.spotify.com/dashboard
   Set redirect URI to http://127.0.0.1:8888/callback
   Spotify Development Mode currently requires Premium for the app owner.
7. In the same PowerShell window:
   $env:SPOTIPY_CLIENT_ID = "YOUR_CLIENT_ID"
   $env:SPOTIPY_REDIRECT_URI = "http://127.0.0.1:8888/callback"
8. Run: python .\playlist_maker.py
9. Search for tracks, select their numbers, finish with a blank query.
10. Type CREATE to publish your private playlist.

This program does not modify existing playlists.
It shows up to 10 search results per query; try more specific terms to find alternate versions.
If you see 429, stop and try later; do not keep rerunning the scan.
Don't share your Client Secret or authentication cache file.
