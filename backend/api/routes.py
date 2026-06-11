from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.api import service
from backend.config import DEFAULT_KEYWORDS, SCORING_WEIGHTS, settings

router = APIRouter(prefix="/api")


class BriefRequest(BaseModel):
    trendId: str


class SearchNowRequest(BaseModel):
    sources: list[str] = ["x", "google_news", "google_trends", "youtube"]
    timeWindow: str = "24h"
    analysisModelProvider: str = "gpt"
    briefModelProvider: str = "claude"


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/top-trends")
def top_trends() -> list[dict]:
    return [trend.as_dict() for trend in service.get_top_trends()]


@router.get("/record-this-week")
def record_this_week() -> list[dict]:
    return [trend.as_dict() for trend in service.get_record_this_week()]


@router.get("/video-opportunities")
def video_opportunities() -> list[dict]:
    return [trend.as_dict() for trend in service.get_video_opportunities()]


@router.get("/trends/{trend_id}")
def trend_detail(trend_id: str) -> dict:
    trend = service.get_trend(trend_id)
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    return trend.as_dict()


@router.get("/briefs")
def briefs() -> list[dict]:
    generated = (service.generate_brief_for_trend(trend.id) for trend in service.get_record_this_week())
    return [brief.as_dict() for brief in generated if brief]


@router.get("/briefs/{brief_id}")
def brief_detail(brief_id: str) -> dict:
    brief = service.get_brief(brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    return brief.as_dict()


@router.post("/generate-brief")
def generate_brief(payload: BriefRequest) -> dict:
    brief = service.generate_brief_for_trend(payload.trendId)
    if not brief:
        raise HTTPException(status_code=404, detail="Trend not found")
    return brief.as_dict()


@router.post("/search-now")
def search_now(payload: SearchNowRequest) -> dict:
    allowed_sources = {"x", "google_news", "google_trends", "youtube"}
    selected_sources = [source for source in payload.sources if source in allowed_sources]
    if not selected_sources:
        raise HTTPException(status_code=400, detail="At least one source must be enabled")
    if payload.timeWindow not in service.TIME_WINDOWS:
        raise HTTPException(status_code=400, detail="Unsupported time window")
    if payload.analysisModelProvider not in {"gpt", "claude"}:
        raise HTTPException(status_code=400, detail="Unsupported analysis model provider")
    if payload.briefModelProvider not in {"gpt", "claude"}:
        raise HTTPException(status_code=400, detail="Unsupported brief model provider")
    return service.run_on_demand_search(
        enabled_sources=selected_sources,
        time_window=payload.timeWindow,
        analysis_model_provider=payload.analysisModelProvider,
        brief_model_provider=payload.briefModelProvider,
    )


@router.post("/approve-topic/{trend_id}")
def approve_topic(trend_id: str) -> dict:
    trend = service.set_topic_status(trend_id, "approved")
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    return trend.as_dict()


@router.post("/reject-topic/{trend_id}")
def reject_topic(trend_id: str) -> dict:
    trend = service.set_topic_status(trend_id, "rejected")
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    return trend.as_dict()


@router.get("/sources")
def sources() -> list[dict]:
    return [
        {
            "id": source.id,
            "source": source.source,
            "title": source.title,
            "text": source.text,
            "url": source.url,
            "keyword": source.keyword,
            "publishedAt": source.published_at.isoformat(),
            "engagement": source.engagement,
            "metadata": source.metadata,
        }
        for source in service.get_sources()
    ]


@router.get("/settings")
def app_settings() -> dict:
    return {
        "keywords": service.get_keywords(),
        "scoringWeights": SCORING_WEIGHTS,
        "channelId": settings.youtube_channel_id or "",
        "modelProvider": settings.model_provider,
        "analysisModelProvider": settings.analysis_model_provider,
        "briefModelProvider": settings.brief_model_provider,
        "lastSearch": service.get_search_meta(),
        "apiKeys": {
            "youtube": bool(settings.youtube_api_key),
            "x": bool(settings.x_bearer_token),
            "anthropic": bool(settings.anthropic_api_key),
            "openai": bool(settings.openai_api_key),
        },
    }


class UpdateKeywordsRequest(BaseModel):
    keywords: list[str]


@router.post("/keywords")
def update_keywords(payload: UpdateKeywordsRequest) -> dict:
    if not payload.keywords or not all(isinstance(k, str) and k.strip() for k in payload.keywords):
        raise HTTPException(status_code=400, detail="Keywords must be non-empty strings")
    updated = service.set_keywords(payload.keywords)
    return {"keywords": updated}
