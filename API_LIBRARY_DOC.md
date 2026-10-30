# API & Library Inventory — CodeAlpha_DataVisualization

> **Project:** Netflix Movies & TV Shows Data Visualization (CodeAlpha Internship — Task 3)
> **Scope:** Files under `CodeAlpha_DataVisualization/` (root: `C:\Users\nayak\Desktop\Intership Projects\CADATAViz3`)
> **Date of audit:** 2026-10-30
> **Sources scanned:** `requirements.txt`, `src/generate_figures.py`, `notebooks/netflix_visualization.ipynb`,
> `_fix_nb.py`, `.venv/pyvenv.cfg`, `data/netflix_titles.csv` (8,807 rows), `README.md`, `.git` history.

**Bottom line:** this is a **purely local, file-based analysis project**. It has **no external API integrations, no internal HTTP routes, and no environment-variable configuration**. All data is read from a local CSV, and all outputs are PNG files written to disk. Sections 2, 3 and 4 of this document are therefore empty — explainers are provided in each section rather than left blank.

---

## 1. Libraries

### 1.1 Declared direct dependencies (`requirements.txt`)

| # | Name | Exact version | Runtime / Dev | Purpose in this project | Files where used | Flag |
|---|------|---------------|---------------|------------------------|------------------|------|
| 1 | `pandas` | `>=2.0` **(min only — not pinned)** | Runtime | Load `netflix_titles.csv`; group/aggregate; `explode()` for multi-value columns (`country`, `listed_in`); datetime parsing; `value_counts()`; `pct_change()` | `src/generate_figures.py` (lines 21, 42–53, 129–194), `notebooks/netflix_visualization.ipynb` (cells 1, 3, 4, 6–13) | — |
| 2 | `numpy` | `>=1.24` | Runtime | `np.nan` sentinel arrays; `np.linspace()` for trendline x-axis; `np.arange()` for bar positions; `.astype(float)` conversions | `src/generate_figures.py` (lines 21, 57, 107, 223, 285), `notebooks/netflix_visualization.ipynb` (cells 1, 3, 5, 7) | — |
| 3 | `matplotlib` | `>=3.7` | Runtime | All chart rendering; `Agg` backend for headless script execution; `GridSpec` dashboard layout; `FuncFormatter` for comma-separated tick labels | `src/generate_figures.py` (lines 22–24, 34–43, 197–582), `notebooks/netflix_visualization.ipynb` (cells 1, 5–13) | — |
| 4 | `seaborn` | `>=0.13` | Runtime | `set_theme(style="whitegrid")`; `despine()`; `heatmap()` (charts 9, 10); `violinplot()` (chart 11) | `src/generate_figures.py` (lines 25, 34, 216, 330, 362, 425, 577, 609, 625, 658), `notebooks/netflix_visualization.ipynb` (cells 1, 5–13) | — |
| 5 | `scipy` | `>=1.11` | Runtime | `stats.linregress()` — OLS trendline on release-year vs year-added (chart 03) | `src/generate_figures.py` (lines 26, 239), `notebooks/netflix_visualization.ipynb` (cells 1, 7) | — |
| 6 | `jupyter` | `>=1.0` | Dev / runtime tooling | Interactive notebook execution in `notebooks/`; not imported by any source file | `README.md` ("How to Run" §3b), `submission_checklist.md` | Not imported by project code — CLI tooling only |
| 7 | `nbformat` | `>=5.7` | Dev / serialization | Notebook `.ipynb` read/write; required by `jupyter nbconvert --execute` | `submission_checklist.md`; consumed transitively by `jupyter` | Not imported by project code |
| 8 | `Pillow` | `>=9.0` | Runtime (image backend) | PNG rasterisation backend used by Matplotlib's `Agg` backend when `Figure.savefig()` writes `visuals/*.png` | `src/generate_figures.py` (`save()` helper, line 61); `notebooks/netflix_visualization.ipynb` (`save_fig`) | Never imported directly — pulled in by matplotlib; correctness of 300 dpi exports depends on it |

### 1.2 Transitive (indirect) dependencies

These are pulled in by the packages above but are **not declared** in `requirements.txt`. Versions could not be determined because the project venv has no packages installed (see §1.4).

