import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# =================================================================================================
def compute_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute basic summary statistics if columns exist."""
    stats = {"num_tracks": len(df)}

    for col in ["Year", "BPM", "Energy", "Danceability", "Loudness"]:
        if col in df.columns:
            s = pd.to_numeric(df[col], errors="coerce")
            stats[f"{col.lower()}_min"]  = s.min(skipna=True)
            stats[f"{col.lower()}_max"]  = s.max(skipna=True)
            stats[f"{col.lower()}_mean"] = s.mean(skipna=True)
            stats[f"{col.lower()}_std"]  = s.std(skipna=True)

    return pd.DataFrame([stats])


def plot_distributions(df: pd.DataFrame, out_dir: str = "outputs/plots") -> None:
    """Generate basic distribution plots for key metadata fields."""
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    df["tempo"].plot.hist(ax=axes[0], bins=20, alpha=0.7, title="Tempo Distribution")
    df["key"].value_counts().sort_index().plot.bar(ax=axes[1], alpha=0.7, title="Key Distribution")
    plt.tight_layout()
    plt.savefig(f"{out_dir}/metadata_distributions.png")
    plt.close()


def analyze(df: pd.DataFrame, do_report=True, do_plot=True) -> pd.DataFrame:
    """Run metadata analysis pipeline."""
    result = None
    if do_report:
        result = compute_statistics(df)
        print(result)
    if do_plot:
        plot_distributions(df)
        print("Plots saved under outputs/plots/")
    return result
