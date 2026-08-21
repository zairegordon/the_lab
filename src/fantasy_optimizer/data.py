import pandas as pd


def load_players_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Expect columns: id,name,position,team,cost,projected_points
    expected = {"id", "name", "position", "team", "cost", "projected_points"}
    if not expected.issubset(df.columns):
        raise ValueError(f"players CSV must include columns: {expected}")
    return df
