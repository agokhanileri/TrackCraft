# TrackCraft

Audio tracks analyzer, enriching, and normalizing audio metadata from a local library.

## Structure
- `trackcraft.py` – Main driver via CLI.
- `inputs/` - Input path to load tracks.
- `outputs/` – Output path to dump logs, statistical reports, and graphs.
- `load_tracks.py` – File I/O and load ops.


## Overview
1. Load tracks from a given folder
2. Pull year and popularity from Spotify
3. Extract other features

## Requirements
- Python 3.12+
- Spotify API credentials in env variables: `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET`

## Manual
Run the CLI from the repository root.
```bash
python trackcraft.py full --input-dir ./inputs --output-dir ./outputs [--skip-spotify]
```

Each step saves intermediate TSVs into `outputs/` and logs skipped files to `outputs/skipped.txt` when applicable.