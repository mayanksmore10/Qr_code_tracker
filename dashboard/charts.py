import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set_theme(style="whitegrid")


def visits_over_time(df: pd.DataFrame) -> plt.Figure:
    daily = df.groupby("date").size().reset_index(name="visits")

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=daily, x="date", y="visits", marker="o", ax=ax)
    ax.set_title("Total Visits Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Visits")
    fig.autofmt_xdate(rotation=45)
    fig.tight_layout()
    return fig


def top_places(df: pd.DataFrame, place_col: str = "suburb", top_n: int = 10) -> plt.Figure:
    counts = df[place_col].value_counts().head(top_n).sort_values()

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=counts.values, y=counts.index, ax=ax, orient="h", palette="viridis")
    ax.set_title(f"Top {top_n} Places by Visit Count")
    ax.set_xlabel("Visits")
    ax.set_ylabel(place_col.capitalize())
    fig.tight_layout()
    return fig


def device_distribution(df: pd.DataFrame) -> plt.Figure:
    counts = df["device_type"].value_counts()

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=sns.color_palette("pastel"),
    )
    ax.set_title("Device Type Distribution")
    ax.axis("equal")
    fig.tight_layout()
    return fig

def date_hour_heatmap(df: pd.DataFrame) -> plt.Figure:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.hour

    pivot = df.pivot_table(
        index="date", columns="hour", values=df.columns[0], aggfunc="count", fill_value=0
    )

    fig, ax = plt.subplots(figsize=(12, max(4, len(pivot) * 0.3)))
    sns.heatmap(pivot, cmap="YlOrRd", annot=True, fmt="d", ax=ax, linewidths=0.5)
    ax.set_title("Visit Activity: Date x Hour")
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Date")
    fig.tight_layout()
    return fig

if __name__ == "__main__":
    from data_loader import load_visits

    df = load_visits()
    print(f"Loaded {len(df)} rows from database")

    visits_over_time(df)
    top_places(df)
    device_distribution(df)
    date_hour_heatmap(df)

    plt.show()

