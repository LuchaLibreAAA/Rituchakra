"use client";

import { useEffect, useState } from "react";
import { ChatDock } from "@/components/ChatDock";
import { DistrictSearch } from "@/components/DistrictSearch";
import { EarlyWarnings } from "@/components/EarlyWarnings";
import { ForecastCharts } from "@/components/ForecastCharts";
import { OverviewLive, OverviewPlots } from "@/components/OverviewLive";
import { LensGrid } from "@/components/LensGrid";
import { MandiPanel } from "@/components/MandiPanel";
import { OutlookTable } from "@/components/OutlookTable";
import { PredictionsPanel } from "@/components/PredictionsPanel";
import { RiskCard } from "@/components/RiskCard";
import { Sidebar } from "@/components/Sidebar";
import { SquareMap } from "@/components/SquareMap";
import { COPY } from "@/i18n/copy";
import { fetchCompare, searchPlaces } from "@/lib/api";
import { useApp } from "@/lib/store";

export default function Page() {
  const { locale, tab, dashboard, status, error, refresh, quietRefresh, setLocation } = useApp();
  const t = COPY[locale];
  const [cmpQ, setCmpQ] = useState("Pune");
  const [cmp, setCmp] = useState<Record<string, unknown> | null>(null);
  const [cmpBusy, setCmpBusy] = useState(false);
  const [plotsOpen, setPlotsOpen] = useState(false);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    const id = window.setInterval(() => {
      void quietRefresh();
    }, 60_000);
    return () => window.clearInterval(id);
  }, [quietRefresh]);

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

  return (
    <div className="mx-auto flex min-h-screen max-w-[1600px] flex-col gap-3 p-3 lg:flex-row lg:p-4">
      <Sidebar />
      <div className="min-w-0 flex-1 space-y-3">
        <header className="neo flex flex-wrap items-center gap-3 px-4 py-3">
          <DistrictSearch locale={locale} onPick={(l) => setLocation(l)} />
          {dashboard ? (
            <div className="flex min-w-0 flex-wrap items-center gap-2">
              <span className="live-dot" aria-hidden />
              <span className="truncate text-sm font-semibold text-neo-accent">{dashboard.location.label}</span>
              {liveAt ? (
                <span className="text-[11px] text-neo-muted">
                  {t.updated}{" "}
                  {new Date(liveAt).toLocaleTimeString("en-IN", {
                    timeZone: "Asia/Kolkata",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}{" "}
                  IST
                </span>
              ) : null}
              <span className="chip">{t.autoRefresh}</span>
              {dashboard.descriptive.current.aqi != null ? (
                <span className="chip">
                  {t.aqi} {dashboard.descriptive.current.aqi}
                </span>
              ) : null}
            </div>
          ) : null}
        </header>

        {status === "error" ? (
          <p className="neo px-3 py-2 text-sm text-neo-danger">{error} — is FastAPI on :8000?</p>
        ) : null}

        {!dashboard ? (
          <p className="text-neo-muted">{status === "loading" ? t.loading : "…"}</p>
        ) : (
          <>
            {tab === "overview" && (
              <div className="space-y-3">
                <EarlyWarnings
                  items={dashboard.prescriptive.warnings}
                  locale={locale}
                  live={dashboard.live}
                  status={dashboard.provider_status}
                />
                <OverviewLive dash={dashboard} locale={locale} />
                <LensGrid dash={dashboard} locale={locale} focus="why-do" />
                <section className="neo px-4 py-3">
                  <button
                    type="button"
                    className="flex w-full items-center justify-between text-left"
                    onClick={() => setPlotsOpen((v) => !v)}
                    aria-expanded={plotsOpen}
                  >
                    <h3 className="text-[11px] font-bold uppercase tracking-[0.16em] text-neo-accent">{t.plots}</h3>
                    <span className="text-[11px] text-neo-muted">{plotsOpen ? t.collapse : t.expand}</span>
                  </button>
                  {plotsOpen ? (
                    <div className="mt-3">
                      <OverviewPlots dash={dashboard} locale={locale} />
                    </div>
                  ) : null}
                </section>
              </div>
            )}

            {tab === "map" && (
              <SquareMap dash={dashboard} locale={locale} onPick={(l) => setLocation(l)} />
            )}

            {tab === "forecast" && (
              <div className="space-y-4">
                <OutlookTable dash={dashboard} locale={locale} />
                <ForecastCharts dash={dashboard} locale={locale} />
                <section className="neo p-4">
                  <h3 className="text-[11px] font-bold uppercase tracking-[0.16em] text-neo-accent">{t.compare}</h3>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <input
                      value={cmpQ}
                      onChange={(e) => setCmpQ(e.target.value)}
                      className="neo-in px-3 py-2 text-sm outline-none"
                      placeholder="Pune"
                    />
                    <button className="neo-btn" disabled={cmpBusy} onClick={runCompare}>
                      {cmpBusy ? "…" : t.compare}
                    </button>
                  </div>
                  {cmp && !("error" in cmp) ? (
                    <pre className="mt-3 max-h-64 overflow-auto text-xs">
                      {JSON.stringify((cmp as { delta_a_minus_b?: unknown }).delta_a_minus_b, null, 2)}
                    </pre>
                  ) : null}
                </section>
              </div>
            )}

            {tab === "predicted" && <PredictionsPanel dash={dashboard} locale={locale} />}

            {tab === "risks" && (
              <div className="grid gap-4 lg:grid-cols-2">
                {dashboard.risks.map((r) => (
                  <RiskCard key={r.id} risk={r} locale={locale} />
                ))}
              </div>
            )}

            {tab === "market" && <MandiPanel dash={dashboard} locale={locale} />}

            {tab === "advisor" && <ChatDock tall />}
          </>
        )}
      </div>
    </div>
  );
}
