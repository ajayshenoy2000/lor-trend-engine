"use client";

import { useState } from "react";
import { Header } from "@/components/Header";
import { useEffect } from "react";
import { X } from "lucide-react";
import { API_BASE } from "@/lib/api-config";

interface Settings {
  keywords: string[];
  apiKeys: {
    youtube: boolean;
    x: boolean;
    anthropic: boolean;
    openai: boolean;
  };
  channelId: string;
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [keywords, setKeywords] = useState<string[]>([]);
  const [newKeyword, setNewKeyword] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/api/settings`, { cache: "no-store" })
      .then((res) => res.json())
      .then((data) => {
        setSettings(data);
        setKeywords(data.keywords);
      })
      .catch((err) => setError(err.message));
  }, []);

  const handleAddKeyword = () => {
    if (newKeyword.trim() && !keywords.includes(newKeyword.trim())) {
      setKeywords([...keywords, newKeyword.trim()]);
      setNewKeyword("");
    }
  };

  const handleRemoveKeyword = (keyword: string) => {
    setKeywords(keywords.filter((k) => k !== keyword));
  };

  const handleSaveKeywords = async () => {
    if (keywords.length === 0) {
      setError("Please add at least one keyword");
      return;
    }
    setSaving(true);
    setError(null);
    setSuccess(false);
    try {
      const response = await fetch(`${API_BASE}/api/keywords`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ keywords }),
      });
      if (!response.ok) throw new Error("Failed to save keywords");
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error saving keywords");
    } finally {
      setSaving(false);
    }
  };

  if (!settings) return <div>Loading...</div>;

  return (
    <div>
      <Header title="Settings" subtitle="API connection status and searchable keywords. Keywords are used when you run Search Now. Edit below to customize your search." />
      <div className="grid gap-5 lg:grid-cols-2">
        <section className="rounded-md border border-ink/10 bg-white p-4 shadow-soft lg:col-span-2">
          <h2 className="mb-4 text-xl font-bold">API Connections</h2>
          <div className="space-y-3 text-sm">
            <Status label="YouTube API Key" ready={settings.apiKeys.youtube} />
            <Status label="YouTube Channel ID" ready={Boolean(settings.channelId)} value={settings.channelId || "Not set"} />
            <Status label="X Bearer Token" ready={settings.apiKeys.x} />
            <Status label="Anthropic API Key" ready={settings.apiKeys.anthropic} />
            <Status label="OpenAI API Key" ready={settings.apiKeys.openai} />
          </div>
        </section>
        <section className="rounded-md border border-ink/10 bg-white p-4 shadow-soft lg:col-span-2">
          <h2 className="mb-4 text-xl font-bold">Search Keywords</h2>
          <div className="mb-4 space-y-3">
            <div className="flex gap-2">
              <input
                type="text"
                value={newKeyword}
                onChange={(e) => setNewKeyword(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleAddKeyword()}
                placeholder="Add a keyword..."
                className="min-h-11 flex-1 rounded-md border border-ink/10 bg-mist px-3 text-sm outline-none focus:border-sage"
              />
              <button
                onClick={handleAddKeyword}
                disabled={!newKeyword.trim()}
                className="min-h-11 rounded-md bg-sage px-4 text-sm font-bold text-white disabled:cursor-not-allowed disabled:bg-ink/25"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {keywords.map((keyword) => (
                <div
                  key={keyword}
                  className="flex items-center gap-2 rounded-md bg-sage/10 px-3 py-2 text-sm font-bold text-sage"
                >
                  {keyword}
                  <button
                    onClick={() => handleRemoveKeyword(keyword)}
                    className="flex h-4 w-4 items-center justify-center hover:opacity-70"
                    type="button"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
            {error && <p className="text-sm text-coral">{error}</p>}
            {success && <p className="text-sm text-sage font-bold">Keywords updated!</p>}
          </div>
          <button
            onClick={handleSaveKeywords}
            disabled={saving || keywords.length === 0}
            className="min-h-11 w-full rounded-md bg-sage px-4 text-sm font-bold text-white disabled:cursor-not-allowed disabled:bg-ink/25"
          >
            {saving ? "Saving..." : "Save Keywords"}
          </button>
        </section>
      </div>
    </div>
  );
}

function Status({ label, ready, value }: { label: string; ready: boolean; value?: string }) {
  return (
    <div className="flex min-h-11 items-center justify-between gap-3 rounded-md bg-mist px-3">
      <span className="font-bold text-ink/70">{label}</span>
      <span className={`rounded-md px-2 py-1 text-xs font-bold ${ready ? "bg-sage/15 text-sage" : "bg-coral/10 text-coral"}`}>
        {value ?? (ready ? "Configured" : "Missing")}
      </span>
    </div>
  );
}
