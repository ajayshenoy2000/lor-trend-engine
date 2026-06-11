import Link from "next/link";
import { ArrowRight, FileText } from "lucide-react";
import { Header } from "@/components/Header";
import { getBriefs } from "@/lib/api";

export default async function BriefsPage() {
  const briefs = await getBriefs();

  return (
    <div>
      <Header title="Briefs" subtitle="Ready-to-shoot 3-5 minute talking briefs for this week's record-worthy topics." />
      <div className="space-y-3">
        {briefs.length ? (
          briefs.map((brief) => (
            <Link
              key={brief.id}
              href={`/briefs/${brief.id}`}
              className="flex items-center justify-between gap-3 rounded-md border border-ink/10 bg-white p-4 shadow-soft transition hover:-translate-y-0.5 hover:border-sage/50"
            >
              <div className="min-w-0">
                <div className="mb-2 flex items-center gap-2 text-xs font-bold uppercase text-coral">
                  <FileText className="h-4 w-4" />
                  {brief.durationMinutes} min
                </div>
                <h2 className="truncate text-lg font-bold leading-snug text-ink">{brief.titleOptions[0]}</h2>
                <p className="mt-1 truncate text-sm leading-6 text-ink/65">{brief.hook}</p>
              </div>
              <ArrowRight className="h-4 w-4 shrink-0 text-sage" />
            </Link>
          ))
        ) : (
          <p className="text-sm text-ink/60">No briefs yet. Run a search and approve a topic to generate one.</p>
        )}
      </div>
    </div>
  );
}
