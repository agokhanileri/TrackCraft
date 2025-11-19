"""Tracks organizer."""

import os

import pandas as pd
import spotipy
from spotipy.cache_handler import CacheFileHandler
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyClientCredentials
from tinytag import TinyTag

# import json
# import math
# import openai
# import requests
# import sys

# =================================================================================================
# 1) Extract metadata
project_path = os.path.expanduser("~/Git/TrackCraft/")
input_path = os.path.expanduser("~/Git/TrackCraft/inputs/")
output_path = os.path.expanduser("~/Git/TrackCraft/outputs/")

SUPPORTED_EXT = (".mp3", ".flac", ".wav", ".m4a", ".aiff", ".aif")
audio_data = []
skipped_files = []


# Function to extract artist and title (with minimal exceptions) to be searched on APIs
def extract_song(file_name: str, artist_tag, title_tag):
    """Fallback: infer artist/title from filename if tags are missing."""
    stem = os.path.splitext(str(file_name))[0]
    stem = stem.replace(" – ", " - ").replace("—", "-")
    parts = [p.strip() for p in stem.split(" - ", 1)]

    artist = (artist_tag or "").strip() or None
    title = (title_tag or "").strip() or None

    if not artist or not title:
        if len(parts) == 2:
            if not artist:
                artist = parts[0] or None
            if not title:
                title = parts[1] or None
        elif not title:
            title = stem or None

    return artist, title


for file in os.listdir(input_path):  # for every file in the given dir
    # TODO: extract the actual file type instead of relying on the original file naming
    if not file.lower().endswith(SUPPORTED_EXT):  # continue if the extension matches
        continue

    file_path = os.path.join(input_path, file)

    try:
        tag = TinyTag.get(file_path)  #
        ext = os.path.splitext(file)[1].lower().lstrip(".").upper()  # extract extension

        raw_artist = getattr(tag, "artist", None)
        raw_title = getattr(tag, "title", None)
        artist, title = extract_song(file, raw_artist, raw_title)  # extract

        # If still nothing usable, mark skipped
        if not artist and not title:
            skipped_files.append(file)
            continue

        # ISRC is a unique song identifier, but can't be found for WAV/AIFF
        # TODO: manually add for WAV/AIFF later
        # TinyTag sometimes hides ISRC codes in tag.other or tag.extra instead of top-level
        other = getattr(tag, "other", {}) or {}
        isrc = next((v for k, v in other.items() if "isrc" in k.lower()), None)

        metadata = {
            "File": file,
            "Title": title,
            "Artist": artist,
            "Genre": getattr(tag, "genre", None),
            "Year": getattr(tag, "year", None),
            "Duration": getattr(tag, "duration", None),
            "Type": ext,
            "BitRate": getattr(tag, "bitrate", None),
            "Size": (
                getattr(tag, "filesize", None) / (1024 * 1024)
                if getattr(tag, "filesize", None)
                else None
            ),
            "SampleRate": getattr(tag, "samplerate", None),
            "BitDepth": getattr(tag, "bitdepth", None),
            "Album": getattr(tag, "album", None),
            "AlbumArtist": getattr(tag, "albumartist", None),
            "Composer": getattr(tag, "composer", None),
            "Channels": getattr(tag, "channels", None),
            "Comment": getattr(tag, "comment", None),
            "Other": getattr(tag, "other", None),
            "ISRC": isrc,
        }

        audio_data.append(metadata)

    except Exception as e:
        skipped_files.append(f"{file} | error: {e}")


# if used within a func: extract_audio_metadata(folder_path)
# audio_data[0]["Title"]  # direct access example

df0 = pd.DataFrame(audio_data)  # pandas is better
# df0['Title']  # list songs
# track1 = df0.iloc[0]  # first song
# df0.columns                     #
df0.to_csv(output_path + "/df0.csv", index=False, sep="\t")


def seconds2mins(seconds):
    """Convert time to mm:ss format."""
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{int(minutes)}:{int(remaining_seconds):02}"


df1 = df0  # buffer first --> may need to discard df0 later
# df1 = df1.drop(['BitDepth', 'SampleRate', 'AlbumArtist', 'Composer', 'Album', 'Size',
#                'Extra', 'Comment', 'Offset', 'Channels'], axis=1) # drop unused cols
# df1 = df0['File', 'Artist', 'Title', 'Genre', 'Year', 'Duration', 'Size', 'BitRate']
df1["Year"] = df0["Year"].str[:4]  # just need the year
df1["BitRate (kbps)"] = df0["BitRate"].round(0)
df1["Size (MB)"] = (df0["Size"] / 1024**2).round(0)
df1["Duration"] = df0["Duration"].apply(seconds2mins)

