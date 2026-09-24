"""
generate_figures.py
-------------------
Regenerates every figure for the Netflix Movies & TV Shows Data Visualization project.

Usage (from repo root):
    py src/generate_figures.py

All PNGs are written to visuals/ at 300 dpi.

Dataset: Netflix Movies and TV Shows
Source : https://www.kaggle.com/datasets/shivamb/netflix-shows
File   : data/netflix_titles.csv
"""

import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend – safe for scripts
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats

warnings.filterwarnings("ignore")

# ──────────────────────────────────────────────────────────────────────────────
# PATHS
# ──────────────────────────────────────────────────────────────────────────────
ROOT        = Path(__file__).resolve().parent.parent
DATA_PATH   = ROOT / "data" / "netflix_titles.csv"
VISUALS_DIR = ROOT / "visuals"
VISUALS_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
# DESIGN SYSTEM  — Wong (2011) colorblind-safe palette
# ──────────────────────────────────────────────────────────────────────────────
PAL = {
    "blue":   "#0072B2",
    "orange": "#E69F00",
    "green":  "#009E73",
    "red":    "#D55E00",
    "purple": "#CC79A7",
    "sky":    "#56B4E9",
    "yellow": "#F0E442",
}
CB6 = [PAL["blue"], PAL["orange"], PAL["green"],
       PAL["red"],  PAL["purple"], PAL["sky"]]

sns.set_theme(style="whitegrid", font_scale=1.0)
plt.rcParams.update({
    "savefig.dpi":     300,
    "font.family":     "DejaVu Sans",
    "axes.titlesize":  13,
    "axes.labelsize":  11,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.titlesize": 15,
})

MONTH_ORDER = ["Jan","Feb","Mar","Apr","May","Jun",
               "Jul","Aug","Sep","Oct","Nov","Dec"]

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────
def save(fig, name: str):
    path = VISUALS_DIR / f"{name}.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved -> {path.relative_to(ROOT)}")


def explode_col(df: pd.DataFrame, col: str, new_col: str) -> pd.DataFrame:
    """Split a comma-separated column into one value per row."""
    return (
        df[[col]]
        .assign(**{col: df[col].str.split(",")})
        .explode(col)
        .rename(columns={col: new_col})
        .assign(**{new_col: lambda d: d[new_col].str.strip()})
        .loc[lambda d: d[new_col].ne("") & d[new_col].ne("Unknown")]
    )


# ──────────────────────────────────────────────────────────────────────────────
# 1. LOAD & CLEAN
# ──────────────────────────────────────────────────────────────────────────────
def load_and_clean(path: Path) -> pd.DataFrame:
    print("\n[1] Loading & cleaning …")
    df = pd.read_csv(path)
    print(f"    Raw shape: {df.shape}")

    # ── 1a. Duplicates: drop on show_id; also drop exact title+type duplicates
    before = len(df)
    df.drop_duplicates(subset="show_id", keep="first", inplace=True)
    df.drop_duplicates(subset=["title", "type"], keep="first", inplace=True)
    print(f"    Duplicates removed: {before - len(df)}")

    # ── 1b. Fix misplaced duration values in the rating column
    #        Three rows have '66 min','74 min','84 min' in rating — shift them
    bad_rating_mask = df["rating"].str.match(r"^\d+\s*min$", na=False)
    print(f"    Misplaced duration-in-rating rows: {bad_rating_mask.sum()}")
    df.loc[bad_rating_mask, "duration"] = df.loc[bad_rating_mask, "rating"]
    df.loc[bad_rating_mask, "rating"]   = np.nan

    # ── 1c. Missing values — explicit handling
    df["director"] = df["director"].fillna("Unknown")
    df["cast"]     = df["cast"].fillna("Unknown")
    df["country"]  = df["country"].fillna("Unknown")
    df["rating"]   = df["rating"].fillna("Unknown")
    # date_added: keep NaT after parse; we will drop NaT rows only when needed
    # duration: 3 NaN rows kept as NaN in derived numeric columns
    print(f"    Missing date_added after fill: {df['date_added'].isna().sum()} (kept as NaT)")

    # ── 1d. Parse date_added  (strip whitespace before parsing)
    df["date_added"]  = pd.to_datetime(df["date_added"].str.strip(), errors="coerce")
    df["year_added"]  = df["date_added"].dt.year.astype("Int64")
    df["month_added"] = df["date_added"].dt.month.astype("Int64")
    print(f"    date_added NaT count: {df['date_added'].isna().sum()}")

    # ── 1e. release_year numeric
    df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce")

    # ── 1f. Split duration into minutes (Movies) and seasons (TV Shows)
    movie_mask  = df["type"] == "Movie"
    show_mask   = df["type"] == "TV Show"
    df["duration_min"]     = np.nan
    df["duration_seasons"] = np.nan
    df.loc[movie_mask, "duration_min"] = (
        df.loc[movie_mask, "duration"]
        .str.extract(r"(\d+)")[0].astype(float)
    )
    df.loc[show_mask, "duration_seasons"] = (
        df.loc[show_mask, "duration"]
        .str.extract(r"(\d+)")[0].astype(float)
    )

    # ── 1g. Primary country and genre (first item — for per-row charts only)
    df["primary_country"] = df["country"].str.split(",").str[0].str.strip()
    df["primary_genre"]   = df["listed_in"].str.split(",").str[0].str.strip()

    print(f"    Clean shape: {df.shape}")
    return df


