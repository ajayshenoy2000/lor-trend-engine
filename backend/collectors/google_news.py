from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha1
from urllib.parse import quote
from xml.etree import ElementTree
import urllib.request

from backend.db.models import SourceItem
from backend.sample_data import sample_sources


def _recent_only(items: list[SourceItem], hours: int) -> list[SourceItem]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    return [item for item in items if item.published_at >= cutoff]


def _google_news_when(hours: int) -> str:
    if hours <= 12:
        return "12h"
    if hours <= 24:
        return "1d"
    if hours <= 72:
        return "3d"
    if hours <= 168:
        return "7d"
    return "30d"


def collect_google_news(keywords: list[str], limit_per_keyword: int = 5, hours: int = 24) -> list[SourceItem]:
    items: list[SourceItem] = []
    for keyword in keywords:
        query = f"{keyword} when:{_google_news_when(hours)}"
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl=ja&gl=JP&ceid=JP:ja"
        try:
            with urllib.request.urlopen(url, timeout=8) as response:
                root = ElementTree.fromstring(response.read())
            for entry in root.findall(".//item")[:limit_per_keyword]:
                title = entry.findtext("title") or keyword
                link = entry.findtext("link") or url
                published = entry.findtext("pubDate")
                published_at = datetime.now(timezone.utc)
                if published:
                    try:
                        published_at = datetime.strptime(published, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=timezone.utc)
                    except ValueError:
                        pass
                item_id = sha1(f"google_news:{keyword}:{title}".encode()).hexdigest()
                items.append(
                    SourceItem(
                        id=item_id,
                        source="google_news",
                        title=title,
                        text=entry.findtext("description") or title,
                        url=link,
                        keyword=keyword,
                        published_at=published_at,
                        engagement=25,
                    )
                )
        except Exception:
            continue
    recent_items = _recent_only(items, hours)
    fallback = _recent_only([item for item in sample_sources if item.source == "google_news"], hours)
    return recent_items or fallback