# df1.to_csv(output_path + "/df1.csv", index=False, sep='\t')
df1["Key"] = None
df1["BPM"] = None
df1["Fame"] = None
df1["Mood"] = None
df1["Energy"] = None  #
df1["Groove"] = None  # danceability
df1["Comment"] = None
new_column_order = [
    "File",
    "Title",
    "Artist",
    "Genre",
    "Year",
    "Duration",
    "BPM",
    "Key",
    "Energy",
    "Groove",
    "Mood",
    "Fame",
    "Type",
    "BitRate (kbps)",
    "Size (MB)",
    "Comment",
]
df1 = df1[new_column_order]
# df1.to_csv(output_path + "/df1.csv", index=False, sep="\t")
# optional Excel output
# with pd.ExcelWriter("output.xlsx", engine="openpyxl") as writer:  # save DF to Excel
#    df1.to_excel(writer, index=False, sheet_name="Sheet1")
#    workbook = writer.book
#    worksheet = writer.sheets["Sheet1"]


# =================================================================================================
# 2) Enhance metadata
# API connect:
# print(os.getenv("SPOTIPY_CLIENT_ID"))  # for test
cache_path = os.path.join(project_path, ".spotipy_cache")  # kill the cache to prevent ambiguity
if os.path.exists(cache_path):
    os.remove(cache_path)

cache_path = os.path.join(project_path, ".spotipy_cache")
auth_manager = SpotifyClientCredentials(cache_handler=CacheFileHandler(cache_path=cache_path))
sp = spotipy.Spotify(auth_manager=auth_manager)

# First check API connection
try:
    ping = sp.search(q="test", type="track", limit=1)
    items = ping.get("tracks", {}).get("items", [])
    if items:
        print("Spotify API OK (search working).")
    else:
        print("Spotify API reachable, but no items returned for test query.")
except Exception as e:
    print(f"Spotify API error: {e}")


def get_track_features(sp, track_id: str) -> dict:
    """Return Spotify audio features for a track ID."""
    feats = sp.audio_features([track_id])
    return feats[0] if feats and feats[0] else {}


def get_audio_features_batch(sp, track_ids) -> list[dict]:
    """Fetch Spotify audio features in batches of up to 100 IDs."""
    all_features = []
    batch_size = 100

    for i in range(0, len(track_ids), batch_size):
        batch = track_ids[i : i + batch_size]
        try:
            feats = sp.audio_features(batch) or []
        except SpotifyException as e:
            print(f" audio_features failed for batch starting {batch[0]}: {e}")
            continue

        all_features.extend(f for f in feats if f)

    return all_features


# ------------------------------------------------------------------
test_search = sp.search(q="Eric Prydz Opus", type="track", limit=1)
print("Search items:", len(test_search["tracks"]["items"]))
# sanity: audio_features for a known good ID
test_id = "3v2oAQomhOcYCPPHafS3KV"  # Eric Prydz - Opus (public, has features)

features = sp.audio_features([test_id])[0]

try:
    test_feats = sp.audio_features([test_id])
    print("Audio features test:", test_feats)
except Exception as e:
    print("Audio features error:", repr(e))


def debug_audio_features(sp, track_id: str):
    try:
        feats = sp.audio_features([track_id])
        print("audio_features OK:", feats)
    except SpotifyException as e:
        print("audio_features SpotifyException:", e.http_status, repr(e))
    except Exception as e:
        print("audio_features generic error:", repr(e))


debug_audio_features(sp, "3v2oAQomhOcYCPPHafS3KV")

# ------------------------------------------------------------------
# Map local file to Spotify track via search
spotify_rows = []
for row in df1.itertuples(index=False):
    file_name = getattr(row, "File", None)
    title = getattr(row, "Title", None)
    artist = getattr(row, "Artist", None)

    print(file_name)  # TEMP
    if not file_name or not title or not artist:
        continue

    q = f'track:"{title}" artist:"{artist}"'
    results = sp.search(q=q, type="track", limit=3)
    items = results.get("tracks", {}).get("items", [])
    if not items:
        continue

    track = items[0]  # later: add scoring

    release_date = track["album"].get("release_date")
    year_sp = release_date[:4] if release_date else None

    spotify_rows.append(
        {
            "File": file_name,
            "SpotifyID": track["id"],
            # "SpotifyURL": track["external_urls"]["spotify"],
            "Fame_sp": track.get("popularity"),
            "Year_sp": year_sp,
            "ISRC": track.get("external_ids", {}).get("isrc"),
        }
    )