def compute_kpis(df: pd.DataFrame) -> dict:
    # Use exploded country/genre for accurate counts
    countries_exploded = explode_col(df[df["country"] != "Unknown"], "country", "c")
    genres_exploded    = explode_col(df, "listed_in", "g")

    kpis = dict(
        total           = len(df),
        n_movies        = int((df["type"] == "Movie").sum()),
        n_shows         = int((df["type"] == "TV Show").sum()),
        n_countries     = countries_exploded["c"].nunique(),
        n_genres        = genres_exploded["g"].nunique(),
        avg_movie_min   = round(df.loc[df["type"]=="Movie","duration_min"].mean(), 1),
        median_movie_min= round(df.loc[df["type"]=="Movie","duration_min"].median(), 0),
        top_country     = countries_exploded["c"].value_counts().idxmax(),
        top_genre       = genres_exploded["g"].value_counts().idxmax(),
        pct_movies      = round((df["type"]=="Movie").mean()*100, 1),
        pct_shows       = round((df["type"]=="TV Show").mean()*100, 1),
        pct_1season     = round((df.loc[df["type"]=="TV Show","duration_seasons"]==1).mean()*100, 1),
    )
    return kpis


# ──────────────────────────────────────────────────────────────────────────────
# CHART 01 — Content type split  (Bar)
# Q1: What is the split between Movies and TV Shows?
# ──────────────────────────────────────────────────────────────────────────────
def chart_01(df, kpis):
    counts = df["type"].value_counts()
    pcts   = counts / counts.sum() * 100

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(counts.index, counts.values,
                  color=[PAL["blue"], PAL["orange"]],
                  edgecolor="white", width=0.5)
    for bar, (lbl, pct) in zip(bars, pcts.items()):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 60,
                f"{int(bar.get_height()):,}\n({pct:.1f}%)",
                ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_title("Netflix Catalog: Movies vs TV Shows", fontweight="bold", pad=10)
    ax.set_xlabel("Content Type")
    ax.set_ylabel("Number of Titles")
    ax.set_ylim(0, counts.max() * 1.22)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
    sns.despine()
    fig.tight_layout()
    save(fig, "01_content_type_bar")


# ──────────────────────────────────────────────────────────────────────────────
# CHART 02 — Titles added per year  (Line)
# Q2: How has the library grown over time?
# ──────────────────────────────────────────────────────────────────────────────
def chart_02(df):
    yr = (df.dropna(subset=["year_added"])
           .groupby(["year_added","type"])
           .size().reset_index(name="n"))
    yr = yr[yr["year_added"].between(2008, 2021)]

    fig, ax = plt.subplots(figsize=(10, 5))
    for t, grp in yr.groupby("type"):
        col = PAL["blue"] if t == "Movie" else PAL["orange"]
        ax.plot(grp["year_added"], grp["n"], marker="o", color=col,
                label=t, linewidth=2.2, markersize=5)
        last = grp.iloc[-1]
        ax.annotate(f"{int(last['n'])}",
                    xy=(last["year_added"], last["n"]),
                    xytext=(4, 4), textcoords="offset points", fontsize=8)
    ax.set_title("Netflix Titles Added Per Year (by Type)", fontweight="bold", pad=10)
    ax.set_xlabel("Year Added to Netflix")
    ax.set_ylabel("Number of Titles Added")
    ax.legend(title="Type")
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    sns.despine()
    fig.tight_layout()
    save(fig, "02_titles_per_year_line")