| Name | Pulled in by | Purpose | Flag |
|------|-------------|---------|------|
| `contourpy` | matplotlib | Contour/quad-mesh rasterisation | Undeclared transitive |
| `cycler` | matplotlib | Style property cycling | Undeclared transitive |
| `fonttools` | matplotlib | Font loading (DejaVu Sans is the configured `font.family`) | Undeclared transitive |
| `kiwisolver` | matplotlib | Layout constraint solver | Undeclared transitive |
| `packaging` | matplotlib / setuptools | Version spec handling | Undeclared transitive |
| `pyparsing` | matplotlib | Parser for Matplotlib's math text / style strings | Undeclared transitive |
| `python-dateutil` | pandas | `pd.to_datetime()` parsing of `date_added` | Undeclared transitive |
| `pytz`, `tzdata` | pandas | Timezone support for datetime columns | Undeclared transitive |
| `ipykernel`, `ipython`, `jupyter-client`, `jupyter-core`, `nbconvert`, `notebook`, `traitlets` | jupyter | Notebook kernel + execution infrastructure | Undeclared transitive |

### 1.3 Standard-library modules used

| Module | Where | Purpose |
|--------|-------|---------|
| `pathlib.Path` | `src/generate_figures.py` (lines 17, 30–33, 61, 649), `notebooks/netflix_visualization.ipynb` (cell 1) | OS-independent path resolution (`Path(__file__).resolve().parent.parent`) and `mkdir(parents=True, exist_ok=True)` |
| `warnings` | `src/generate_figures.py` (line 18), `notebooks/netflix_visualization.ipynb` (cell 1) | `warnings.filterwarnings("ignore")` — suppresses Matplotlib/Seaborn deprecation and `SettingWithCopy`-adjacent warnings |
| `os` | `src/generate_figures.py` (line 16) | **Imported but never used.** No occurrence of `os.` anywhere in the codebase (verified by grep). Dead import. |

### 1.4 Version certainty — what could NOT be determined

- **No lockfile exists.** There is no `requirements.lock`, `pip freeze` output, `pyproject.toml`, or `Pipfile.lock` in the repository. `requirements.txt` uses only lower-bound specifiers (`>=`), so exact resolved versions are **not known** from the code.
- **The virtual environment is empty.** `.venv/Lib/site-packages/` exists but contains **zero installed packages** (verified by directory listing). The venv was created against `C:\Users\nayak\AppData\Local\Programs\Python\Python314` (Python 3.14.0) but `pip install -r requirements.txt` has **not** been run.
- **Consequence:** the "Exact version" column above reports the declared minimum only. Until dependencies are installed, the actual runtime versions of pandas, numpy, matplotlib, seaborn, scipy, and all transitive packages are unknown. This matters because `pandas>=2.0` on Python 3.14 would resolve to pandas 2.x, where `df.dtypes` returns `str` for object columns (as seen in the notebook output) — behaviour that differs from pandas 1.x.

**Evidence that a run was attempted (and failed).** `src/__pycache__/generate_figures.cpython-314.pyc` exists — a Python 3.14 bytecode cache for the script. Since the venv has no packages installed, `import numpy` would have raised `ModuleNotFoundError` on the first line, so the script was imported/compiled by the interpreter but could not have completed. The `__pycache__/` directory is correctly gitignored (`.gitignore` covers `__pycache__/` and `*.py[cod]`).

### 1.5 Unused / outdated / orphan items

| Item | Path | Issue |
|------|------|-------|
| Dead import | `src/generate_figures.py:16` | `import os` — never referenced. Safe to delete. |
| Empty orphan file | `bagarty.py` (repo root, outside `CodeAlpha_DataVisualization/`) | 0-byte file. Not referenced by anything. Likely a scratch/placeholder. |
| Out-of-tree shim | `_fix_nb.py` (repo root) | Adds missing `cell.id` UUIDs and bumps `nbformat_minor` to 5 on the notebook. Useful for cross-version compatibility, but it lives **outside** the deliverable package and is not mentioned in `README.md` or `submission_checklist.md`. |
| Stale KPI | `README.md` ("Dashboard" and "Key Insights" §1) | Claims **123 countries**. Both `compute_kpis()` in `src/generate_figures.py` and the notebook compute **122** unique exploded countries. Verified independently against `data/netflix_titles.csv` with a stdlib CSV scan: **122** distinct non-empty, non-`Unknown` country labels (top: United States 3,690; India 1,046; UK 806). The README figure is 1 high. |
| Misleading chart-type claim | `linkedin_content.md` POST 2 | Lists "box plot" among the 12 chart types. No chart uses a box plot — chart 11 is a `sns.violinplot()`. |
| Dataset not committed | `data/netflix_titles.csv` | Correctly excluded by `.gitignore` (this is intentional), so the script raises `FileNotFoundError` on a fresh clone. Documented in `README.md`. |

