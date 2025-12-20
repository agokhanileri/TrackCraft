from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# =================================================================================================
_SHARP_EQUIV = {
    "Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#",
}
_KEY_BASES = {"C","C#","D","D#","E","F","F#","G","G#","A","A#","B",
              "Cb","Db","Eb","Gb","Ab","Bb"}  # accept flats then map

def _canonical_key(key_raw: str) -> str:
    """
    Normalize musical key into a compact token with mode baked in.
    Examples:
      "A minor" -> "Am"
      "C# Minor" -> "C#m"
      "Ab major" -> "G#" (normalize flats to sharps)
      "F" -> "F"
    """
    if not isinstance(key_raw, str) or not key_raw.strip():
        return "Unknown"
    s = key_raw.strip().title()  # e.g., "C# Minor", "Ab Major", "F"
    # Extract base + optional mode
    parts = s.replace("Minor", "minor").replace("Major", "major").split()
    base, mode = parts[0], ("minor" if any("minor" in p for p in parts[1:]) else None)
    # Normalize base to sharp form when possible
    if base in _SHARP_EQUIV:
        base = _SHARP_EQUIV[base]
    # Validate base
    if base not in _KEY_BASES and base not in _SHARP_EQUIV.values():
        return "Unknown"
    # Compose compact token
    return f"{base}m" if mode == "minor" else base

_GENRE_MAP: dict[str, str] = {
    # Electronic
    "electro":"Electronic","electronic":"Electronic","edm":"Electronic",
    "house":"Electronic","techno":"Electronic","trance":"Electronic",
    "dnb":"Electronic","drum & bass":"Electronic","drum and bass":"Electronic",
    "dubstep":"Electronic","garage":"Electronic","breaks":"Electronic",
    "progressive":"Electronic","psytrance":"Electronic","melodic house":"Electronic",
    "hardstyle":"Electronic","tech house":"Electronic",
    # Pop
    "pop":"Pop","dance pop":"Pop","synthpop":"Pop","k-pop":"Pop","indie pop":"Pop",
    # Rock
    "rock":"Rock","alt rock":"Rock","alternative rock":"Rock","hard rock":"Rock",
    "punk":"Rock","metal":"Rock","indie rock":"Rock","grunge":"Rock",
}

def _bucket_genre(g: str) -> str:
    """Map any genre string to Pop / Electronic / Rock / Other."""
    if not isinstance(g, str) or not g.strip():
        return "Other"
    s = g.strip().lower()
    # try exact and substring matches
    if s in _GENRE_MAP:
        return _GENRE_MAP[s]
    for k, v in _GENRE_MAP.items():
        if k in s:
            return v
    return "Other"

def _classify_mood(x) -> str:
    """
    Classify mood to firm / medium / soft.
    Accepts 0..1 or 0..100; coerces to 0..1.
    """
    try:
        val = float(x)
    except Exception:
        return "Unknown"
    if val > 1.0:
        val /= 100.0
    if val >= 0.66:
        return "firm"
    if val <= 0.33:
        return "soft"
    return "medium"

