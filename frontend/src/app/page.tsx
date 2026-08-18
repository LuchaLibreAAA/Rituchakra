"use client";

import { useEffect, useMemo, useState } from "react";
import { ChatDock } from "@/components/ChatDock";
import { DistrictSearch } from "@/components/DistrictSearch";
import { EarlyWarnings } from "@/components/EarlyWarnings";
import { ForecastCharts } from "@/components/ForecastCharts";
import { OverviewLive, OverviewPlots } from "@/components/OverviewLive";
import { OutlookTable } from "@/components/OutlookTable";
import { PredictionsPanel } from "@/components/PredictionsPanel";
import { RiskCard } from "@/components/RiskCard";
import { SettingsPanel } from "@/components/SettingsPanel";
import { Sidebar } from "@/components/Sidebar";
import { SquareMap } from "@/components/SquareMap";
import { ThemeBoot } from "@/components/ThemeBoot";
import { Collapse, SourcesBox } from "@/components/ui";
import { COPY } from "@/i18n/copy";
import { fetchCompare, searchPlaces } from "@/lib/api";
import { rain } from "@/lib/units";
import { useApp } from "@/lib/store";
import type { TabId } from "@/types/dashboard";

const TAB_ORDER: TabId[] = [
  "home",
  "weather",
  "air_quality",
  "marine",
  "seismic",
  "advisor",
  "settings",
];

