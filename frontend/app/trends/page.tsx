import { Header } from "@/components/Header";
import { TrendCard } from "@/components/TrendCard";
import { getTopTrends } from "@/lib/api";

export default async function TrendsPage() {
  const trends = await getTopTrends();

  return (
    <div>
      <Header title="Trends" subtitle="All ranked topics from the most recent search, sorted by score." />
      <div className="space-y-3">
        {trends.length ? (
          trends.map((trend, index) => <TrendCard key={trend.id} trend={trend} rank={index + 1} />)
        ) : (
          <p className="text-sm text-ink/60">No trends yet. Run a search from the Home screen.</p>
        )}
      </div>
    </div>
  );
}
