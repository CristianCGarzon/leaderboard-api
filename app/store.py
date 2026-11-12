"""In-memory score store. All state lives here, per AGENTS.md."""
from collections import defaultdict


class Store:
    def __init__(self) -> None:
        self._scores: dict[str, int] = defaultdict(int)

    def add(self, name: str, points: int) -> None:
        self._scores[name] += points

    def total(self, name: str) -> int:
        return self._scores.get(name, 0)  # reading must not create a 0-point player

    def top(self, limit: int) -> list[dict]:
        ranked = sorted(self._scores.items(), key=lambda kv: kv[1], reverse=True)
        return [{"name": n, "points": p} for n, p in ranked[:limit]]

    def stats(self) -> dict:
        players = len(self._scores)
        if players == 0:
            return {"players": 0, "average": 0.0}
        return {"players": players, "average": sum(self._scores.values()) / players}

    def reset(self) -> None:
        self._scores.clear()


STORE = Store()
