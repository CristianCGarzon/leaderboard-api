from fastapi.testclient import TestClient

from app.main import app
from app.store import STORE

client = TestClient(app)


def setup_function() -> None:
    STORE.reset()


def test_health() -> None:
    assert client.get("/health").json() == {"ok": True}


def test_add_score_accumulates() -> None:
    client.post("/scores", json={"name": "ana", "points": 10})
    r = client.post("/scores", json={"name": "ana", "points": 5})
    assert r.json() == {"name": "ana", "total": 15}


def test_leaderboard_sorted() -> None:
    client.post("/scores", json={"name": "ana", "points": 10})
    client.post("/scores", json={"name": "leo", "points": 30})
    top = client.get("/leaderboard").json()
    assert top[0] == {"name": "leo", "points": 30}


def test_reading_a_total_does_not_add_a_player() -> None:
    assert STORE.total("ghost") == 0
    assert client.get("/leaderboard").json() == []


def test_rejects_bad_input() -> None:
    assert client.post("/scores", json={"name": "", "points": 10}).status_code == 422
    assert client.get("/leaderboard?limit=0").status_code == 422


def test_delete_existing_returns_204() -> None:
    client.post("/scores", json={"name": "ana", "points": 10})
    r = client.delete("/scores/ana")
    assert r.status_code == 204
    assert r.content == b""


def test_delete_removes_from_leaderboard() -> None:
    client.post("/scores", json={"name": "ana", "points": 10})
    client.post("/scores", json={"name": "leo", "points": 30})
    client.delete("/scores/ana")
    assert client.get("/leaderboard").json() == [{"name": "leo", "points": 30}]


def test_delete_unknown_returns_404() -> None:
    assert client.delete("/scores/ghost").status_code == 404


def test_delete_twice_returns_404() -> None:
    client.post("/scores", json={"name": "ana", "points": 10})
    client.delete("/scores/ana")
    assert client.delete("/scores/ana").status_code == 404


def test_delete_zero_point_player() -> None:
    client.post("/scores", json={"name": "ana", "points": 0})
    assert client.delete("/scores/ana").status_code == 204


def test_delete_rejects_too_long_name() -> None:
    assert client.delete("/scores/" + "a" * 41).status_code == 422


def test_delete_does_not_affect_others() -> None:
    client.post("/scores", json={"name": "ana", "points": 10})
    client.post("/scores", json={"name": "leo", "points": 30})
    client.delete("/scores/ana")
    assert STORE.total("leo") == 30


def test_readd_after_delete_starts_from_zero() -> None:
    client.post("/scores", json={"name": "ana", "points": 10})
    client.delete("/scores/ana")
    r = client.post("/scores", json={"name": "ana", "points": 4})
    assert r.json() == {"name": "ana", "total": 4}