---

## 2. External APIs and SDKs

**None.** The project makes zero network calls.

Verification: a recursive grep across `**/*.py` for `requests|urllib|http\.|httpx|fetch|API_KEY|api_key|SECRET|TOKEN|os\.environ|getenv|\.env|API_BASE|base_url|status_code|retry|timeout|rate.?limit` returned **no matches**.

The only URLs in the codebase are **documentation links**, never executed:

| URL | Appears in | Role |
|-----|-----------|------|
| `https://www.kaggle.com/datasets/shivamb/netflix-shows` | `README.md` (lines 17, 88), `src/generate_figures.py:12`, `src/generate_figures.py:635` (runtime error message) | Manual dataset download instruction. The Kaggle dataset API is **not** used — the CSV must be placed at `data/netflix_titles.csv` by hand. |
| `https://www.kaggle.com/datasets/shivam Bansal` / `https://github.com/...` | `linkedin_content.md`, `git_commands.md` | Author attribution and repo setup guidance. |
| `https://github.com/nayaksuvamsuryakanta-a11y/CodeAlpha_DataVisualization.git` | `.git/config` (configured `origin` remote) | Git transport only; not part of the application. |

**Therefore:** no base URLs, endpoints, HTTP methods, auth schemes, headers, sample requests/responses, retry logic, or rate limits exist for this project. Nothing in sections 2's requested fields is applicable.

### 2.1 The de-facto data "interface" (local CSV)

Since the only external input is a static file, the closest analogue to an API is the dataset contract:

- **Source:** Kaggle dataset `shivamb/netflix-shows` (CC0 / public domain, per `README.md`).
- **Format:** UTF-8 CSV, comma-delimited, CRLF/lf line endings.
- **Schema** (12 columns, confirmed from `data/netflix_titles.csv` header and notebook cell 3 output):

| Column | Type (as read) | Notes |
|--------|---------------|-------|
| `show_id` | `str` | Unique primary key; 0 duplicates found |
| `type` | `str` | `Movie` / `TV Show` |
| `title` | `str` | — |
| `director` | `str` | 2,634 missing → filled `"Unknown"` |
| `cast` | `str` | 825 missing → filled `"Unknown"` |
| `country` | `str` | Comma-separated; 831 missing → `"Unknown"`; **122 distinct values** when exploded |
| `date_added` | `str` → parsed to `datetime` | 10 missing → kept `NaT` |
| `release_year` | `int64` | — |
| `rating` | `str` | 4 missing → `"Unknown"`; **3 rows contain misplaced duration values** (`66 min`, `74 min`, `84 min`) that the code relocates to `duration` |
| `duration` | `str` | e.g. `90 min`, `2 Seasons` |
| `listed_in` | `str` | Comma-separated genre list; 42 distinct values when exploded |
| `description` | `str` | Not used in any chart |

- **Row count:** 8,807 data rows (8,810 lines incl. header).
- **Derived columns created by the code** (not present in the source): `year_added`, `month_added`, `duration_min`, `duration_seasons`, `primary_genre`, `primary_country`, `lag`.
- **No auth, no rate limit, no pagination** — it is a single local file read once.

---

## 3. Internal APIs

**None.** The project exposes no HTTP routes, no web server, and no network-accessible endpoints. It consists of:

- A CLI script (`src/generate_figures.py`) that runs once and exits.
- A Jupyter notebook (`notebooks/netflix_visualization.ipynb`) executed cell-by-cell in a local kernel.

**Closest analogue — internal function API (Python call graph).** Since there is no HTTP layer, the project's internal surface is the set of pure functions in `src/generate_figures.py`. This is provided in place of section 3's route table:

