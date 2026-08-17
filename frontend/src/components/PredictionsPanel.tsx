"use client";

import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { COPY, type Locale } from "@/i18n/copy";
import type { DashboardSnapshot, PredictionPack } from "@/types/dashboard";

export function PredictionsPanel({ dash, locale }: { dash: DashboardSnapshot; locale: Locale }) {
  const t = COPY[locale];
  const [src, setSrc] = useState<"ours" | "trusted">("ours");
  const pack: PredictionPack | undefined = src === "ours" ? dash.predictions?.ours : dash.predictions?.trusted;
  const other = src === "ours" ? dash.predictions?.trusted : dash.predictions?.ours;
  const chart = useMemo(() => {
    const a = dash.predictions?.ours?.days || [];
    const b = dash.predictions?.trusted?.days || [];
    const n = Math.max(a.length, b.length);
    return Array.from({ length: n }, (_, i) => ({
      d: (a[i]?.date || b[i]?.date || "").slice(5),
      ours: a[i]?.precip_mm,
      trusted: b[i]?.precip_mm,
    }));
  }, [dash.predictions]);

  if (!pack) {
    return <p className="text-sm text-neo-muted">{t.loading}</p>;
  }

  return (
    <div className="space-y-4">
      <div className="neo flex flex-wrap items-center gap-2 p-3">
        <button className={`neo-btn ${src === "ours" ? "neo-btn-on" : ""}`} onClick={() => setSrc("ours")}>
          {t.ours}
        </button>
        <button className={`neo-btn ${src === "trusted" ? "neo-btn-on" : ""}`} onClick={() => setSrc("trusted")}>
          {t.trusted}
        </button>
        <p className="text-xs text-neo-muted">{t.predHint}</p>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <Kpi label={t.rain3} value={`${pack.precip_3d_mm} mm`} sub={other ? `API ${other.precip_3d_mm}` : ""} />
        <Kpi label={t.rain7} value={`${pack.precip_7d_mm} mm`} sub={other ? `API ${other.precip_7d_mm}` : ""} />
        <Kpi label={t.balance} value={`${pack.water_balance_7d_mm} mm`} />
      </div>

      <section className="neo p-4">
        <p className="text-sm font-semibold text-neo-accent">{pack.source}</p>
        <p className="text-xs text-neo-muted">{pack.method}</p>
        <div className="mt-3 h-56">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chart}>
              <CartesianGrid stroke="#cfe0dd" vertical={false} />
              <XAxis dataKey="d" stroke="#4d6b70" fontSize={10} />
              <YAxis stroke="#4d6b70" fontSize={10} width={28} />
              <Tooltip contentStyle={{ background: "#eef6f4", border: "none", borderRadius: 16 }} />
              <Legend />
              <Bar dataKey="ours" fill="#146b7a" radius={[6, 6, 0, 0]} />
              <Bar dataKey="trusted" fill="#4aa3b5" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      {dash.predictions?.hazards ? (
        <section className="neo p-4">
          <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-neo-accent">{t.hazardOutlook}</p>
          <div className="mt-3 grid gap-3 md:grid-cols-3">
            {(["flood", "tsunami", "seismic"] as const).map((k) => {
              const h = dash.predictions?.hazards?.[k];
              if (!h) return null;
              return (
                <div key={k} className="neo-in p-3">
                  <p className="text-[10px] uppercase tracking-widest text-neo-muted">{k}</p>
                  <p className="mt-1 font-mono text-2xl font-bold text-neo-accent">{h.score_pct ?? "—"}%</p>
                  <p className="text-sm font-semibold">{h.level || "—"}</p>
                  {"nearest_place" in h && h.nearest_place ? (
                    <p className="mt-1 text-xs text-neo-muted">
                      M{h.nearest_mag} · {h.nearest_km} km · {h.nearest_place}
                    </p>
                  ) : null}
                  {"latest_title" in h && h.latest_title ? (
                    <p className="mt-1 text-xs text-neo-muted">{h.latest_title}</p>
                  ) : null}
                  {"drivers" in h && Array.isArray(h.drivers) ? (
                    <p className="mt-1 text-[11px] text-neo-muted">{h.drivers.slice(0, 3).join(" · ")}</p>
                  ) : null}
                  <p className="mt-2 text-[10px] text-neo-muted">{h.method}</p>
                </div>
              );
            })}
          </div>
        </section>
      ) : null}

      <section className="neo overflow-auto p-4">
        <table className="w-full text-left text-xs">
          <thead className="text-neo-muted">
            <tr>
              <th className="py-2">Date</th>
              <th>Rain</th>
              <th>P%</th>
              <th>ET₀</th>
              <th>Soil</th>
              <th>Conf</th>
              <th>Note</th>
            </tr>
          </thead>
          <tbody>
            {pack.days.map((d) => (
              <tr key={d.date} className="border-t border-[#cfe0dd]">
                <td className="py-2 font-mono">{d.date}</td>
                <td>{d.precip_mm}</td>
                <td>{d.precip_prob_pct}</td>
                <td>{d.et0_mm}</td>
                <td>{d.soil_m3m3}</td>
                <td>{d.confidence_pct ?? "—"}</td>
                <td className="text-neo-muted">{d.adjustment || (d.flood_watch ? "flood" : d.irrigate ? "irrigate" : "—")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

function Kpi({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="neo p-4">
      <p className="text-[10px] uppercase tracking-widest text-neo-muted">{label}</p>
      <p className="font-mono text-2xl font-bold text-neo-accent">{value}</p>
      {sub ? <p className="text-[11px] text-neo-muted">{sub}</p> : null}
    </div>
  );
}