# ──────────────────────────────────────────────────────────────────────────────
# CHART 03 — Release year vs Year added  (Scatter + Trendline)
# Q2: How quickly does Netflix add recently released content?
# ──────────────────────────────────────────────────────────────────────────────
def chart_03(df):
    sdf = df.dropna(subset=["release_year","year_added"]).copy()
    sdf = sdf[(sdf["release_year"] >= 1990) & (sdf["year_added"] >= 2008)]
    sdf["lag"] = sdf["year_added"] - sdf["release_year"]
    median_lag = sdf["lag"].median()

    sample = sdf.sample(min(2500, len(sdf)), random_state=42)
    cmap   = sample["type"].map({"Movie": PAL["blue"], "TV Show": PAL["orange"]})

    slope, intercept, r, *_ = stats.linregress(sdf["release_year"], sdf["year_added"])
    xr = np.linspace(sdf["release_year"].min(), sdf["release_year"].max(), 200)

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(sample["release_year"], sample["year_added"],
               c=cmap, alpha=0.3, s=14, linewidths=0)
    ax.plot(xr, slope * xr + intercept, color=PAL["red"], linewidth=2,
            label=f"Trend  r={r:.2f}")
    ax.plot([1990, 2022], [1990, 2022], color="grey", linewidth=1.2,
            linestyle="--", label="y = x  (same year)")
    ax.annotate(f"Median lag: {int(median_lag)} yr",
                xy=(2002, 2021), fontsize=10, color=PAL["red"], fontweight="bold")
    legend_handles = [mpatches.Patch(color=PAL["blue"], label="Movie"),
                      mpatches.Patch(color=PAL["orange"], label="TV Show")]
    h2, l2 = ax.get_legend_handles_labels()
    ax.legend(handles=h2 + legend_handles, fontsize=9)
    ax.set_title("Release Year vs Year Added to Netflix", fontweight="bold", pad=10)
    ax.set_xlabel("Original Release Year")
    ax.set_ylabel("Year Added to Netflix")
    sns.despine()
    fig.tight_layout()
    save(fig, "03_release_vs_added_scatter")


# ──────────────────────────────────────────────────────────────────────────────
# CHART 04 — Movie duration distribution  (Histogram)
# Q4: How long are Netflix movies?
# ──────────────────────────────────────────────────────────────────────────────
def chart_04(df):
    dur = df.loc[df["type"]=="Movie", "duration_min"].dropna()

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.hist(dur, bins=40, color=PAL["sky"], edgecolor="white",
            linewidth=0.5, alpha=0.9)
    ax.axvline(dur.median(), color=PAL["red"],    linewidth=2,
               linestyle="--", label=f"Median: {dur.median():.0f} min")
    ax.axvline(dur.mean(),   color=PAL["orange"], linewidth=2,
               linestyle="-.", label=f"Mean: {dur.mean():.1f} min")
    ax.set_title("Distribution of Netflix Movie Durations", fontweight="bold", pad=10)
    ax.set_xlabel("Duration (minutes)")
    ax.set_ylabel("Number of Movies")
    ax.legend()
    sns.despine()
    fig.tight_layout()
    save(fig, "04_movie_duration_hist")


