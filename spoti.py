"""Scraper through Spotify API."""

import os
from functools import lru_cache

import pandas as pd
import spotipy
from spotipy.cache_handler import CacheFileHandler
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyClientCredentials


# =================================================================================================
def _connect_spotify(project_path: str = ".") -> spotipy.Spotify:
    """Return a connected Spotify client via ClientCredentials flow."""

    cache_path = os.path.join(project_path, ".spotipy_cache")
    if os.path.exists(cache_path):
        os.remove(cache_path)

    auth = SpotifyClientCredentials(cache_handler=CacheFileHandler(cache_path=cache_path))
    sp = spotipy.Spotify(auth_manager=auth)

    # Simple connectivity test
    try:
        _ping = sp.search(q="test", type="track", limit=1)  # silent/test vars
        _items = _ping.get("tracks", {}).get("items", [])
        print("Spotipy connected")
    except Exception as e:
        print(f"[Warning] Spotipy failed: {e}")
    return sp


# =================================================================================================
def _search_track(sp: spotipy.Spotify, title: str, artist: str) -> dict | None:
    """Search Spotify for a given title/artist and return top track metadata."""

    q = f'track:"{title}" artist:"{artist}"'
    try:
        results = sp.search(q=q, type="track", limit=3)
        items = results.get("tracks", {}).get("items", [])
        if not items:
            return None
        track = items[0]
        return {
            "SpotifyID": track.get("id"),
            "Fame": track.get("popularity"),
            "Year": (track.get("album", {}) or {}).get("release_date", "")[:4],
        }
    except SpotifyException as e:
        print(f"[SpotifyException] search failed for {q}: {e}")
    except Exception as e:
        print(f"[Error] Spotify search failed for {q}: {e}")
    return None


# =================================================================================================
def enrich_spotify(df: pd.DataFrame, project_path: str = ".") -> pd.DataFrame:
    """Augment df with Spotify-derived columns (e.g., Fame, Year)."""

    sp = _connect_spotify(project_path)

    # Optional memo in case rows repeat artist/title
    @lru_cache(maxsize=2048)
    def _search_cached(title, artist):
        return _search_track(sp, title, artist) or {}

    rows = []
    for row in df.itertuples(index=False):
        title, artist, file_name = (
            getattr(row, "Title", None),
            getattr(row, "Artist", None),
            getattr(row, "File", None),
        )
        if not (title and artist):
            continue
        meta = _search_cached(title, artist)
        if meta:
            meta["File"] = file_name
            rows.append(meta)

    if not rows:
        print("Spotify search returned no matches; returning original DataFrame.")
        return df.copy()

    df_sp = pd.DataFrame(rows)
    print(f"Matched {len(df_sp)} / {len(df)} files on Spotify.")

    # Merge all Spotify metadata back onto the original rows
    df_out = df.merge(df_sp, on="File", how="left")
    return df_out


def prefer_columns(df: pd.DataFrame, pairs: list[tuple[str, str]]) -> pd.DataFrame:
    """Prefer source columns when filling final columns, then drop the sources."""

    out = df.copy()
    for preferred, final in pairs:
        if preferred not in out.columns:
            continue
        if final in out.columns:
            out[final] = out[final].where(out[final].notna(), out[preferred])
        else:
            out[final] = out[preferred]
        out.drop(columns=[preferred], inplace=True, errors="ignore")
    return out
