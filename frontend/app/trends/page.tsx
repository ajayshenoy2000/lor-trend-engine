import { Header } from "@/components/Header";
import { TrendFilter } from "@/components/TrendFilter";
import { getTrendHistory } from "@/lib/api";

export default async function TrendHistoryPage() {
  const trends = await getTrendHistory();

  return (
    <div>
      <Header title="Trend History" subtitle="Trends from previous searches. The most recent search results live on the Home tab." />
      {trends.length ? (
        <TrendFilter trends={trends} />
      ) : (
        <p className="text-sm text-ink/60">No history yet. Run another search from the Home screen — the current results will move here.</p>
      )}
    </div>
  );
}
