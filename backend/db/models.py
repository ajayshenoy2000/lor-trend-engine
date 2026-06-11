from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal


SourceType = Literal["x", "google_news", "google_trends", "youtube", "manual"]


@dataclass
class SourceItem:
    id: str
    source: SourceType
    title: str
    text: str
    url: str
    keyword: str
    published_at: datetime
    engagement: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class YouTubeVideo:
    id: str
    title: str
    description: str
    published_at: datetime
    views: int
    likes: int
    comments: int
    impressions: int | None = None
    ctr: float | None = None
    avg_view_duration_seconds: float | None = None
    avg_percentage_viewed: float | None = None
    subscribers_gained: int | None = None
    category: str = "美容医療全般"


@dataclass
class ScoreBreakdown:
    trend_momentum: float
    google_search_demand: float
    medical_relevance: float
    youtube_historical_fit: float
    conversion_potential: float
    safety_brand_fit: float

    @property
    def total(self) -> float:
        return round(
            self.trend_momentum
            + self.google_search_demand
            + self.medical_relevance
            + self.youtube_historical_fit
            + self.conversion_potential
            + self.safety_brand_fit,
            2,
        )

    def as_dict(self) -> dict[str, float]:
        return {
            "trendMomentum": round(self.trend_momentum, 2),
            "googleSearchDemand": round(self.google_search_demand, 2),
            "medicalRelevance": round(self.medical_relevance, 2),
            "youtubeHistoricalFit": round(self.youtube_historical_fit, 2),
            "conversionPotential": round(self.conversion_potential, 2),
            "safetyBrandFit": round(self.safety_brand_fit, 2),
            "total": self.total,
        }


@dataclass
class Trend:
    id: str
    title: str
    keyword: str
    summary: str
    cluster_terms: list[str]
    score: ScoreBreakdown
    sources: list[SourceItem]
    youtube_history: list[YouTubeVideo] = field(default_factory=list)
    status: Literal["new", "approved", "rejected"] = "new"
    why_it_matters: str = ""
    safety_notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "keyword": self.keyword,
            "summary": self.summary,
            "clusterTerms": self.cluster_terms,
            "score": self.score.as_dict(),
            "sources": [
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
                for source in self.sources
            ],
            "youtubeHistory": [
                {
                    "id": video.id,
                    "title": video.title,
                    "description": video.description,
                    "publishedAt": video.published_at.isoformat(),
                    "views": video.views,
                    "likes": video.likes,
                    "comments": video.comments,
                    "impressions": video.impressions,
                    "ctr": video.ctr,
                    "avgViewDurationSeconds": video.avg_view_duration_seconds,
                    "avgPercentageViewed": video.avg_percentage_viewed,
                    "subscribersGained": video.subscribers_gained,
                    "category": video.category,
                }
                for video in self.youtube_history
            ],
            "status": self.status,
            "whyItMatters": self.why_it_matters,
            "safetyNotes": self.safety_notes,
        }


@dataclass
class VideoBrief:
    id: str
    trend_id: str
    title_options: list[str]
    hook: str
    conclusion: str
    outline: list[str]
    talking_points: list[str]
    risks_to_mention: list[str]
    cta: str
    duration_minutes: str = "3-5"

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "trendId": self.trend_id,
            "titleOptions": self.title_options,
            "hook": self.hook,
            "conclusion": self.conclusion,
            "outline": self.outline,
            "talkingPoints": self.talking_points,
            "risksToMention": self.risks_to_mention,
            "cta": self.cta,
            "durationMinutes": self.duration_minutes,
        }
