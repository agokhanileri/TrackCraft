"""TrackCraft package."""

from main.access import load_tracks
from main.analysis import analyze_tracks, compute_statistics, plot_distributions
from main.analysis2 import analyze_tracks2, compute_statistics2, plot_distributions2
from main.spoti import enrich_spotify, prefer_columns


# =================================================================================================
__all__ = [
    "analyze_tracks",
    "compute_statistics",
    "enrich_spotify",
    "load_tracks",
    "plot_distributions",
    "prefer_columns",
]