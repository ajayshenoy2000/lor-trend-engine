import Link from "next/link";
import { FileText } from "lucide-react";
import { Header } from "@/components/Header";
import { ScoreBreakdown } from "@/components/ScoreBreakdown";
import { SourceList } from "@/components/SourceList";
import { getTrend } from "@/lib/api";

export default async function TrendDetailPage({ params }: { params: { id: string } }) {
  const trend = await getTrend(params.id);

  return (
    <div>
      <Header title={trend.keyword} subtitle={trend.title} />
      <div className="grid gap-5 lg:grid-cols-[0.85fr_1.15fr]">
        <aside className="space-y-4">
          <ScoreBreakdown score={trend.score} />
          <Link
            href={`/briefs/brief-${trend.id}`}
            className="flex min-h-12 items-center justify-center gap-2 rounded-md bg-coral px-4 text-sm font-bold text-white shadow-soft"
          >
            <FileText className="h-4 w-4" />
            Open Video Brief
          </Link>
          <section className="rounded-md border border-ink/10 bg-white p-4 shadow-soft">
            <h2 className="mb-2 text-base font-bold">Why This Matters</h2>
            <p className="text-sm leading-6 text-ink/70">{trend.whyItMatters}</p>
          </section>
          <section className="rounded-md border border-ink/10 bg-white p-4 shadow-soft">
            <h2 className="mb-2 text-base font-bold">Safety Notes</h2>
            <div className="space-y-2">
              {trend.safetyNotes.map((note) => (
                <p key={note} className="rounded-md bg-mist p-2 text-sm leading-6 text-ink/70">
                  {note}
                </p>
              ))}
            </div>
          </section>
        </aside>
        <section className="space-y-5">
          <div className="rounded-md border border-ink/10 bg-white p-4 shadow-soft">
            <h2 className="mb-2 text-xl font-bold">{trend.title}</h2>
            <p className="text-sm leading-6 text-ink/70">{trend.summary}</p>
            <div className="mt-4 flex flex-wrap gap-2">
              {trend.clusterTerms.map((term) => (
                <span key={term} className="rounded-md border border-ink/10 px-2 py-1 text-xs font-semibold text-ink/60">
                  {term}
                </span>
              ))}
            </div>
          </div>
          <section>
            <h2 className="mb-3 text-xl font-bold">Source Links</h2>
            <SourceList sources={trend.sources} />
          </section>
          <section className="rounded-md border border-ink/10 bg-white p-4 shadow-soft">
            <h2 className="mb-3 text-xl font-bold">Related YouTube History</h2>
            <div className="space-y-3">
              {trend.youtubeHistory.length ? (
                trend.youtubeHistory.map((video) => (
                  <div key={video.id} className="rounded-md bg-mist p-3">
                    <div className="text-sm font-bold">{video.title}</div>
                    <div className="mt-1 text-xs font-semibold text-ink/55">
                      {video.category} · {video.views.toLocaleString()} views · CTR {video.ctr ? `${Math.round(video.ctr * 1000) / 10}%` : "--"}
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-ink/60">No close historical match yet. This may be a useful new-format test.</p>
              )}
            </div>
          </section>
        </section>
      </div>
    </div>
  );
}