# =================================================================================================
def compute_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute summary stats with key-mode fusion, genre bucketing, and mood classes."""
    stats: dict[str, object] = {"num_tracks": len(df)}

    # ----- Numeric summaries (if present)
    for col in ["Year", "BPM", "Energy", "Danceability", "Loudness", "DurationS", "DurationMs"]:
        if col in df.columns:
            s = pd.to_numeric(df[col], errors="coerce")
            prefix = col.lower()
            stats[f"{prefix}_min"] = float(s.min(skipna=True)) if s.notna().any() else None
            stats[f"{prefix}_max"] = float(s.max(skipna=True)) if s.notna().any() else None
            stats[f"{prefix}_mean"] = float(s.mean(skipna=True)) if s.notna().any() else None
            stats[f"{prefix}_std"] = float(s.std(skipna=True)) if s.notna().any() else None

    # ----- Key distribution (mode embedded)
    key_col = "Key" if "Key" in df.columns else ("key" if "key" in df.columns else None)
    if key_col:
        keys = df[key_col].map(_canonical_key)
        key_counts = keys.value_counts(dropna=False)
        # store top 7 for brevity
        stats["key_top"] = key_counts.head(7).to_dict()

    # ----- Genre → Pop/Electronic/Rock mapping
    genre_col = "Genre" if "Genre" in df.columns else ("genre" if "genre" in df.columns else None)
    if genre_col:
        buckets = df[genre_col].map(_bucket_genre)
        pct = (buckets.value_counts(normalize=True) * 100).round(1)
        # ensure all three categories present
        for cat in ["Pop", "Electronic", "Rock"]:
            stats[f"genre_{cat.lower()}_pct"] = float(pct.get(cat, 0.0))
        # optional: report Other
        stats["genre_other_pct"] = float(pct.get("Other", 0.0))

    # ----- Mood class distribution
    # Prefer "Mood" column; fall back to "Valence" if present
    mood_basis = None
    for cand in ["Mood", "mood", "Valence", "valence"]:
        if cand in df.columns:
            mood_basis = cand
            break
    if mood_basis:
        classes = df[mood_basis].map(_classify_mood)
        mood_pct = (classes.value_counts(normalize=True) * 100).round(1)
        for cat in ["firm", "medium", "soft"]:
            stats[f"mood_{cat}_pct"] = float(mood_pct.get(cat, 0.0))
        stats["mood_unknown_pct"] = float(mood_pct.get("Unknown", 0.0))

    return pd.DataFrame([stats])


def plot_distributions(df: pd.DataFrame, out_dir: str = "outputs/plots") -> None:
    """Generate basic distribution plots for BPM and Key (with fused mode)."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    # Prepare BPM series (if present)
    bpm = None
    if "BPM" in df.columns:
        bpm = pd.to_numeric(df["BPM"], errors="coerce").dropna()

    # Prepare Key tokens
    key_col = "Key" if "Key" in df.columns else ("key" if "key" in df.columns else None)
    key_series = df[key_col].map(_canonical_key) if key_col else None

    # Build figure with 1–2 panels depending on availability
    if bpm is not None and key_series is not None:
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        bpm.plot.hist(ax=axes[0], bins=24, alpha=0.7)
        axes[0].set_title("BPM Distribution")
        axes[0].set_xlabel("BPM")
        axes[0].set_ylabel("Count")

        key_series.value_counts().sort_index().plot.bar(ax=axes[1], alpha=0.7)
        axes[1].set_title("Key Distribution (mode fused)")
        axes[1].set_xlabel("Key")
        axes[1].set_ylabel("Count")
    elif bpm is not None:
        fig, ax = plt.subplots(1, 1, figsize=(5, 4))
        bpm.plot.hist(ax=ax, bins=24, alpha=0.7)
        ax.set_title("BPM Distribution")
        ax.set_xlabel("BPM")
        ax.set_ylabel("Count")
    elif key_series is not None:
        fig, ax = plt.subplots(1, 1, figsize=(5, 4))
        key_series.value_counts().sort_index().plot.bar(ax=ax, alpha=0.7)
        ax.set_title("Key Distribution (mode fused)")
        ax.set_xlabel("Key")
        ax.set_ylabel("Count")
    else:
        return  # nothing to plot

    plt.tight_layout()
    plt.savefig(f"{out_dir}/metadata_distributions.png")
    plt.close()


def analyze_tracks(df: pd.DataFrame, do_report: bool=True, do_plot: bool=True) -> pd.DataFrame:
    """Run metadata analysis pipeline with your specified stats."""
    result = None
    if do_report:
        result = compute_statistics(df)
        print(result.to_string(index=False))
    if do_plot:
        plot_distributions(df)
        print("Plots saved under outputs/plots/")
    return result