# ──────────────────────────────────────────────────────────────────────────────
# CHART 05 — TV Show seasons distribution  (Bar)
# Q5: How many seasons do Netflix TV Shows run?
# ──────────────────────────────────────────────────────────────────────────────
def chart_05(df):
    seasons = (df.loc[df["type"]=="TV Show","duration_seasons"]
               .dropna().astype(int)
               .value_counts().sort_index())
    pct1 = seasons.get(1, 0) / seasons.sum() * 100

    capped = seasons[seasons.index <= 15].copy()
    if seasons.index.max() > 15:
        capped[16] = seasons[seasons.index > 15].sum()
    capped.index = [str(i) if i <= 15 else "16+" for i in capped.index]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(capped.index, capped.values, color=PAL["green"],
                  edgecolor="white", linewidth=0.7)
    for bar in bars:
        if bar.get_height() > 15:
            ax.text(bar.get_x()+bar.get_width()/2,
                    bar.get_height()+8,
                    f"{int(bar.get_height()):,}",
                    ha="center", fontsize=8)
    ax.set_title(f"Netflix TV Shows: Season Count  ({pct1:.0f}% have 1 season)",
                 fontweight="bold", pad=10)
    ax.set_xlabel("Number of Seasons")
    ax.set_ylabel("Number of TV Shows")
    sns.despine()
    fig.tight_layout()
    save(fig, "05_tv_seasons_bar")


# ──────────────────────────────────────────────────────────────────────────────
# CHART 06 — Top 10 countries  (Horizontal Bar)  — EXPLODED
# Q3: Which countries produce the most Netflix content?
# ──────────────────────────────────────────────────────────────────────────────
def chart_06(df):
    exploded = explode_col(df[df["country"] != "Unknown"], "country", "country")
    top10    = exploded["country"].value_counts().head(10).sort_values()

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(top10.index, top10.values, color=PAL["blue"], edgecolor="white")
    for bar in bars:
        ax.text(bar.get_width() + 12,
                bar.get_y() + bar.get_height()/2,
                f"{int(bar.get_width()):,}",
                va="center", fontsize=9)
    ax.set_title("Top 10 Countries by Netflix Titles (each country counted separately)",
                 fontweight="bold", pad=10)
    ax.set_xlabel("Number of Titles")
    ax.set_ylabel("Country")
    ax.set_xlim(0, top10.max() * 1.15)
    sns.despine()
    fig.tight_layout()
    save(fig, "06_top_countries_bar")


# ──────────────────────────────────────────────────────────────────────────────
# CHART 07 — Top 10 genres  (Horizontal Bar)  — EXPLODED
# Q3: Which genres dominate?
# ──────────────────────────────────────────────────────────────────────────────
def chart_07(df):
    exploded = explode_col(df, "listed_in", "genre")
    top10    = exploded["genre"].value_counts().head(10).sort_values()

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(top10.index, top10.values, color=PAL["purple"], edgecolor="white")
    for bar in bars:
        ax.text(bar.get_width() + 10,
                bar.get_y() + bar.get_height()/2,
                f"{int(bar.get_width()):,}",
                va="center", fontsize=9)
    ax.set_title("Top 10 Netflix Genres (titles can appear in multiple genres)",
                 fontweight="bold", pad=10)
    ax.set_xlabel("Number of Titles")
    ax.set_ylabel("Genre")
    ax.set_xlim(0, top10.max() * 1.15)
    sns.despine()
    fig.tight_layout()
    save(fig, "07_top_genres_bar")


# ──────────────────────────────────────────────────────────────────────────────
# CHART 08 — Rating breakdown  (Stacked Bar: Movies vs TV Shows)
# Q5: How does content maturity differ by type?
# ──────────────────────────────────────────────────────────────────────────────
def chart_08(df):
    known_ratings = ["G","PG","PG-13","R","NC-17","NR","UR",
                     "TV-Y","TV-Y7","TV-Y7-FV","TV-G","TV-PG","TV-14","TV-MA"]
    rdf = (df[df["rating"].isin(known_ratings)]
           .groupby(["rating","type"]).size()
           .unstack(fill_value=0)
           .reindex(columns=["Movie","TV Show"], fill_value=0))
    rdf["total"] = rdf.sum(axis=1)
    rdf = rdf.sort_values("total", ascending=False).drop(columns="total")

    x   = np.arange(len(rdf))
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.bar(x, rdf["Movie"],
           label="Movie",   color=PAL["blue"],   edgecolor="white")
    ax.bar(x, rdf.get("TV Show", 0), bottom=rdf["Movie"],
           label="TV Show", color=PAL["orange"], edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(rdf.index, rotation=30, ha="right")
    ax.set_title("Content Ratings: Movies vs TV Shows (Stacked)",
                 fontweight="bold", pad=10)
    ax.set_xlabel("Content Rating")
    ax.set_ylabel("Number of Titles")
    ax.legend()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v,_: f"{int(v):,}"))
    sns.despine()
    fig.tight_layout()
    save(fig, "08_rating_stacked_bar")


