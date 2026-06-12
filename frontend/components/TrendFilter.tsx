"use client";

import { useState, useMemo } from "react";
import { X, Search } from "lucide-react";
import { TrendCard } from "./TrendCard";
import type { Trend } from "@/lib/types";

export function TrendFilter({ trends, showRank = true }: { trends: Trend[]; showRank?: boolean }) {
  const [filterText, setFilterText] = useState("");

  const filtered = useMemo(() => {
    if (!filterText.trim()) return trends;
    const query = filterText.toLowerCase();
    return trends.filter(
      (trend) =>
        trend.title.toLowerCase().includes(query) ||
        trend.keyword.toLowerCase().includes(query) ||
        trend.summary.toLowerCase().includes(query) ||
        trend.clusterTerms.some((term) => term.toLowerCase().includes(query))
    );
  }, [trends, filterText]);

  return (
    <>
      <div className="mb-4 flex flex-col gap-2">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink/40" />
          <input
            type="text"
            placeholder="Filter by keyword, title, or terms..."
            value={filterText}
            onChange={(e) => setFilterText(e.target.value)}
            className="min-h-11 w-full rounded-md border border-ink/10 bg-mist pl-9 pr-3 text-sm font-semibold outline-none focus:border-sage"
          />
          {filterText && (
            <button
              onClick={() => setFilterText("")}
              type="button"
              className="absolute right-3 top-1/2 -translate-y-1/2 text-ink/40 hover:text-ink/70"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
        {filterText && (
          <p className="text-xs text-ink/50">
            {filtered.length} of {trends.length} trend{trends.length === 1 ? "" : "s"} match
          </p>
        )}
      </div>
      <div className="stagger-list space-y-3">
        {filtered.map((trend, index) => (
          <TrendCard
            key={trend.rowId ?? trend.id}
            trend={trend}
            rank={showRank ? index + 1 : undefined}
          />
        ))}
      </div>
      {trends.length > 0 && filtered.length === 0 && (
        <p className="text-sm text-ink/60">No trends match your filter.</p>
      )}
    </>
  );
}
