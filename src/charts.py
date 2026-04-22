import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def build_weekly_distance_chart(df: pd.DataFrame):
    if df.empty or "date" not in df.columns or "distance_km" not in df.columns:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.text(0.5, 0.5, "No weekly distance data available", ha="center", va="center")
        ax.axis("off")
        return fig

    chart_df = df.copy()
    chart_df["date"] = pd.to_datetime(chart_df["date"])
    chart_df["week_start"] = chart_df["date"] - pd.to_timedelta(chart_df["date"].dt.weekday, unit="D")

    weekly = (
        chart_df.groupby("week_start", as_index=False)["distance_km"]
        .sum()
        .sort_values("week_start")
    )

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(weekly["week_start"], weekly["distance_km"], marker="o")
    ax.set_title("Weekly distance")
    ax.set_ylabel("Distance (km)")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig


def plot_training_balance(balance_df: pd.DataFrame):
    required_cols = {
        "Session type",
        "Current days",
        "Ideal days",
        "Current %",
        "Ideal %",
    }

    if balance_df.empty or not required_cols.issubset(balance_df.columns):
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, "No training balance data available", ha="center", va="center")
        ax.axis("off")
        return fig

    categories = balance_df["Session type"].tolist()
    current_pct = balance_df["Current %"].tolist()
    ideal_pct = balance_df["Ideal %"].tolist()
    current_days = balance_df["Current days"].tolist()
    ideal_days = balance_df["Ideal days"].tolist()

    x = np.arange(len(categories))
    width = 0.34

    fig, ax = plt.subplots(figsize=(11, 5.5))

    current_bars = ax.bar(x - width / 2, current_pct, width, label="Current %")
    ideal_bars = ax.bar(x + width / 2, ideal_pct, width, label="Ideal %")

    ax.set_title("Current vs ideal training mix", fontsize=16, pad=16)
    ax.set_ylabel("% of run days", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=25, ha="right")
    ax.legend()

    ymax = max(current_pct + ideal_pct) if (current_pct + ideal_pct) else 100
    ax.set_ylim(0, max(100, ymax + 10))

    for bar, days in zip(current_bars, current_days):
        height = bar.get_height()
        ax.annotate(
            f"{days}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    for bar, days in zip(ideal_bars, ideal_days):
        height = bar.get_height()
        ax.annotate(
            f"{days}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    fig.tight_layout()
    return fig


def plot_training_balance_with_counts(balance_df: pd.DataFrame):
    """
    Backward-compatible wrapper for older app.py imports.
    """
    return plot_training_balance(balance_df)