# ──────────────────────────────────────────────────────────────────────────────
# CHART 09 — Rating × Primary Genre heatmap
# Q3/Q5: Which genres carry which ratings?
# ──────────────────────────────────────────────────────────────────────────────
def chart_09(df):
    known_ratings = ["TV-MA","TV-14","TV-PG","TV-Y7","TV-Y","TV-G","R","PG-13","PG","G"]
    # top 10 genres (by primary_genre, single column — keeps heatmap readable)
    top_genres = df["primary_genre"].value_counts().head(10).index.tolist()
    hdf = (df[df["rating"].isin(known_ratings) & df["primary_genre"].isin(top_genres)]
           .groupby(["primary_genre","rating"])
           .size().unstack(fill_value=0)
           .reindex(columns=known_ratings, fill_value=0))
    # Normalise by row so colours show proportion within each genre
    hdf_norm = hdf.div(hdf.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(13, 6))
    sns.heatmap(hdf_norm, annot=hdf.values, fmt="d",
                cmap="Blues", linewidths=0.4, linecolor="white",
                annot_kws={"size": 8}, ax=ax,
                cbar_kws={"label": "% of genre titles"})
    ax.set_title("Rating × Genre Heatmap  (cell = count; colour = % within genre)",
                 fontweight="bold", pad=10)
    ax.set_xlabel("Content Rating")
    ax.set_ylabel("Primary Genre")
    ax.tick_params(axis="x", rotation=30)
    ax.tick_params(axis="y", rotation=0)
    fig.tight_layout()
    save(fig, "09_rating_genre_heatmap")


# ──────────────────────────────────────────────────────────────────────────────
# CHART 10 — Month × Year heatmap of additions
# Q2: Is there seasonality in when Netflix adds content?
# ──────────────────────────────────────────────────────────────────────────────
def chart_10(df):
    mdf = (df.dropna(subset=["year_added","month_added"])
            .copy())
    mdf = mdf[mdf["year_added"].between(2015, 2021)]
    mdf["month_name"] = mdf["month_added"].apply(lambda m: MONTH_ORDER[int(m)-1])
    pivot = (mdf.groupby(["year_added","month_name"])
               .size()
               .unstack(fill_value=0)
               .reindex(columns=MONTH_ORDER, fill_value=0))

    fig, ax = plt.subplots(figsize=(13, 5))
    sns.heatmap(pivot, annot=True, fmt="d", cmap="YlOrRd",
                linewidths=0.4, linecolor="white",
                annot_kws={"size": 9}, ax=ax,
                cbar_kws={"label": "Titles added"})
    ax.set_title("Monthly Netflix Additions by Year (2015–2021)",
                 fontweight="bold", pad=10)
    ax.set_xlabel("Month")
    ax.set_ylabel("Year")
    ax.tick_params(axis="y", rotation=0)
    fig.tight_layout()
    save(fig, "10_month_year_heatmap")


# ──────────────────────────────────────────────────────────────────────────────
# CHART 11 — Movie duration by rating  (Violin)
# Q4: Does content rating affect duration?
# ──────────────────────────────────────────────────────────────────────────────
def chart_11(df):
    sel_ratings = ["G","PG","PG-13","R","TV-Y","TV-Y7","TV-G","TV-PG","TV-14","TV-MA"]
    mvs = df[(df["type"]=="Movie") &
             df["rating"].isin(sel_ratings) &
             df["duration_min"].notna()].copy()
    order = (mvs.groupby("rating")["duration_min"]
               .median().sort_values().index.tolist())

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.violinplot(data=mvs, x="rating", y="duration_min",
                   order=order, palette="Blues", inner="quartile", ax=ax)
    ax.set_title("Movie Duration by Content Rating (Violin)",
                 fontweight="bold", pad=10)
    ax.set_xlabel("Content Rating")
    ax.set_ylabel("Duration (minutes)")
    ax.tick_params(axis="x", rotation=30)
    sns.despine()
    fig.tight_layout()
    save(fig, "11_duration_by_rating_violin")


