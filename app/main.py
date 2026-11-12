"""Community-event leaderboard. Demo app for the software-factory talk."""
from typing import Any, Callable, Coroutine

from fastapi import APIRouter, FastAPI, HTTPException, Request, Response
from fastapi.routing import APIRoute
from pydantic import BaseModel, Field

from app.store import STORE

app = FastAPI(title="Leaderboard")


class ScoreIn(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    points: int = Field(ge=0, le=1000)


@app.get("/health")
def health() -> dict:
    return {"ok": True}


class AuditRoute(APIRoute):
    """Records the raw body before parsing, so malformed bodies are kept too."""

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original = super().get_route_handler()

        async def handler(request: Request) -> Response:
            raw = await request.body()
            STORE.record_request(raw.decode("utf-8", errors="replace"))
            return await original(request)

        return handler


scores_router = APIRouter(route_class=AuditRoute)


@scores_router.post("/scores")
def add_score(score: ScoreIn) -> dict:
    STORE.add(score.name, score.points)
    return {"name": score.name, "total": STORE.total(score.name)}


app.include_router(scores_router)


@app.get("/leaderboard")
def leaderboard(limit: int = 10) -> list[dict]:
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=422, detail="limit must be 1-100")
    return STORE.top(limit)
