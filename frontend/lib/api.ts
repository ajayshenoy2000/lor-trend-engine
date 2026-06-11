import { sampleBrief, sampleSources, sampleTrends } from "./sampleData";
import type { AppSettings, Brief, SearchNowRequest, SearchNowResponse, SourceItem, Trend } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function getJson<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
    if (!response.ok) return fallback;
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export function getTopTrends() {
  return getJson<Trend[]>("/api/top-trends", sampleTrends);
}

export function getRecordThisWeek() {
  return getJson<Trend[]>("/api/record-this-week", sampleTrends.slice(0, 2));
}

export function getVideoOpportunities() {
  return getJson<Trend[]>("/api/video-opportunities", sampleTrends.slice(0, 2));
}

export function getTrend(id: string) {
  const fallback = sampleTrends.find((trend) => trend.id === id) ?? sampleTrends[0];
  return getJson<Trend>(`/api/trends/${id}`, fallback);
}

export function getBrief(id: string) {
  return getJson<Brief>(`/api/briefs/${id}`, sampleBrief);
}

export function getBriefs() {
  return getJson<Brief[]>("/api/briefs", [sampleBrief]);
}

export function getSources() {
  return getJson<SourceItem[]>("/api/sources", sampleSources);
}

export function getSettings() {
  return getJson<AppSettings>("/api/settings", {
    keywords: ["二重整形", "埋没", "クマ取り", "美容医療", "涙袋", "ヒアルロン酸", "ボトックス", "マンジャロ", "GLP-1"],
    scoringWeights: {
      trend_momentum: 25,
      google_search_demand: 20,
      medical_relevance: 20,
      youtube_historical_fit: 20,
      conversion_potential: 10,
      safety_brand_fit: 5
    },
    channelId: "",
    modelProvider: "mock",
    analysisModelProvider: "gpt",
    briefModelProvider: "claude",
    lastSearch: {
      mode: "sample",
      timeWindow: "sample",
      sources: ["x", "google_news", "google_trends", "youtube"],
      analysisModelProvider: "gpt",
      briefModelProvider: "claude"
    },
    apiKeys: {
      youtube: false,
      x: false,
      anthropic: false,
      openai: false
    }
  });
}

export async function searchNow(payload: SearchNowRequest): Promise<SearchNowResponse> {
  const response = await fetch(`${API_BASE}/api/search-now`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Search failed");
  }
  return (await response.json()) as SearchNowResponse;
}
