# Copilot & AI Agent Guidance — TrackCraft

This file helps AI agents be productive in this repository. Keep suggestions short and exact: focus on code-level edits, tests, and PRs that align with the project patterns.

## Big picture (what this repo does)
- TrackCraft is a small, script-driven audio metadata extractor & enhancer.
- Key tasks: read audio files in `inputs/`, extract metadata with `tinytag`, enrich metadata via Spotify (spotipy), produce tabular outputs (Pandas DataFrames) and CSV files in `outputs/` (and occasionally to `~/Desktop`).
- The main modules are `trackcraft.py` (primary script) and `spotify.py` (overlapping/duplicate behaviors). Both are executed top-to-bottom rather than exported as functions or a CLI.

## Key files & responsibilities
- `trackcraft.py` — main end-to-end script
  - Scans `inputs/` (see `input_path`) for supported audio files.
  - Builds `df0` (raw metadata) and `df1` (cleaned + user-visible columns), `df2` (Spotify matches), `df3` (merged).
  - Uses `tinytag` to extract tags and `spotipy` to query Spotify API.
  - Writes CSVs; note it writes to `outputs/` for `df0` but saves other CSVs to `~/Desktop` — be careful when updating paths.
- `spotify.py` — alternate script; mirrors many of `trackcraft.py` sections (searching + feature fetch), useful for testing Spotify-specific flows.
- `pyproject.toml` — primary package metadata and dependency pins
- `trackcraft.yml` — conda environment used for development & reproducible builds
- `.pre-commit-config.yaml` — pre-commit checks & formatting rules; use these in PRs.

## Data flow & conventions to maintain
- DataFrames are named `df0`, `df1`, `df2`, `df3` (raw -> cleaned -> spotify-matched -> merged). Prefer using these same names when adding code to keep consistency.
- Columns of interest:
  - Core: `File`, `Title`, `Artist`, `Year`, `Duration`, `Genre`, `Type`, `BitRate`, `Size`.
  - Enhanced: `Key`, `BPM`, `Fame`, `Energy`, `Groove`, `Mood`, `Comment`.
  - Spotify side: `SpotifyID`, `Fame_sp`, `Year_sp`, `ISRC`.
- `extract_song(file, artist_tag, title_tag)` is a small helper to infer artist/title from filename; keep pattern of fallback and minimal disruption to existing behavior.
- `prefer_spotify(sp_col, base_col)` merges Spotify-sourced columns into the user-facing DF — preserve this pattern when enriching data.
- File detection uses SUPPORTED_EXT and `tinytag` for metadata; new audio formats should be added to `SUPPORTED_EXT` (in `trackcraft.py`) and included in `inputs/` if necessary.

## Environment & running
- Python 3.12 (or newer as stated in `pyproject.toml`) is required.
- Recommended setup using conda environment:

  ```bash
  conda env create -f trackcraft.yml -n trackcraft
  conda activate trackcraft
  python -m pip install -e .  # optional: installs the project as an editable package
  ```

- Spotify API credentials are mandatory for any Spotify enrichments:
  ```bash
  export SPOTIPY_CLIENT_ID=<id>
  export SPOTIPY_CLIENT_SECRET=<secret>
  ```
  The code uses `SpotifyClientCredentials`; avoid committing secrets to the repo (detection is already enabled via `.secrets.baseline`).
- Run the script for a quick check:
  ```bash
  python trackcraft.py
  ```
  - Ensure `inputs/` contains audio files. TrackCraft's `input_path` is hardcoded to `~/Git/TrackCraft/inputs/` — you might need to symlink or run from that folder.
  - The script writes CSV outputs to `outputs/` and `~/Desktop` (see `df1.to_csv` in `trackcraft.py`).

## Debugging & troubleshooting patterns
- `test_search` and `debug_audio_features` are included to verify Spotify connectivity; use them as smoke tests.
- The script clears `.spotipy_cache` at the start; this is intentional to avoid stale tokens but should be documented in PRs if changed.
- When adding or changing Spotify calls, maintain the `get_audio_features_batch` batching behavior (up to 100 IDs) and error handling pattern for `SpotifyException`.

## Project-specific conventions & patterns
- Scripts are concise and intentionally minimize print noise; preserve the pattern of focusing on functionality over verbose logging, but add informative debug prints when adding features.
- Prefers pandas-style transforms in-place and uses pandas integer NA compatible types (e.g. `Int64`), keep this for compatibility.
- Naming conventions: use `df0`/`df1`/`df2`/`df3` as the flow; column names are TitleCase and occasionally snake_case for helper variables — follow existing casing.
- Default paths are anchored to `~/Git/TrackCraft/`; prefer using repo-relative paths if you need to generalize.

## Suggested safe edits for AI agents
- Prefer minimal, local changes per PR. Example tasks:
  - Convert `project_path`/`input_path` to repo-relative path detection (using `Path(__file__).parent.resolve()`) and update tests/README accordingly.
  - Centralize CSV output paths to `output_path` to avoid inconsistent writes to `~/Desktop`.
  - Add a small CLI via `argparse` to override `input_path`, `output_path`, and `--no-spotify` options.
  - Move repeated Spotify code to a small helper module and remove duplication between `trackcraft.py` and `spotify.py`.

## Immediate checks to run when opening a PR
- Run `pre-commit` hooks or `git commit` locally. `pre-commit` is configured to run `ruff` and `black`.
- If you added new imports, ensure the whole `pyproject.toml` or `trackcraft.yml` contains the dependency. Use the `dev` or `audio` extras as appropriate.
- Verify `extract_song` edge cases by extending test cases (no test suite exists; adding minimal tests under `tests/` is okay).

## Good-first-issue ideas (for contributors)
- Add a CLI using `argparse`/`click` to set paths and flags.
- Add tests for `extract_song` and `seconds2mins` in a `tests/` folder using `pytest`.
- Unify Spotify logic into a single helper module with tests for `get_audio_features_batch`.
- Fix Desktop output to use `outputs/` consistently.

---

If anything is unclear or you need implementation suggestions for any of the tasks above (like a small refactor or test harness), say which part and I’ll provide a patch. :sparkles: