import Link from "next/link";
import { ArrowRight, CheckCircle2, ShieldAlert } from "lucide-react";
import type { Trend } from "@/lib/types";

export function TrendCard({ trend, rank }: { trend: Trend; rank?: number }) {
  return (
    <Link href={`/trends/${trend.id}`} className="block rounded-md border border-ink/10 bg-white p-4 shadow-soft transition hover:-translate-y-0.5 hover:border-sage/50">
      <div className="mb-3 flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            {rank ? <span className="rounded-md bg-gold/15 px-2 py-1 text-xs font-bold text-ink">#{rank}</span> : null}
            <span className="rounded-md bg-mist px-2 py-1 text-xs font-semibold text-ink/70">{trend.keyword}</span>
          </div>
          <h2 className="text-lg font-bold leading-snug text-ink">{trend.title}</h2>
        </div>
        <div className="shrink-0 rounded-md bg-ink px-3 py-2 text-center text-white">
          <div className="text-lg font-bold leading-none">{Math.round(trend.score.total)}</div>
          <div className="text-[10px] uppercase">score</div>
        </div>
      </div>
      <p className="mb-3 text-sm leading-6 text-ink/68">{trend.summary}</p>
      <div className="mb-4 flex flex-wrap gap-2">
        {trend.clusterTerms.slice(0, 5).map((term) => (
          <span key={term} className="rounded-md border border-ink/10 px-2 py-1 text-xs text-ink/60">
            {term}
          </span>
        ))}
      </div>
      <div className="flex items-center justify-between text-sm font-semibold text-sage">
        <span className="flex items-center gap-2">
          {trend.safetyNotes.length ? <ShieldAlert className="h-4 w-4" /> : <CheckCircle2 className="h-4 w-4" />}
          {trend.safetyNotes.length ? "Risk-aware angle" : "Ready angle"}
        </span>
        <ArrowRight className="h-4 w-4" />
      </div>
    </Link>
  );
}
