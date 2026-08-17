"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { COPY, type Locale } from "@/i18n/copy";
import type { DashboardSnapshot } from "@/types/dashboard";

export function MandiPanel({ dash, locale }: { dash: DashboardSnapshot; locale: Locale }) {
  const rows = dash.ogd?.mandi || [];
  if (!rows.length) return <p className="text-sm text-neo-muted">No Agmarknet arrivals for this district today.</p>;
  const chart = rows.slice(0, 8).map((r) => ({
    name: `${r.commodity}`.slice(0, 10),
    price: r.modal_price,
  }));
  return (
    <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
      <section className="neo p-4">
        <div className="mb-2 flex items-center justify-between">
          <h3 className="text-[11px] font-bold uppercase tracking-[0.16em] text-neo-accent">
            {COPY[locale].mandi}
          </h3>
          <span className="chip">INR / quintal</span>
        </div>
        <div className="max-h-72 overflow-auto">
          <table className="w-full text-left text-xs">
            <thead className="text-neo-muted">
              <tr>
                <th className="py-1 font-medium">Commodity</th>
                <th className="py-1 font-medium">Market</th>
                <th className="py-1 font-medium">Modal</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={`${r.commodity}-${r.market}-${i}`} className="border-t border-[#d5dde6]">
                  <td className="py-1.5">
                    {r.commodity}
                    {r.variety ? <span className="text-neo-muted"> · {r.variety}</span> : null}
                  </td>
                  <td className="py-1.5 text-neo-muted">{r.market}</td>
                  <td className="py-1.5 font-mono text-neo-accent">{r.modal_price}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section className="neo p-4">
        <h3 className="mb-2 text-[11px] font-bold uppercase tracking-[0.16em] text-neo-accent">Modal prices</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chart} layout="vertical" margin={{ left: 24 }}>
              <CartesianGrid stroke="#d5dde6" horizontal={false} />
              <XAxis type="number" stroke="#6b7c93" fontSize={10} />
              <YAxis type="category" dataKey="name" stroke="#6b7c93" fontSize={10} width={70} />
              <Tooltip contentStyle={{ background: "#e8eef4", border: "none", borderRadius: 12 }} />
              <Bar dataKey="price" fill="#3a7ca5" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
}
