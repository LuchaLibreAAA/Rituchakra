"use client";

import type { DashboardSnapshot } from "@/types/dashboard";
import { COPY, type Locale } from "@/i18n/copy";

export function OutlookTable({ dash, locale }: { dash: DashboardSnapshot; locale: Locale }) {
  const t = COPY[locale];
  const days = dash.predictive.outlook_days || [];
  return (
    <section className="neo p-4">
      <div className="mb-3 flex flex-wrap gap-3 text-sm">
        <span className="chip">
          {t.rain7}: {dash.predictive.precip_7d_mm ?? "—"} mm
        </span>
        <span className="chip">
          {t.balance}: {dash.predictive.water_balance_7d_mm ?? "—"} mm
        </span>
        <span className="chip">
          {t.irrigateDays}: {(dash.predictive.irrigate_dates || []).length}
        </span>
        <span className="chip">
          {t.floodDays}: {(dash.predictive.flood_watch_dates || []).length}
        </span>
      </div>
      <div className="overflow-auto">
        <table className="w-full text-left text-xs">
          <thead className="text-neo-muted">
            <tr>
              <th className="py-2">Date</th>
              <th>Rain</th>
              <th>P%</th>
              <th>Tmax</th>
              <th>ET₀</th>
              <th>Soil</th>
              <th>WB</th>
              <th>Flag</th>
            </tr>
          </thead>
          <tbody>
            {days.map((d) => (
              <tr key={d.date} className="border-t border-[#d5dde6]">
                <td className="py-2 font-mono">{d.date}</td>
                <td>{d.precip_mm}</td>
                <td>{d.precip_prob_pct}</td>
                <td>{d.temp_max_c ?? "—"}</td>
                <td>{d.et0_mm}</td>
                <td>{d.soil_m3m3}</td>
                <td>{d.water_balance_mm}</td>
                <td>
                  {d.flood_watch ? "flood" : ""}
                  {d.irrigate ? " irrigate" : ""}
                  {!d.flood_watch && !d.irrigate ? "—" : ""}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
