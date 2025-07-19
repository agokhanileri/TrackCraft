# Author: AGI

"""pip install: mutagen tinytag + spotipy."""

import os
import pandas as pd
from tinytag import TinyTag
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from bs4 import BeautifulSoup as bs
import json
# import openai

user = 'agi'
input_path = "/Users/" + user + "/Desktop"
folder_path = "/Users/" + user + "/Desktop/agiTracks/Bardo"
output_path = input_path
os.chdir(output_path)

# 1) Access the tracks and capture metadata
audio_data = []
for file in os.listdir(folder_path):
    if file.endswith(('.mp3', '.flac', '.wav', '.m4a')):  # Supported formats
        file_path = os.path.join(folder_path, file)
        tag = TinyTag.get(file_path)
        metadata = {
            'File': file,
            'Artist': tag.artist,
            'Title': tag.title,
            'Genre': tag.genre,
            'Year': tag.year,
            'SampleRate': tag.samplerate,
            'BitRate': tag.bitrate,
            'BitDepth': tag.bitdepth,
            'Duration': tag.duration,
            'Album': tag.album,
            'AlbumArtist': tag.albumartist,
            'Composer': tag.composer,
            'Offset': tag.audio_offset,
            'Channels': tag.channels,
            'Comment': tag.comment,
            'Extra': tag.extra,
            'Size': tag.filesize
            }
        audio_data.append(metadata)

metadata = audio_data  # if used within a func: extract_audio_metadata(folder_path)

# metadata[0]['Title']          # access brute-force
# for track in metadata:         # print brute-force
#    print(track)

df0 = pd.DataFrame(metadata)     # pandas is better
# df0['Title']                    # access via pandas
first_row = df0.iloc[0]          # //
# df0.columns                     #
df0.to_csv(output_path + "/df0.csv", index=False, sep='\t')


# 2) Set the columns and format
def seconds2mins(seconds):
    """Convert time to mm:ss format."""
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{int(minutes)}:{int(remaining_seconds):02}"


df1 = df0  # buffer first
# df1 = df1.drop(['BitDepth', 'SampleRate', 'AlbumArtist', 'Composer', 'Album', 'Size',
#                'Extra', 'Comment', 'Offset', 'Channels'], axis=1) # drop unused cols
# df1 = df0['File', 'Artist', 'Title', 'Genre', 'Year', 'Duration', 'Size', 'BitRate']
df1['Year'] = df0['Year'].str[:4]  # just need the year
df1['BitRate'] = df0['BitRate'].round(0)
df1['Size'] = (df0['Size'] / 1024**2).round(0)
df1['Duration'] = df0['Duration'].apply(seconds2mins)

# df1.to_csv(output_path + "/df1.csv", index=False, sep='\t')
df1['Key'] = None
df1['BPM'] = None
df1['Type'] = None
df1['Fame'] = None
df1['Mood'] = None
df1['Energy'] = None
df1['Dancey'] = None
df1['Remarks'] = None

new_column_order = ['File', 'Genre', 'Year', 'Duration', 'Key', 'BPM', 'Fame', 'Mood', 'Energy',
                    'Dancey', 'BitRate', 'Size', 'Type', 'Artist', 'Title', 'Remarks']
df1 = df1[new_column_order]


# 3) Fix columns and formatting
# 3a) Order: File - Artist - Title - Genre - Year - Duration - Size - BitRate - BitDepth - BPM
with pd.ExcelWriter('output.xlsx', engine='openpyxl') as writer:  # save DF to Excel
    df1.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

# 3b) Extract extention
# 3c) Smaller Case
# 3d) Move the ft. to comments
# 3e) get size from file directly


# 4) Scrape for: Key, BPM, Fame, Mood, Energy, Dancey
client_id = '87d49912361f4c52bb1c2e4cf1046628'
client_secret = '74d05e1f882d4a299638d7fe36b52830'
client_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_manager)
# playlist_id = '1EDcxh5STcNeXU66vUhLT9'

first_row = df1.iloc[3]
if str(first_row['Title']) is None:  # if Title is missing
    song = first_row.Title  # search for the filename directly
elif str(first_row['Artist']) is None:  # if just Artist is missing
    song = str(first_row['Title'])  # search for the Title only
else:  # both available --> construct the full search pattern
    song = str(first_row['Artist']) + ' - ' + str(first_row['Title'])

track_results = sp.search(q=song, type="track", limit=1)

track = track_results['tracks']['items'][0]
track_id = track['id']

# Fetch the audio features for the track
audio_features = sp.audio_features(track_id)[0]

# Print the audio features
print(f"BPM: {audio_features['tempo']}")
print(f"Energy: {audio_features['energy']}")
print(f"Key: {audio_features['key']}")
print(f"Valence (Mood): {audio_features['valence']}")
print(f"Danceability: {audio_features['danceability']}")


def get_track_features(token=None, track_id=None):
    """Get track features."""
    url = "https://api.spotify.com/v1/audio-features/"+track_id
    with requests.session() as sesh:
        header = {"Authorization": "Bearer {}".format(token)}
        response = sesh.get(url, headers=header)
        feature = str(bs(response.content, "html.parser"))
        return json.loads(feature)


query_ids = [track_id]
response = sp.audio_features(query_ids)


# 5) Handle duplicates and suggest best version
# 6) Visualize and mark outliers
# 6a) Genre / BPM / Year /
# 6b) Fame / Energy /
