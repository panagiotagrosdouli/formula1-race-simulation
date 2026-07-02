from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict

import pandas as pd


@dataclass
class EloSystem:
    k: float = 16.0
    initial_rating: float = 1500.0
    ratings: Dict[str, float] = field(default_factory=dict)

    def get(self, name: str) -> float:
        return float(self.ratings.get(str(name), self.initial_rating))

    def expected_score(self, a: str, b: str) -> float:
        ra = self.get(a)
        rb = self.get(b)
        return 1.0 / (1.0 + 10.0 ** ((rb - ra) / 400.0))

    def update_pair(self, winner: str, loser: str) -> None:
        ew = self.expected_score(winner, loser)
        el = 1.0 - ew

        self.ratings[winner] = self.get(winner) + self.k * (1.0 - ew)
        self.ratings[loser] = self.get(loser) + self.k * (0.0 - el)

    def update_race(self, race_df: pd.DataFrame, entity_col: str, finish_col: str = "FinishPosition") -> None:
        clean = race_df[[entity_col, finish_col]].dropna().copy()
        clean[finish_col] = pd.to_numeric(clean[finish_col], errors="coerce")
        clean = clean.dropna(subset=[finish_col]).sort_values(finish_col)

        entities = clean[entity_col].astype(str).tolist()

        for i, j in combinations(range(len(entities)), 2):
            winner = entities[i]
            loser = entities[j]
            if winner != loser:
                self.update_pair(winner, loser)


def compute_pre_race_elo(
    df: pd.DataFrame,
    entity_col: str,
    round_col: str = "Round",
    finish_col: str = "FinishPosition",
    rating_col: str = "Elo",
    k: float = 16.0,
    initial_rating: float = 1500.0,
) -> pd.DataFrame:
    out = df.sort_values(round_col).copy()
    elo = EloSystem(k=k, initial_rating=initial_rating)
    out[rating_col] = float(initial_rating)

    for round_no in sorted(out[round_col].dropna().unique()):
        idx = out[out[round_col] == round_no].index
        out.loc[idx, rating_col] = out.loc[idx, entity_col].astype(str).map(elo.get).astype(float)

        race_df = out.loc[idx]
        if finish_col in race_df.columns and race_df[finish_col].notna().any():
            elo.update_race(race_df, entity_col=entity_col, finish_col=finish_col)

    return out.sort_index()
