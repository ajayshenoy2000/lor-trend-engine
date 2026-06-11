from __future__ import annotations

from typing import Any

from backend.collectors.google_news import collect_google_news
from backend.collectors.google_trends import collect_google_trends
from backend.collectors.x import collect_x_posts
from backend.collectors.youtube import collect_youtube_history
from backend.config import DEFAULT_KEYWORDS, settings

_user_keywords: list[str] | None = None
from backend.db.models import Trend, VideoBrief
from backend.llm.analysis import enrich_trends_with_analysis
from backend.llm.brief_generator import generate_riki_style_brief
from backend.processors.cluster import cluster_by_keyword
from backend.processors.safety_filter import rejection_reasons
from backend.processors.score import score_trend
from backend.sample_data import sample_briefs, sample_trends


TIME_WINDOWS = {
    "12h": 12,
    "24h": 24,
    "3d": 72,
    "7d": 168,
    "30d": 720,
}
DEFAULT_SOURCES = ["x", "google_news", "google_trends", "youtube"]

_trend_status: dict[str, str] = {}
_briefs: dict[str, VideoBrief] = {brief.id: brief for brief in sample_briefs}
_last_trends: list[Trend] | None = None
_last_sources = [source for trend in sample_trends for source in trend.sources]
_last_search_meta: dict[str, Any] = {
    "mode": "sample",
    "timeWindow": "sample",
    "sources": DEFAULT_SOURCES,
    "analysisModelProvider": settings.analysis_model_provider,
    "briefModelProvider": settings.brief_model_provider,
    "hours": None,
}


def _hours_for_window(time_window: str) -> int:
    return TIME_WINDOWS.get(time_window, 24)


def collect_and_rank_trends(
    use_live_sources: bool = False,
    enabled_sources: list[str] | None = None,
    time_window: str = "24h",
    analysis_model_provider: str | None = None,
    brief_model_provider: str | None = None,
) -> list[Trend]:
    global _last_sources, _last_search_meta
    sources_to_use = enabled_sources or DEFAULT_SOURCES
    analysis_model = analysis_model_provider or settings.analysis_model_provider
    brief_model = brief_model_provider or settings.brief_model_provider
    hours = _hours_for_window(time_window)
    keywords_to_use = _user_keywords or DEFAULT_KEYWORDS

    if not use_live_sources:
        trends = sample_trends
        _last_sources = [source for trend in trends for source in trend.sources]
    else:
        items = []
        if "x" in sources_to_use:
            items.extend(collect_x_posts(keywords_to_use, hours=hours))
        if "google_news" in sources_to_use:
            items.extend(collect_google_news(keywords_to_use, hours=hours))
        if "google_trends" in sources_to_use:
            items.extend(collect_google_trends(keywords_to_use, hours=hours))

        youtube_history = collect_youtube_history(keywords=keywords_to_use, hours=hours) if "youtube" in sources_to_use else []
        _last_sources = items
        trends = []
        for keyword, sources in cluster_by_keyword(items).items():
            text = " ".join(source.title + " " + source.text for source in sources)
            reasons = rejection_reasons(text)
            if reasons:
                continue
            score = score_trend(keyword, sources, youtube_history)
            trends.append(
                Trend(
                    id=keyword.lower().replace(" ", "-"),
                    title=f"SNSで話題の{keyword}、実際どうなの？",
                    keyword=keyword,
                    summary=f"直近{time_window}の{keyword}に関する投稿・ニュース・検索シグナルがまとまって伸びています。",
                    cluster_terms=sorted({source.keyword for source in sources}),
                    score=score,
                    sources=sources,
                    youtube_history=youtube_history,
                    why_it_matters="医師が不安、誤解、リスクを整理する価値があるテーマです。",
                    safety_notes=["断定的な効能表現を避ける", "適応と個人差を明確に伝える"],
                )
            )

    _last_search_meta = {
        "mode": "live" if use_live_sources else "sample",
        "timeWindow": time_window,
        "sources": sources_to_use,
        "analysisModelProvider": analysis_model,
        "briefModelProvider": brief_model,
        "hours": hours if use_live_sources else None,
    }
    for trend in trends:
        trend.status = _trend_status.get(trend.id, trend.status)  # type: ignore[assignment]
    ranked = sorted(trends, key=lambda trend: trend.score.total, reverse=True)
    if use_live_sources:
        # Analysis model rewrites summary / why_it_matters for the top trends;
        # the template text above is kept when the provider is mock/unavailable.
        enrich_trends_with_analysis(ranked, analysis_model)
    return ranked


def run_on_demand_search(
    enabled_sources: list[str],
    time_window: str,
    analysis_model_provider: str,
    brief_model_provider: str,
) -> dict[str, Any]:
    global _last_trends
    _last_trends = collect_and_rank_trends(
        use_live_sources=True,
        enabled_sources=enabled_sources,
        time_window=time_window,
        analysis_model_provider=analysis_model_provider,
        brief_model_provider=brief_model_provider,
    )
    return {
        "trends": [trend.as_dict() for trend in _last_trends],
        "recordThisWeek": [trend.as_dict() for trend in get_record_this_week()],
        "meta": _last_search_meta,
    }


def get_top_trends(limit: int = 20) -> list[Trend]:
    trends = _last_trends if _last_trends is not None else collect_and_rank_trends()
    return trends[:limit]


def get_record_this_week(limit: int = 5) -> list[Trend]:
    return [
        trend
        for trend in get_top_trends()
        if trend.score.medical_relevance >= 14 and trend.score.safety_brand_fit >= 3
    ][:limit]


def get_video_opportunities(limit: int = 10) -> list[Trend]:
    return [
        trend
        for trend in get_top_trends()
        if trend.score.youtube_historical_fit >= 10 or trend.score.conversion_potential >= 5
    ][:limit]


def get_trend(trend_id: str) -> Trend | None:
    return next((trend for trend in get_top_trends() if trend.id == trend_id), None)


def get_brief(brief_id: str) -> VideoBrief | None:
    if brief_id in _briefs:
        return _briefs[brief_id]
    trend_id = brief_id.removeprefix("brief-")
    trend = get_trend(trend_id)
    if not trend:
        return None
    brief = generate_riki_style_brief(trend, provider=_brief_provider())
    _briefs[brief.id] = brief
    return brief


def generate_brief_for_trend(trend_id: str) -> VideoBrief | None:
    cached = _briefs.get(f"brief-{trend_id}")
    if cached:
        return cached
    trend = get_trend(trend_id)
    if not trend:
        return None
    brief = generate_riki_style_brief(trend, provider=_brief_provider())
    _briefs[brief.id] = brief
    return brief


def _brief_provider() -> str:
    return str(_last_search_meta.get("briefModelProvider") or settings.brief_model_provider)


def get_sources() -> list:
    return _last_sources


def get_search_meta() -> dict[str, Any]:
    return _last_search_meta


def set_topic_status(trend_id: str, status: str) -> Trend | None:
    trend = get_trend(trend_id)
    if not trend:
        return None
    _trend_status[trend_id] = status
    trend.status = status  # type: ignore[assignment]
    return trend


def get_keywords() -> list[str]:
    return _user_keywords or DEFAULT_KEYWORDS


def set_keywords(keywords: list[str]) -> list[str]:
    global _user_keywords
    _user_keywords = keywords if keywords else None
    return get_keywords()
