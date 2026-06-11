import { Header } from "@/components/Header";
import { TrendCard } from "@/components/TrendCard";
import { getTrendHistory } from "@/lib/api";

export default async function TrendHistoryPage() {
  const trends = await getTrendHistory();

  return (
    <div>
      <Header title="Trend History" subtitle="Trends from previous searches. The most recent search results live on the Home tab." />
      <div className="stagger-list space-y-3">
        {trends.length ? (
          trends.map((trend, index) => <TrendCard key={trend.rowId ?? trend.id} trend={trend} rank={index + 1} />)
        ) : (
          <p className="text-sm text-ink/60">No history yet. Run another search from the Home screen — the current results will move here.</p>
        )}
      </div>
    </div>
  );
}
