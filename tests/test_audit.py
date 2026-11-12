from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.store import STORE

client = TestClient(app)
HEADERS = {"content-type": "application/json"}


def setup_function() -> None:
    STORE.reset()


def post(body: str):
    return client.post("/scores", content=body, headers=HEADERS)


def test_valid_post_records_exact_body() -> None:
    body = '{"name":  "ana", "points":5}'
    r = post(body)
    assert r.json() == {"name": "ana", "total": 5}
    assert STORE.audit_log() == [body]


def test_two_posts_in_order() -> None:
    a = '{"name": "a", "points": 1}'
    b = '{"name":"b","points":2}'
    post(a)
    post(b)
    assert STORE.audit_log() == [a, b]


def test_invalid_posts_are_recorded() -> None:
    bad = '{"name": "ana", "points": -1}'
    assert post(bad).status_code == 422
    assert post("{not json").status_code == 422
    assert STORE.audit_log() == [bad, "{not json"]


def test_long_body_truncated() -> None:
    post("x" * 10_500)
    assert STORE.audit_log() == ["x" * 10_000]


def test_log_bounded_to_newest_1000() -> None:
    for i in range(1005):
        STORE.record_request(str(i))
    log = STORE.audit_log()
    assert len(log) == 1000
    assert log[0] == "5"
    assert log[-1] == "1004"


def test_reset_clears_audit() -> None:
    post('{"name": "a", "points": 1}')
    STORE.reset()
    assert STORE.audit_log() == []


def test_gets_add_no_entries() -> None:
    client.get("/health")
    client.get("/leaderboard")
    assert STORE.audit_log() == []


def test_no_log_file_created() -> None:
    post('{"name": "a", "points": 1}')
    assert not Path("logs/requests.log").exists()
