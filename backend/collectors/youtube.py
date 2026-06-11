from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
import isodate
import urllib.request
import json
import time

from backend.config import settings
from backend.db.models import YouTubeVideo
from backend.processors.classify import classify_topic
from backend.sample_data import sample_youtube


YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

# Cache the channel's full upload history in-process so repeated Search Now
# calls don't re-fetch ~everything from YouTube every time.
_CHANNEL_CACHE_TTL_SECONDS = 60 * 30
_channel_cache: dict[str, tuple[float, list[YouTubeVideo]]] = {}


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


def _fetch_channel_uploads(channel_id: str) -> list[YouTubeVideo]:
    """Fetch the channel's full upload history (up to 200 most recent videos)."""
    channels_payload = _youtube_get("channels", {"part": "contentDetails", "id": channel_id})
    items = channels_payload.get("items", [])
    if not items:
        return []
    uploads_playlist_id = items[0].get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
    if not uploads_playlist_id:
        return []

    video_ids: list[str] = []
    page_token: str | None = None
    for _ in range(4):  # up to 4 pages * 50 = 200 videos
        playlist_payload = _youtube_get(
            "playlistItems",
            {
                "part": "contentDetails",
                "playlistId": uploads_playlist_id,
                "maxResults": 50,
                "pageToken": page_token,
            },
        )
        for item in playlist_payload.get("items", []):
            video_id = item.get("contentDetails", {}).get("videoId")
            if video_id:
                video_ids.append(video_id)
        page_token = playlist_payload.get("nextPageToken")
        if not page_token:
            break

    return _videos_from_ids(video_ids)


def _get_channel_videos(channel_id: str) -> list[YouTubeVideo]:
    cached = _channel_cache.get(channel_id)
    now = time.monotonic()
    if cached and now - cached[0] < _CHANNEL_CACHE_TTL_SECONDS:
        return cached[1]
    try:
        videos = _fetch_channel_uploads(channel_id)
    except Exception:
        return cached[1] if cached else []
    _channel_cache[channel_id] = (now, videos)
    return videos


def _search_public_videos(keywords: list[str]) -> list[YouTubeVideo]:
    """Fallback: search public YouTube for topical reference videos."""
    videos: list[YouTubeVideo] = []
    for keyword in keywords[:8]:
        try:
            search_payload = _youtube_get(
                "search",
                {
                    "part": "snippet",
                    "q": keyword,
                    "type": "video",
                    "maxResults": 15,
                    "order": "relevance",
                    "regionCode": "JP",
                    "relevanceLanguage": "ja",
                },
            )
        except Exception:
            continue

        video_ids = [
            item["id"]["videoId"]
            for item in search_payload.get("items", [])
            if "videoId" in item.get("id", {})
        ]
        if not video_ids:
            continue
        try:
            videos.extend(_videos_from_ids(video_ids))
        except Exception:
            continue

    return videos


def collect_youtube_history(keywords: list[str] | None = None, hours: int | None = None) -> list[YouTubeVideo]:
    """Return reference videos for scoring "youtube historical fit" and the
    "Related YouTube History" panel.

    Priority order:
    1. The configured channel's own upload history (real performance data) -
       this is NOT time-windowed; a channel's past videos remain relevant
       reference points regardless of how recent the current search is.
    2. A broad public-search fallback across all provided keywords.
    3. Bundled sample data, if nothing else is configured/available.
    """
    if not settings.youtube_api_key or not keywords:
        return _recent_only(sample_youtube, hours)

    videos: list[YouTubeVideo] = []

    if settings.youtube_channel_id:
        try:
            videos.extend(_get_channel_videos(settings.youtube_channel_id))
        except Exception:
            pass

    if not videos:
        try:
            videos.extend(_search_public_videos(keywords))
        except Exception:
            pass

    if not videos:
        return _recent_only(sample_youtube, hours)

    seen_ids: set[str] = set()
    unique_videos: list[YouTubeVideo] = []
    for video in videos:
        if video.id and video.id not in seen_ids:
            seen_ids.add(video.id)
            unique_videos.append(video)

    unique_videos.sort(key=lambda v: v.views, reverse=True)
    return unique_videos