df2 = pd.DataFrame(spotify_rows)  # Spotify-only metadata per File
print(f"Matched {len(df2)} / {len(df1)} files via search.")

# Fetch audio features for all matched SpotifyIDs
if df2.empty:
    print("Problem: df2 is empty, copying df1 to df3")
    df3 = df1.copy()
else:
    # 2) Fetch audio features for matched SpotifyIDs
    track_ids = df2["SpotifyID"].dropna().unique().tolist()
    features = get_audio_features_batch(sp, track_ids)
    df_features = pd.DataFrame(features)  # has: id, tempo, energy, danceability, valence, key, ...

    # Merge into df2
    df2 = df2.merge(df_features, left_on="SpotifyID", right_on="id", how="left")

    # Keep only enrichment-relevant fields
    df2 = df2.rename(
        columns={
            "tempo": "BPM_sp",
            "energy": "Energy_sp",
            "danceability": "Groove_sp",
            "valence": "Mood_sp",
            "key": "Key_sp",
        }
    )[
        [
            "File",
            "BPM_sp",
            "Energy_sp",
            "Groove_sp",
            "Mood_sp",
            "Key_sp",
            "Fame_sp",
            "Year_sp",
        ]
    ]

    # 3) Build df3 = df1 enriched (user-facing)
    df3 = df1.merge(df2, on="File", how="left")

    # Prefer Spotify where available; fall back to df1
    def prefer_spotify(sp_col, base_col):
        if sp_col in df3.columns:
            df3[base_col] = df3[sp_col].combine_first(df3.get(base_col))
            df3.drop(columns=[sp_col], inplace=True)

    prefer_spotify("BPM_sp", "BPM")
    prefer_spotify("Energy_sp", "Energy")
    prefer_spotify("Groove_sp", "Groove")
    prefer_spotify("Mood_sp", "Mood")
    prefer_spotify("Fame_sp", "Fame")
    prefer_spotify("Key_sp", "Key")

    if "Year_sp" in df3.columns:
        df3["Year"] = df3["Year_sp"].combine_first(df3.get("Year"))
        df3.drop(columns=["Year_sp"], inplace=True)


# Extract Year:


# Extract Tempo:


# Extract Key:


# Extract Fame/Mood/Energy/Groove


# Enhance Name: Optional, fix the case and foreign letters
# - Convention: Artist1 & Artist2 – Track (Artist3 Remix) [ft. Artist4]
# first_row = df1.iloc[3]
# if str(first_row["Title"]) is None:  # if Title is missing
#     song = first_row.Title  # search for the filename directly
# elif str(first_row["Artist"]) is None:  # if just Artist is missing
#     song = str(first_row["Title"])  # search for the Title only
# else:  # both available --> construct the full search pattern
#     song = str(first_row["Artist"]) + " - " + str(first_row["Title"])
# print(first_row.File)

# Extract Type: Optional, in case the extension was misleading

# Enchance Genre: Difficult, needs API + clustering
# - Convention: Classical, Electronic (House, Techno, Trance), Rock (Metal), Soul (Reggea, HipHop)

# Extract Size: Get size from file directly

# Extract the audio features
# print(f"BPM: {audio_features['tempo']}")
# print(f"Energy: {audio_features['energy']}")
# print(f"Key: {audio_features['key']}")
# print(f"Valence (Mood): {audio_features['valence']}")
# print(f"Danceability: {audio_features['danceability']}")


# 5) Handle duplicates and suggest best version
# 6) Visualize and mark outliers
# 6a) Genre / BPM / Year /
# 6b) Fame / Energy /


# =================================================================================================
# 3) Visualize metadata
# df0.to_csv("~/Desktop/df1.csv", index=False, sep="\t")  #  raw metadata
df1.to_csv("~/Desktop/df1.csv", index=False, sep="\t")  # after formatting
df2.to_csv("~/Desktop/df2.csv", index=False, sep="\t")  # spotify metadata
df3.to_csv("~/Desktop/df3.csv", index=False, sep="\t")  # merged metadata
# df4.to_csv("~/Desktop/df1.csv", index=False, sep="\t")  # after final reformatting
m0, n0 = df0.shape
m1, n1 = df1.shape
