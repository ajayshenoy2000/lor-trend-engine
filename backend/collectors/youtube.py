from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
import isodate
import urllib.request
import json

from backend.config import settings
from backend.db.models import YouTubeVideo
from backend.processors.classify import classify_topic
from backend.sample_data import sample_youtube


YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"


def _recent_only(videos: list[YouTubeVideo], hours: int | None) -> list[YouTubeVideo]:
    if hours is None:
        return videos
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    return [video for video in videos if video.published_at >= cutoff]


def _youtube_get(path: str, params: dict[str, str | int | None]) -> dict:
    clean_params = {key: value for key, value in params.items() if value is not None}
    query = urlencode({**clean_params, "key": settings.youtube_api_key})
    url = f"{YOUTUBE_API_BASE}/{path}?{query}"
    with urllib.request.urlopen(url, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def _parse_youtube_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _parse_duration_seconds(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return float(isodate.parse_duration(value).total_seconds())
    except Exception:
        return None


def _videos_from_ids(video_ids: list[str]) -> list[YouTubeVideo]:
    videos: list[YouTubeVideo] = []
    for batch_start in range(0, len(video_ids), 50):
        batch = video_ids[batch_start : batch_start + 50]
        videos_payload = _youtube_get(
            "videos",
            {"part": "snippet,statistics,contentDetails", "id": ",".join(batch)},
        )
        for item in videos_payload.get("items", []):
            snippet = item.get("snippet", {})
            statistics = item.get("statistics", {})
            content_details = item.get("contentDetails", {})
            title = snippet.get("title", "")
            description = snippet.get("description", "")
            published_at = _parse_youtube_datetime(
                snippet.get("publishedAt", datetime.now(timezone.utc).isoformat())
            )
            videos.append(
                YouTubeVideo(
                    id=item.get("id", ""),
                    title=title,
                    description=description,
                    published_at=published_at,
                    views=int(statistics.get("viewCount", 0)),
                    likes=int(statistics.get("likeCount", 0)),
                    comments=int(statistics.get("commentCount", 0)),
                    avg_view_duration_seconds=_parse_duration_seconds(content_details.get("duration")),
                    category=classify_topic(f"{title} {description}"),
                )
            )
    return videos


def _search_keyword(keyword: str, order: str, published_after: str | None) -> list[str]:
    search_payload = _youtube_get(
        "search",
        {
            "part": "snippet",
            "q": keyword,
            "type": "video",
            "maxResults": 25,
            "order": order,
            "publishedAfter": published_after,
            "regionCode": "JP",
            "relevanceLanguage": "ja",
        },
    )
    return [
        item["id"]["videoId"]
        for item in search_payload.get("items", [])
        if "videoId" in item.get("id", {})
    ]


def collect_youtube_history(keywords: list[str] | None = None, hours: int | None = None) -> list[YouTubeVideo]:
    """Search public YouTube for videos related to the trend keywords.

    Combines a relevance-ordered search (broad topical coverage, no time
    restriction) with a viewCount-ordered search over a generous 90-day
    window (surfaces what's currently popular on the topic). The previous
    implementation only did viewCount + the (often very short) trend time
    window, which routinely returned zero results.
    """
    if not settings.youtube_api_key or not keywords:
        return _recent_only(sample_youtube, hours)

    published_after_90d = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat().replace("+00:00", "Z")

    video_ids: list[str] = []
    seen_ids: set[str] = set()

    for keyword in keywords[:8]:
        for order, published_after in (("relevance", None), ("viewCount", published_after_90d)):
            try:
                ids = _search_keyword(keyword, order, published_after)
            except Exception:
                continue
            for video_id in ids:
                if video_id not in seen_ids:
                    seen_ids.add(video_id)
                    video_ids.append(video_id)

    if not video_ids:
        return _recent_only(sample_youtube, hours)

    try:
        videos = _videos_from_ids(video_ids)
    except Exception:
        return _recent_only(sample_youtube, hours)

    videos.sort(key=lambda v: v.views, reverse=True)
    return videos
