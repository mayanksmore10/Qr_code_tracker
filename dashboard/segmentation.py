import pandas as pd
def place_frequency_segmentation(df: pd.DataFrame, place_col: str = "place") -> pd.DataFrame:

    if place_col not in df.columns:
        raise ValueError(f"'{place_col}' column not found in the data.")

    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    now = df["timestamp"].max()

    grouped = df.groupby(place_col).agg(
        last_visit=("timestamp", "max"),
        frequency=("timestamp", "count"),
    )
    grouped["recency_days"] = (now - grouped["last_visit"]).dt.days
    try:
        grouped["r_score"] = pd.qcut(grouped["recency_days"].rank(ascending=False, method="first"), 4, labels=[1, 2, 3, 4])
        grouped["f_score"] = pd.qcut(grouped["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4])
    except ValueError:
        grouped["r_score"] = pd.qcut(grouped["recency_days"].rank(ascending=False, method="first"), 2, labels=[1, 4])
        grouped["f_score"] = pd.qcut(grouped["frequency"].rank(method="first"), 2, labels=[1, 4])

    def label(row):
        r, f = int(row["r_score"]), int(row["f_score"])
        if r >= 3 and f >= 3:
            return "Hotspot (frequent & recent)"
        elif r >= 3 and f < 3:
            return "Emerging (recent, low volume)"
        elif r < 3 and f >= 3:
            return "Cooling off (was frequent)"
        else:
            return "Low activity"

    grouped["segment"] = grouped.apply(label, axis=1)
    return grouped.reset_index().sort_values("frequency", ascending=False)


def suburb_frequency(df: pd.DataFrame, suburb_col: str = "suburb") -> pd.DataFrame:

    grouped = df.groupby(suburb_col).agg(
        total_visits=("timestamp", "count"),
        first_visit=("timestamp", "min"),
        last_visit=("timestamp", "max"),
    ).sort_values("total_visits", ascending=False)

    return grouped.reset_index()


if __name__ == "__main__":
    from data_loader import load_visits

    df = load_visits()
    print(f"Loaded {len(df)} rows")

    print("\n--- Place Segmentation ---")
    print(place_frequency_segmentation(df))

    print("\n--- Suburb Frequency ---")
    print(suburb_frequency(df))