# ──────────────────────────────────────────────────────────────────────────────
# CHART 12 — Year-over-year growth  (Dual-axis: bar + line)
# Q2: At what rate has the library grown?
# ──────────────────────────────────────────────────────────────────────────────
def chart_12(df):
    yt = (df.dropna(subset=["year_added"])
           .groupby("year_added").size()
           .reset_index(name="n"))
    yt = yt[yt["year_added"].between(2010, 2021)]
    yt["yoy"] = yt["n"].pct_change() * 100

    peak = yt.loc[yt["yoy"].idxmax()]

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()
    ax1.bar(yt["year_added"], yt["n"], color=PAL["sky"],
            alpha=0.7, label="Titles Added")
    ax2.plot(yt["year_added"], yt["yoy"], color=PAL["red"],
             marker="D", linewidth=2, label="YoY Growth %")
    ax2.axhline(0, color="grey", linewidth=0.8, linestyle="--")
    ax2.annotate(f"+{peak['yoy']:.0f}%",
                 xy=(peak["year_added"], peak["yoy"]),
                 xytext=(8, 4), textcoords="offset points",
                 fontsize=10, color=PAL["red"], fontweight="bold")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Titles Added", color=PAL["sky"])
    ax2.set_ylabel("YoY Growth (%)", color=PAL["red"])
    ax1.set_title("Netflix Annual Additions & YoY Growth Rate",
                  fontweight="bold", pad=10)
    l1, lb1 = ax1.get_legend_handles_labels()
    l2, lb2 = ax2.get_legend_handles_labels()
    ax1.legend(l1+l2, lb1+lb2, loc="upper left", fontsize=9)
    sns.despine(right=False)
    fig.tight_layout()
    save(fig, "12_yoy_growth_line")


