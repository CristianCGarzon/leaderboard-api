"""In-memory score store. All state lives here, per AGENTS.md."""
from collections import defaultdict, deque

AUDIT_MAX_ENTRIES = 1000
AUDIT_MAX_CHARS = 10_000


class Store:
    def __init__(self) -> None:
        self._scores: dict[str, int] = defaultdict(int)
        self._audit: deque[str] = deque(maxlen=AUDIT_MAX_ENTRIES)

    def record_request(self, raw: str) -> None:
        self._audit.append(raw[:AUDIT_MAX_CHARS])

    def audit_log(self) -> list[str]:
        return list(self._audit)

    def add(self, name: str, points: int) -> None:
        self._scores[name] += points

    def total(self, name: str) -> int:
        return self._scores.get(name, 0)  # reading must not create a 0-point player

    def top(self, limit: int) -> list[dict]:
        ranked = sorted(self._scores.items(), key=lambda kv: kv[1], reverse=True)
        return [{"name": n, "points": p} for n, p in ranked[:limit]]

    def reset(self) -> None:
        self._scores.clear()
        self._audit.clear()


STORE = Store()
