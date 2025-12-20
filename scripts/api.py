"""FastAPI service."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd  # delete if unused

from access import load_tracks
from analysis import analyze_tracks
from spoti import enrich_spotify


# =================================================================================================
app = FastAPI(title="TrackCraft API", version="0.1.0")


# Request / Response Models
class TrackRequest(BaseModel):
    path: str


# =================================================================================================
# Endpoints
@app.get("/")
def root():
    """Simple health check."""
    return {"status": "ok", "message": "TrackCraft API is running"}


@app.post("/analyze")
def analyze(request: TrackRequest):
    """
    Load, enrich, and analyze a track dataset.
    Expects a path to a track file or folder.
    """
    try:
        df = load_tracks(request.path)
        df = enrich_spotify(df)
        result = analyze_tracks(df)
        return {"summary": "success", "rows": len(df), "result": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}") from e


@app.get("/ping")
def ping():
    """Quick Spotify connectivity test."""
    try:
        _ = enrich_spotify(pd.DataFrame())
        return {"spotify": "connected"}
    except Exception as e:
        return {"spotify": f"failed ({e})"}