| Function | Signature | Returns | Called by | Key behaviour / "response" shape |
|----------|-----------|---------|-----------|----------------------------------|
| `load_and_clean` | `(path: Path) -> pd.DataFrame` | `DataFrame` (8,807 × 18 after cleaning) | `main()` | Reads CSV; drops duplicate `show_id` then duplicate `title`+`type`; relocates misplaced duration strings; fills NaNs; parses dates; splits `duration`; adds derived columns. |
| `compute_kpis` | `(df: pd.DataFrame) -> dict` | `dict` of 11 metrics | `main()` | Keys: `total`, `n_movies`, `n_shows`, `n_countries`, `n_genres`, `avg_movie_min`, `median_movie_min`, `top_country`, `top_genre`, `pct_movies`, `pct_shows`, `pct_1season`. |
| `explode_col` | `(df, col, new_col) -> pd.DataFrame` | `DataFrame` | `compute_kpis()`, `chart_06/07/09`, `chart_dashboard` | Splits a comma-separated column into one row per value, strips whitespace, drops empty and `Unknown` entries. |
| `save` | `(fig, name) -> None` | `None` (side effect: writes PNG) | Every `chart_*` | Writes `visuals/<name>.png` at 300 dpi with `bbox_inches="tight"`, then `plt.close(fig)`. |
| `chart_01` … `chart_12` | `(df, [kpis]) -> None` | `None` | `main()` | Each builds one `matplotlib.figure.Figure` and calls `save()`. |
| `chart_dashboard` | `(df, kpis) -> None` | `None` | `main()` | 4×4 `GridSpec` layout: 4 KPI tiles + panels A–E; writes `visuals/00_dashboard.png`. |
| `main` | `() -> None` | `None` | `__main__` guard | Orchestrates load → KPIs → 13 figures; raises `FileNotFoundError` if `data/netflix_titles.csv` is absent. |

**No status codes, no auth, no request/response schemas in the HTTP sense.** All functions run in-process with no permission surface.

---

## 4. Environment variables

**None required or consumed.**

Verification: grep for `os\.environ|getenv|\.env|SECRET|TOKEN|API_KEY` across all `.py`, `.md`, `.txt`, `.json`, `.yml`, `.yaml`, `.cfg` files in `CodeAlpha_DataVisualization/` returned **no matches** (the only `os.` match was the unused import noted in §1.3).

- **Path resolution is fully path-based, not env-based:** `ROOT = Path(__file__).resolve().parent.parent`, so `DATA_PATH = ROOT / "data" / "netflix_titles.csv"` resolves relative to the script's own location. No variable overrides it.
- **No configuration file** (`.env`, `.qwen/config`, `settings.json` override, or similar) exists in the project.
- **The only runtime parameter is a filesystem requirement:** `data/netflix_titles.csv` must exist, otherwise `main()` raises `FileNotFoundError` with a message pointing to the Kaggle URL.

### 4.1 Non-variable inputs that act like configuration

| "Setting" | Value | Source | Required? |
|-----------|-------|--------|-----------|
| Dataset path | `data/netflix_titles.csv` (relative to repo root) | `src/generate_figures.py:31` | Yes — hard crash if absent |
| Output directory | `visuals/` | `src/generate_figures.py:32` | No — auto-created via `mkdir(parents=True, exist_ok=True)` |
| Export DPI | 300 | `src/generate_figures.py:36` (`savefig.dpi` rcParam) and `save()` | No — baked in |
| Matplotlib backend | `Agg` | `src/generate_figures.py:22` | No — set explicitly for headless safety |
| Random seed | `42` | `src/generate_figures.py:231` (`sample(random_state=42)`) | No — makes the scatter sub-sample reproducible |
| Color palette | Wong (2011) 7-colour set, hex-defined in `PAL` | `src/generate_figures.py:38–44` | No — baked in |
| Chart figure sizes / font sizes | `plt.rcParams` block | `src/generate_figures.py:35–43` | No — baked in |

---

## Summary of what could not be determined

| Item | Why undetermined |
|------|------------------|
| **Exact installed versions of all 8 declared packages** | `.venv/Lib/site-packages/` is empty; no lockfile exists. Only the `>=` lower bounds from `requirements.txt` are knowable. |
| **Transitive dependency versions** | Same reason — nothing is installed, so `pip freeze` has no output to read. |
| **The `r` value of the chart-03 trendline** | The notebook's insight text claims "r ≈ 0.80+" but the actual coefficient is only rendered into the chart legend at runtime. Cannot be verified without executing the script. |
| **Whether `src/generate_figures.py` and the notebook run error-free end-to-end** | Dependencies are not installed, so neither entry point could be executed for verification. |
| **Why `README.md` says 123 countries while the code computes 122** | The independent CSV scan confirms **122**, so the README is the incorrect side — but the origin of the `123` figure (e.g. a pre-fix count, or `df['country'].nunique()` on unexploded data = 748) is not recorded anywhere in the code or commit history. |
| **Whether `data/netflix_titles.csv` is the exact Kaggle version assumed by the analysis** | The file is gitignored, so its provenance and row count (8,807) cannot be verified from the repository alone — only from the local copy present at audit time. |
| **Contents of `bagarty.py`** | The file is empty (0 bytes); its intent is not documented. |