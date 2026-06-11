import type { Score } from "@/lib/types";

const rows: Array<[keyof Score, string, number]> = [
  ["trendMomentum", "Trend Momentum", 25],
  ["googleSearchDemand", "Search Demand", 20],
  ["medicalRelevance", "Medical Relevance", 20],
  ["youtubeHistoricalFit", "YouTube Fit", 20],
  ["conversionPotential", "Conversion", 10],
  ["safetyBrandFit", "Brand Safety", 5]
];

export function ScoreBreakdown({ score }: { score: Score }) {
  return (
    <section className="rounded-md border border-ink/10 bg-white p-4 shadow-soft">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-base font-bold">Score Breakdown</h2>
        <span className="rounded-md bg-ink px-3 py-1 text-sm font-bold text-white">{score.total}</span>
      </div>
      <div className="space-y-3">
        {rows.map(([key, label, max]) => {
          const value = Number(score[key] ?? 0);
          return (
            <div key={key}>
              <div className="mb-1 flex items-center justify-between text-xs font-semibold text-ink/70">
                <span>{label}</span>
                <span>
                  {Math.round(value)}/{max}
                </span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-mist">
                <div
                  className="h-full rounded-full bg-coral"
                  style={{ width: `${Math.min(100, (value / max) * 100)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
