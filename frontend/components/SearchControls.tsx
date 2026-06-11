"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Play, RefreshCw } from "lucide-react";
import { searchNow } from "@/lib/api";
import type { AppSettings, ModelProvider, SearchSource, SearchNowResponse, TimeWindow } from "@/lib/types";

const sources: Array<{ id: SearchSource; label: string; detail: string }> = [
  { id: "x", label: "X", detail: "Recent posts" },
  { id: "google_news", label: "Google News", detail: "RSS articles" },
  { id: "google_trends", label: "Google Trends", detail: "Search demand" },
  { id: "youtube", label: "YouTube", detail: "Historical fit" }
];

const timeWindows: TimeWindow[] = ["12h", "24h", "3d", "7d", "30d"];

export function SearchControls({ settings }: { settings: AppSettings }) {
  const router = useRouter();
  const [enabledSources, setEnabledSources] = useState<SearchSource[]>(["x", "google_news", "google_trends", "youtube"]);
  const [timeWindow, setTimeWindow] = useState<TimeWindow>("24h");
  const [analysisModelProvider, setAnalysisModelProvider] = useState<ModelProvider>(settings.analysisModelProvider ?? "gpt");
  const [briefModelProvider, setBriefModelProvider] = useState<ModelProvider>(settings.briefModelProvider ?? "claude");
  const [isSearching, setIsSearching] = useState(false);
  const [result, setResult] = useState<SearchNowResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const disabled = enabledSources.length === 0 || isSearching;
  const sourceText = useMemo(() => enabledSources.join(", "), [enabledSources]);

  async function handleSearch() {
    setIsSearching(true);
    setError(null);
    try {
      const response = await searchNow({
        sources: enabledSources,
        timeWindow,
        analysisModelProvider,
        briefModelProvider
      });
      setResult(response);
      router.refresh();
    } catch (searchError) {
      setError(searchError instanceof Error ? searchError.message : "Search failed");
    } finally {
      setIsSearching(false);
    }
  }

  function toggleSource(source: SearchSource) {
    setEnabledSources((current) =>
      current.includes(source) ? current.filter((item) => item !== source) : [...current, source]
    );
  }

  return (
    <section className="rounded-md border border-ink/10 bg-white p-4 shadow-soft lg:col-span-2">
      <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-bold uppercase text-coral">On-demand collection</p>
          <h2 className="text-xl font-bold">Search Now</h2>
          <p className="mt-1 text-sm leading-6 text-ink/60">Fetch only when you press the button. No weekly scheduler is required.</p>
        </div>
        <button
          className="flex min-h-12 items-center justify-center gap-2 rounded-md bg-coral px-5 text-sm font-bold text-white disabled:cursor-not-allowed disabled:bg-ink/25"
          disabled={disabled}
          onClick={handleSearch}
          type="button"
        >
          {isSearching ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          {isSearching ? "Searching" : "Search Now"}
        </button>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <div>
          <h3 className="mb-2 text-sm font-bold">Sources</h3>
          <div className="grid grid-cols-2 gap-2">
            {sources.map((source) => {
              const checked = enabledSources.includes(source.id);
              return (
                <button
                  key={source.id}
                  className={`min-h-16 rounded-md border px-3 text-left transition ${
                    checked ? "border-sage bg-sage/10" : "border-ink/10 bg-mist"
                  }`}
                  onClick={() => toggleSource(source.id)}
                  type="button"
                >
                  <span className="flex items-center gap-2 text-sm font-bold">
                    <span className={`h-3 w-3 rounded-sm border ${checked ? "border-sage bg-sage" : "border-ink/25 bg-white"}`} />
                    {source.label}
                  </span>
                  <span className="mt-1 block text-xs font-semibold text-ink/50">{source.detail}</span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <h3 className="mb-2 text-sm font-bold">Data Window</h3>
            <div className="grid grid-cols-5 gap-2">
              {timeWindows.map((window) => (
                <button
                  key={window}
                  className={`min-h-11 rounded-md text-sm font-bold ${
                    timeWindow === window ? "bg-ink text-white" : "bg-mist text-ink/70"
                  }`}
                  onClick={() => setTimeWindow(window)}
                  type="button"
                >
                  {window}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <ModelSelect label="Analysis Model" value={analysisModelProvider} onChange={setAnalysisModelProvider} />
            <ModelSelect label="Brief Model" value={briefModelProvider} onChange={setBriefModelProvider} />
          </div>
        </div>
      </div>

      <div className="mt-4 rounded-md bg-mist p-3 text-sm leading-6 text-ink/65">
        <strong className="text-ink">Current request:</strong> {timeWindow} · {sourceText || "No sources"} · analysis {analysisModelProvider} · briefs {briefModelProvider}
      </div>

      {result ? (
        <div className="mt-3 rounded-md border border-sage/25 bg-sage/10 p-3 text-sm font-semibold text-ink/75">
          Search complete: {result.trends.length} trends ranked, {result.recordThisWeek.length} record recommendations. Window: {result.meta.timeWindow}.
        </div>
      ) : null}
      {error ? <div className="mt-3 rounded-md border border-coral/30 bg-coral/10 p-3 text-sm font-semibold text-coral">{error}</div> : null}
    </section>
  );
}

function ModelSelect({
  label,
  value,
  onChange
}: {
  label: string;
  value: ModelProvider;
  onChange: (value: ModelProvider) => void;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-bold text-ink/70">{label}</span>
      <select
        className="min-h-11 w-full rounded-md border border-ink/10 bg-mist px-3 text-sm font-bold outline-none focus:border-sage"
        value={value}
        onChange={(event) => onChange(event.target.value as ModelProvider)}
      >
        <option value="gpt">GPT</option>
        <option value="claude">Claude</option>
      </select>
    </label>
  );
}
