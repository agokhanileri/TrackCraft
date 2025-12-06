"""TrackCraft main driver."""

import os

from access import load_tracks
from analysis import analyze_tracks
from spoti import enrich_spotify

# =================================================================================================
# Control knobs:
report = True
plot = False

# Project paths:
project_path = os.path.expanduser("~/Git/TrackCraft/")
input_path = os.path.join(project_path, "inputs")  # not 'inputs/metadata'
output_path = os.path.join(project_path, "outputs")

# make sure outputs exists
os.makedirs(output_path, exist_ok=True)


# =================================================================================================
def main():
    # 1) Load raw metadata
    df0 = load_tracks(input_path)
    df0.to_csv(os.path.join(output_path, "df0.tsv"), index=False, sep="\t")  # save it
    # print(f"Loaded {len(df0)} tracks.")

    # 2) Enrich with Spotify (Fame, Year)
    df1 = enrich_spotify(df0, input_path)
    # print(f"Enriched {len(df1)} tracks utilizing Spotify API.")
    df1.to_csv(os.path.join(output_path, "df1.tsv"), index=False, sep="\t")  # save it

    # 3) Analyze results
    analyze_tracks(df1, report, plot)


if __name__ == "__main__":
    main()


# =================================================================================================
# 1) Extract metadata


# =================================================================================================
# 3) Report: Visualize and mark outliers
# df1.to_csv("~/Desktop/df1.csv", index=False, sep="\t")  # after formatting
# df2.to_csv("~/Desktop/df2.csv", index=False, sep="\t")  # spotify metadata
# df3.to_csv("~/Desktop/df3.csv", index=False, sep="\t")  # merged metadata
# df4.to_csv("~/Desktop/df1.csv", index=False, sep="\t")  # after final reformatting
# m0, n0 = df0.shape
# m1, n1 = df1.shape


# =================================================================================================
# 4) Naming:
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

# Handle duplicates: Suggest best version

# =================================================================================================
# Extract Type: Optional, in case the extension was misleading
# Extract Fame:
# Extract Tempo:
# Extract Key:
# Extract Groove
# Extract Energy
# Extract Mood
# Extract Genre: Difficult, needs API + clustering
# Convention: Classical, Electronic, Rock, Metal, Soul (Reggea, HipHop)
# Extract Size: Get size from file directly