# ──────────────────────────────────────────────────────────────────────────────
# DASHBOARD — multi-panel summary
# ──────────────────────────────────────────────────────────────────────────────
def chart_dashboard(df, kpis):
    print("\n[Dashboard] Building …")

    fig = plt.figure(figsize=(20, 15))
    fig.patch.set_facecolor("#f4f6f8")
    gs  = gridspec.GridSpec(4, 4, figure=fig,
                            hspace=0.60, wspace=0.45,
                            top=0.91, bottom=0.05,
                            left=0.06, right=0.97)

    # ── KPI tiles (row 0) ────────────────────────────────────────────────────
    kpi_items  = [
        ("Total Titles",   f"{kpis['total']:,}"),
        ("Movies",         f"{kpis['n_movies']:,}  ({kpis['pct_movies']}%)"),
        ("TV Shows",       f"{kpis['n_shows']:,}  ({kpis['pct_shows']}%)"),
        ("Countries",      f"{kpis['n_countries']:,}"),
    ]
    kpi_colors = [PAL["blue"], PAL["sky"], PAL["orange"], PAL["green"]]
    for i, (lbl, val) in enumerate(kpi_items):
        ax = fig.add_subplot(gs[0, i])
        ax.set_facecolor(kpi_colors[i])
        ax.text(0.5, 0.60, val,  ha="center", va="center",
                fontsize=16, fontweight="bold", color="white",
                transform=ax.transAxes)
        ax.text(0.5, 0.22, lbl,  ha="center", va="center",
                fontsize=10, color="white", transform=ax.transAxes)
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values(): sp.set_visible(False)

    # ── Panel A: type split bar ──────────────────────────────────────────────
    axA = fig.add_subplot(gs[1:3, 0:2])
    c2  = df["type"].value_counts()
    bars = axA.bar(c2.index, c2.values,
                   color=[PAL["blue"], PAL["orange"]],
                   edgecolor="white", width=0.5)
    for bar in bars:
        axA.text(bar.get_x()+bar.get_width()/2,
                 bar.get_height()+50,
                 f"{bar.get_height():,}",
                 ha="center", fontsize=9, fontweight="bold")
    axA.set_title("Movies vs TV Shows", fontweight="bold")
    axA.set_ylabel("Titles")
    axA.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"{int(x):,}"))
    sns.despine(ax=axA)

    # ── Panel B: titles per year line ────────────────────────────────────────
    axB = fig.add_subplot(gs[1:3, 2:4])
    yr  = (df.dropna(subset=["year_added"])
            .groupby(["year_added","type"]).size().reset_index(name="n"))
    yr  = yr[yr["year_added"].between(2010, 2021)]
    for t, grp in yr.groupby("type"):
        col = PAL["blue"] if t=="Movie" else PAL["orange"]
        axB.plot(grp["year_added"], grp["n"],
                 marker="o", label=t, color=col, linewidth=2, markersize=4)
    axB.set_title("Titles Added Per Year", fontweight="bold")
    axB.set_xlabel("Year"); axB.set_ylabel("Titles")
    axB.legend(fontsize=8)
    axB.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    sns.despine(ax=axB)

    # ── Panel C: top 8 countries (exploded) ──────────────────────────────────
    axC = fig.add_subplot(gs[3, 0:2])
    exc = explode_col(df[df["country"] != "Unknown"], "country", "c")
    top8 = exc["c"].value_counts().head(8).sort_values()
    axC.barh(top8.index, top8.values, color=PAL["blue"], edgecolor="white")
    axC.set_title("Top 8 Countries", fontweight="bold")
    axC.set_xlabel("Titles")
    sns.despine(ax=axC)

    # ── Panel D: top 6 genres pie (exploded) ─────────────────────────────────
    axD = fig.add_subplot(gs[3, 2])
    exg = explode_col(df, "listed_in", "g")
    top6g = exg["g"].value_counts().head(6)
    wedges, texts, autotexts = axD.pie(
        top6g.values, labels=None, autopct="%1.0f%%",
        colors=CB6, startangle=140, pctdistance=0.78,
        wedgeprops=dict(edgecolor="white", linewidth=1.2))
    for at in autotexts: at.set_fontsize(7)
    axD.legend(top6g.index, loc="lower left", fontsize=6,
               frameon=False, bbox_to_anchor=(-0.2, -0.1))
    axD.set_title("Top 6 Genres", fontweight="bold")

    # ── Panel E: top ratings bar ─────────────────────────────────────────────
    axE = fig.add_subplot(gs[3, 3])
    known_r = ["G","PG","PG-13","R","NC-17","NR","UR",
                "TV-Y","TV-Y7","TV-Y7-FV","TV-G","TV-PG","TV-14","TV-MA"]
    top_r = df[df["rating"].isin(known_r)]["rating"].value_counts().head(7)
    axE.barh(top_r.index[::-1], top_r.values[::-1],
             color=PAL["purple"], edgecolor="white")
    axE.set_title("Top Ratings", fontweight="bold")
    axE.set_xlabel("Titles")
    sns.despine(ax=axE)

    fig.suptitle("Netflix Content Library — Summary Dashboard",
                 fontsize=18, fontweight="bold", y=0.97)
    save(fig, "00_dashboard")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"\nDataset not found: {DATA_PATH}\n"
            "Download from https://www.kaggle.com/datasets/shivamb/netflix-shows\n"
            "and place the CSV at: data/netflix_titles.csv"
        )

    df   = load_and_clean(DATA_PATH)
    kpis = compute_kpis(df)

    print("\n--- KPIs ---")
    for k, v in kpis.items():
        print(f"   {k:<20s}: {v}")
    print("---")

    print("\n[Generating 12 charts + dashboard ...]")
    chart_01(df, kpis)
    chart_02(df)
    chart_03(df)
    chart_04(df)
    chart_05(df)
    chart_06(df)
    chart_07(df)
    chart_08(df)
    chart_09(df)
    chart_10(df)
    chart_11(df)
    chart_12(df)
    chart_dashboard(df, kpis)

    pngs = list(VISUALS_DIR.glob("*.png"))
    print(f"\nDone! {len(pngs)} figures saved to: visuals/")
    for p in sorted(pngs):
        print(f"   {p.name}")


if __name__ == "__main__":
    main()
