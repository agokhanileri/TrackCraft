"""Load tracks by parsing filenames using convention:
Artist = Artist1 & Artist2 & ...
Title  = Song (Artist3 Remix) [ft. Artist4]"""

import os
import re
import unicodedata

import pandas as pd


# =================================================================================================
def _normalize(text: str) -> str:
    """Normalize spaces and remove accents."""
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8", "ignore")
    return re.sub(r"\s+", " ", text.strip())


def _parse_filename(fname: str) -> dict:
    """
    Parse filename into Artist / Title using convention:
      Artist – Title
      Artist - Title (Remix)
      Artist1 & Artist2 – Track (Artist3 Remix) [ft. Artist4]
    """
    stem = _normalize(os.path.splitext(os.path.basename(fname))[0])
    parts = re.split(r"\s+[–-]\s+", stem, maxsplit=1)

    if len(parts) == 2:
        artist, title = parts
    else:
        artist, title = "", parts[0]  # fallback: no dash found

    return {"File": fname, "Artist": artist, "Title": title}


# =================================================================================================
def load_tracks(path: str) -> pd.DataFrame:
    folder = os.path.expanduser(path)
    if not os.path.exists(folder):
        raise FileNotFoundError(f"Tracks folder not found: {folder}")

    valid_exts = (".wav", ".aiff", ".flac", ".mp3", ".m4a", ".txt", ".csv", ".tsv")
    files = [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in valid_exts]

    if not files:
        print(f"No valid files found in {folder}")
        return pd.DataFrame(columns=["File", "Artist", "Title"])

    rows = [_parse_filename(f) for f in files]
    df = pd.DataFrame(rows)
    print(f"Loaded {len(df)} items from {folder}\n")
    return df