export default function Page() {
  const {
    locale,
    tab,
    setTab,
    dashboard,
    status,
    error,
    refresh,
    quietRefresh,
    setLocation,
    favorites,
    toggleFavorite,
    settings,
  } = useApp();
  const t = COPY[locale];
  const [cmpQ, setCmpQ] = useState("Pune");
  const [cmp, setCmp] = useState<Record<string, unknown> | null>(null);
  const [cmpBusy, setCmpBusy] = useState(false);
  const [copied, setCopied] = useState(false);
  const units = settings.units;

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    const id = window.setInterval(() => {
      void quietRefresh();
    }, Math.max(15, settings.refreshSec) * 1000);
    return () => window.clearInterval(id);
  }, [quietRefresh, settings.refreshSec]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      const n = Number(e.key);
      if (n >= 1 && n <= 7) setTab(TAB_ORDER[n - 1]);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [setTab]);

  async function runCompare() {
    if (!dashboard) return;
    setCmpBusy(true);
    try {
      const hits = await searchPlaces(cmpQ);
      const other = hits[0]?.district || cmpQ;
      const data = await fetchCompare(dashboard.location.district, other);
      setCmp(data);
    } catch (e) {
      setCmp({ error: String(e) });
    } finally {
      setCmpBusy(false);
    }
  }

  const liveAt = dashboard?.live?.generated_at || dashboard?.generated_at;
  const pinned = dashboard ? favorites.some((f) => f.id === dashboard.location.id) : false;

  const cmpRows = useMemo(() => {
    const d = (cmp && !("error" in cmp) ? (cmp as { delta_a_minus_b?: Record<string, number | null> }).delta_a_minus_b : null) || {};
    return [
      { k: `${t.rain3} (mm)`, v: d.rain_3d_mm },
      { k: `${t.balance} (mm)`, v: d.water_balance_7d_mm },
      { k: `${t.floodWatch} (%)`, v: d.flood_score },
      { k: t.aqi, v: d.aqi },
    ];
  }, [cmp, t]);

  function copyBrief() {
    if (!dashboard) return;
    const act = dashboard.prescriptive.actions[0];
    const lines = [
      `Rituchakra — ${dashboard.location.label}`,
      `${t.rain3}: ${rain(dashboard.predictive.precip_next_3d_mm, units)}`,
      act?.action || "",
    ].filter(Boolean);
    void navigator.clipboard.writeText(lines.join("\n"));
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-[1600px] flex-col gap-3 p-2 sm:p-3 lg:flex-row lg:p-4">
      <ThemeBoot />
      <Sidebar />
      <div className="min-w-0 flex-1 space-y-3">
        <header className="neo flex flex-wrap items-center gap-2 px-3 py-2 sm:px-4">
          {dashboard ? (
            <div className="flex min-w-0 flex-wrap items-center gap-2">
              <span className="live-dot" aria-hidden />
              <span className="truncate text-sm font-semibold">{dashboard.location.label}</span>
              {liveAt ? (
                <span className="text-[11px] text-neo-muted">
                  {new Date(liveAt).toLocaleTimeString("en-IN", { timeZone: "Asia/Kolkata", hour: "2-digit", minute: "2-digit" })}
                </span>
              ) : null}
              <button className="neo-btn text-xs" onClick={() => toggleFavorite(dashboard.location)}>
                {pinned ? "★" : "☆"}
              </button>
              <button className="neo-btn text-xs" onClick={copyBrief}>
                {copied ? t.copied : t.copyBrief}
              </button>
            </div>
          ) : (
            <div className="text-sm font-bold text-neo-accent">{t.brand}</div>
          )}
        </header>

        {status === "error" ? <p className="neo px-3 py-2 text-sm text-neo-danger">{error}</p> : null}

        {tab === "home" ? (
          <div className="space-y-4">
            <section className="neo p-4">
              <h2 className="text-lg font-bold mb-3">{t.search}</h2>
              <DistrictSearch locale={locale} onPick={(l) => setLocation(l)} />
            </section>
            
            {dashboard ? (
              <div className="space-y-4">
                <SquareMap dash={dashboard} locale={locale} onPick={(l) => setLocation(l)} />
                <SourcesBox tab="home" locale={locale} />
              </div>
            ) : null}
          </div>
        ) : !dashboard && tab !== "settings" ? (
          <p className="text-neo-muted">{status === "loading" ? t.loading : "…"}</p>
        ) : (
          <>
            {tab === "weather" && dashboard ? (
              <div className="space-y-4">
                <OverviewLive dash={dashboard} locale={locale} />
                <OutlookTable dash={dashboard} locale={locale} />
                <ForecastCharts dash={dashboard} locale={locale} />
                <PredictionsPanel dash={dashboard} locale={locale} />
                <Collapse title={t.compare} defaultOpen={false}>
                  <div className="flex flex-wrap gap-2">
                    <input value={cmpQ} onChange={(e) => setCmpQ(e.target.value)} className="neo-in px-3 py-2 text-sm" placeholder="Pune" />
                    <button className="neo-btn" disabled={cmpBusy} onClick={runCompare}>
                      {cmpBusy ? "…" : t.compare}
                    </button>
                  </div>
                  {cmp && !("error" in cmp) ? (
                    <table className="mt-3 w-full text-left text-sm">
                      <tbody>
                        {cmpRows.map((row) => (
                          <tr key={row.k} className="border-t border-neo-line">
                            <td className="py-2 text-neo-muted">{row.k}</td>
                            <td className="py-2 font-mono">{row.v == null ? "—" : `${row.v > 0 ? "+" : ""}${row.v}`}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : null}
                </Collapse>
                <SourcesBox tab="weather" locale={locale} />
              </div>
            ) : null}

            {tab === "air_quality" && dashboard ? (
              <div className="space-y-4">
                <section className="neo p-4">
                  <h3 className="text-sm font-bold">{t.aqi}</h3>
                  <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4 text-sm">
                    <div>
                      <p className="text-[10px] uppercase text-neo-muted">{t.omAqi}</p>
                      <p className="font-mono text-lg font-semibold">{dashboard.descriptive.current.aqi != null ? `${dashboard.descriptive.current.aqi} ${dashboard.descriptive.current.aqi_category || ''}` : "—"}</p>
                    </div>
                  </div>
                </section>
                <OverviewPlots dash={dashboard} locale={locale} />
                <div className="grid gap-3 sm:grid-cols-2">
                  {dashboard.risks.filter(r => r.id.includes('air') || r.id.includes('aqi')).map((r) => (
                    <RiskCard key={r.id} risk={r} locale={locale} />
                  ))}
                </div>
                <EarlyWarnings
                  items={dashboard.prescriptive.warnings.filter(w => w.lenses.includes('air'))}
                  locale={locale}
                  live={dashboard.live}
                  status={dashboard.provider_status}
                />
                <SourcesBox tab="air_quality" locale={locale} />
              </div>
            ) : null}

            {tab === "marine" && dashboard ? (
              <div className="space-y-4">
                <section className="neo p-4">
                  <h3 className="text-sm font-bold">{t.marine}</h3>
                  <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4 text-sm">
                    <div>
                      <p className="text-[10px] uppercase text-neo-muted">{t.waves}</p>
                      <p className="font-mono text-lg font-semibold">{dashboard.live?.marine?.wave_height_m != null ? `${Number(dashboard.live.marine.wave_height_m).toFixed(1)} m` : "—"}</p>
                    </div>
                    <div>
                      <p className="text-[10px] uppercase text-neo-muted">{t.nearestCoast}</p>
                      <p className="font-mono text-lg font-semibold">{dashboard.live?.marine?.nearest_coast || "—"}</p>
                    </div>
                  </div>
                </section>
                <EarlyWarnings
                  items={dashboard.prescriptive.warnings.filter(w => w.lenses.includes('marine'))}
                  locale={locale}
                  live={dashboard.live}
                  status={dashboard.provider_status}
                />
                <div className="grid gap-3 sm:grid-cols-2">
                  {dashboard.risks.filter(r => r.id.includes('marine')).map((r) => (
                    <RiskCard key={r.id} risk={r} locale={locale} />
                  ))}
                </div>
                <SourcesBox tab="marine" locale={locale} />
              </div>
            ) : null}

            {tab === "seismic" && dashboard ? (
              <div className="space-y-4">
                <EarlyWarnings
                  items={dashboard.prescriptive.warnings.filter(w => w.lenses.includes('seismic') || w.lenses.includes('tsunami'))}
                  locale={locale}
                  live={dashboard.live}
                  status={dashboard.provider_status}
                />
                <div className="grid gap-3 sm:grid-cols-2">
                  {dashboard.risks.filter(r => r.id.includes('seismic') || r.id.includes('tsunami')).map((r) => (
                    <RiskCard key={r.id} risk={r} locale={locale} />
                  ))}
                </div>
                <SourcesBox tab="seismic" locale={locale} />
              </div>
            ) : null}

            {tab === "advisor" ? (
              <div className="space-y-3">
                <ChatDock />
                <SourcesBox tab="advisor" locale={locale} />
              </div>
            ) : null}

            {tab === "settings" ? (
              <div className="space-y-3">
                <SettingsPanel />
                <SourcesBox tab="settings" locale={locale} />
              </div>
            ) : null}
          </>
        )}
      </div>
    </div>
  );
}
