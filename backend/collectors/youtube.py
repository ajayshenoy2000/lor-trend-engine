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


def _youtube_get(path: str, params: dict[str, str | int]) -> dict:
    query = urlencode({**params, "key": settings.youtube_api_key})
    url = f"{YOUTUBE_API_BASE}/{path}?{query}"
    with urllib.request.urlopen(url, timeout=10) as response:
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


def collect_youtube_history(keywords: list[str] | None = None, hours: int | None = None) -> list[YouTubeVideo]:
    """Search YouTube for videos matching keywords, sorted by view count."""
    if not settings.youtube_api_key or not keywords:
        return _recent_only(sample_youtube, hours)

    try:
        videos: list[YouTubeVideo] = []
        published_after = None
        if hours:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            published_after = cutoff.isoformat().replace("+00:00", "Z")

        for keyword in keywords[:5]:  # Limit to 5 keywords to avoid rate limits
            search_payload = _youtube_get(
                "search",
                {
                    "part": "snippet",
                    "q": keyword,
                    "type": "video",
                    "maxResults": 10,
                    "order": "viewCount",
                    "publishedAfter": published_after,
                    "regionCode": "JP",
                    "relevanceLanguage": "ja",
                },
            )

            video_ids = [item["id"]["videoId"] for item in search_payload.get("items", [])]
            if not video_ids:
                continue

            videos_payload = _youtube_get(
                "videos",
                {
                    "part": "snippet,statistics,contentDetails",
                    "id": ",".join(video_ids),
                    "maxResults": 50,
                },
            )

            for item in videos_payload.get("items", []):
                snippet = item.get("snippet", {})
                statistics = item.get("statistics", {})
                content_details = item.get("contentDetails", {})
                title = snippet.get("title", "")
                description = snippet.get("description", "")
                published_at = _parse_youtube_datetime(snippet.get("publishedAt", datetime.now(timezone.utc).isoformat()))

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

        # Remove duplicates and sort by view count
        seen_ids = set()
        unique_videos = []
        for video in videos:
            if video.id not in seen_ids:
                seen_ids.add(video.id)
                unique_videos.append(video)

        unique_videos.sort(key=lambda v: v.views, reverse=True)
        return _recent_only(unique_videos, hours)
    except Exception:
        return _recent_only(sample_youtube, hours)
