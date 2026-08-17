"use client";

import type { RiskCard as Risk } from "@/types/dashboard";
import { COPY, type Locale } from "@/i18n/copy";

const SEV: Record<string, string> = {
  high: "text-neo-danger",
  medium: "text-neo-warn",
  low: "text-neo-accent2",
  minimal: "text-neo-muted",
};

export function RiskCard({ risk, locale }: { risk: Risk; locale: Locale }) {
  const t = COPY[locale];
  return (
    <article className="neo p-4">
      <div className="flex items-baseline justify-between gap-3">
        <h3 className="text-sm font-bold tracking-wide">
          {risk.label}:{" "}
          <span className={SEV[risk.severity] || ""}>
            {risk.severity.toUpperCase()} — {risk.score_pct}%
          </span>
        </h3>
        <span className="chip">{risk.horizon_hours}h</span>
      </div>
      <p className="mt-3 text-[11px] uppercase tracking-[0.14em] text-neo-muted">{t.factors}</p>
      <ul className="mt-2 space-y-2">
        {risk.factors.map((f) => (
          <li key={f.id}>
            <div className="mb-1 flex justify-between text-sm">
              <span>{f.label}</span>
              <span className="font-mono text-neo-accent">{f.contribution_pct}%</span>
            </div>
            <div className="neo-in h-2 overflow-hidden rounded-full">
              <div
                className="h-full rounded-full bg-neo-accent/70"
                style={{ width: `${Math.min(100, f.contribution_pct)}%` }}
              />
            </div>
          </li>
        ))}
      </ul>
      <div className="mt-3 flex items-center justify-between text-xs text-neo-muted">
        <span>
          {t.confidence}: <strong className="text-neo-text">{risk.confidence_pct}%</strong>
        </span>
        <span className="font-mono">{risk.method}</span>
      </div>
    </article>
  );
}
