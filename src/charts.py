import matplotlib.pyplot as plt
import pandas as pd


def build_weekly_distance_chart(df: pd.DataFrame):
    """
    Expects a cleaned dataframe with:
    - date
    - distance_km
    Falls back to distance if needed.
    """
    chart_df = df.copy()
    chart_df["date"] = pd.to_datetime(chart_df["date"])

    distance_col = "distance_km" if "distance_km" in chart_df.columns else "distance"

    weekly = (
        chart_df.set_index("date")
        .resample("W")[distance_col]
        .sum()
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(8.5, 3.3), dpi=120)
    ax.plot(weekly["date"], weekly[distance_col], marker="o", linewidth=1.8, markersize=4.5)
    ax.set_title("Weekly distance", fontsize=10, pad=10)
    ax.set_xlabel("Week", fontsize=8, labelpad=4)
    ax.set_ylabel("Distance (km)", fontsize=8, labelpad=4)
    ax.tick_params(axis="x", labelsize=8, rotation=30)
    ax.tick_params(axis="y", labelsize=8)
    plt.tight_layout()

    return fig


def plot_training_balance_with_counts(balance_df: pd.DataFrame):
    """
    Expects a dataframe with these columns:
    - Session type
    - Current days
    - Ideal days
    - Current %
    - ideal_pct

    Produces grouped bars using percentages, with absolute run-day
    counts annotated above each bar.
    """
    chart_df = balance_df.copy()

    fig, ax = plt.subplots(figsize=(8.8, 3.8), dpi=120)

    labels = chart_df["Session type"].tolist()
    current_pct = chart_df["Current %"].tolist()
    ideal_pct = chart_df["ideal_pct"].tolist()
    current_days = chart_df["Current days"].tolist()
    ideal_days = chart_df["Ideal days"].tolist()

    x = list(range(len(labels)))
    width = 0.34

    current_bars = ax.bar(
        [i - width / 2 for i in x],
        current_pct,
        width=width,
        label="Current %",
    )

    ideal_bars = ax.bar(
        [i + width / 2 for i in x],
        ideal_pct,
        width=width,
        label="Ideal %",
    )

    for bar, days in zip(current_bars, current_days):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 1,
            f"{int(days)}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    for bar, days in zip(ideal_bars, ideal_days):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 1,
            f"{int(days)}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylabel("% of run days", fontsize=8)
    ax.set_title("Current vs ideal training mix", fontsize=10, pad=10)
    ax.tick_params(axis="x", labelsize=8)
    ax.tick_params(axis="y", labelsize=8)
    ax.legend(fontsize=8)

    plt.tight_layout()
    return fig