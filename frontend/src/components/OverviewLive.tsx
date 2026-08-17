"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { DashboardSnapshot } from "@/types/dashboard";
import { COPY, type Locale } from "@/i18n/copy";

const tip = { background: "#e8eef4", border: "none", borderRadius: 12, fontSize: 12 };

function hhmm(t: string) {
  const i = t.indexOf("T");
  return i >= 0 ? t.slice(i + 1, i + 6) : t.slice(-5);
}

export function OverviewLive({ dash, locale }: { dash: DashboardSnapshot; locale: Locale }) {
  const t = COPY[locale];
  const live = dash.live;
  const sky = live?.sky || {};
  const wind = live?.wind || {};
  const rose = wind.rose || [];
  const maxRose = Math.max(1, ...rose.map((r) => r.count));

  const todayRain =
    dash.predictive.outlook_days?.[0]?.precip_mm ??
    dash.descriptive.series.precip_daily?.[0]?.value ??
    sky.precip_1h_mm ??
    null;
  const probs = (dash.predictive.precip_probability_pct || []).slice(0, 3);

  return (
    <div className="space-y-3">
      <div className="grid gap-3 lg:grid-cols-12">
        <section className="neo sky-card relative overflow-hidden p-5 lg:col-span-6">
          <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-neo-accent">{t.sky}</p>
          <div className="mt-3 flex items-center gap-4">
            <SkyGlyph kind={sky.kind || dash.descriptive.current.sky_kind || "cloud"} day={sky.is_day !== false} />
            <div className="min-w-0">
              <p className="text-2xl font-extrabold leading-tight">{sky.label || dash.descriptive.current.sky_label || "—"}</p>
              <p className="mt-1 font-mono text-3xl font-bold text-neo-accent">
                {sky.temp_c != null ? `${Number(sky.temp_c).toFixed(1)}°C` : "—"}
              </p>
              <p className="mt-1 text-xs text-neo-muted">
                {sky.is_day ? t.day : t.night}
                {sky.place ? ` · ${sky.place}` : ""}
              </p>
            </div>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
            <Stat k={t.cloud} v={sky.cloud_cover_pct != null ? `${Math.round(Number(sky.cloud_cover_pct))}%` : "—"} />
            <Stat k={t.visibility} v={sky.visibility_km != null ? `${sky.visibility_km} km` : "—"} />
            <Stat k={t.humidity} v={sky.humidity_pct != null ? `${Math.round(Number(sky.humidity_pct))}%` : "—"} />
            <Stat k={t.lastHourRain} v={sky.precip_1h_mm != null ? `${sky.precip_1h_mm} mm` : "—"} />
          </div>
        </section>

        <section className="neo p-5 lg:col-span-6">
          <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-neo-accent">{t.rainToday}</p>
          <p className="mt-3 font-mono text-4xl font-extrabold text-neo-accent">
            {todayRain != null ? `${Number(todayRain).toFixed(1)}` : "—"}
            <span className="ml-1 text-base font-medium text-neo-muted">mm</span>
          </p>
          <p className="mt-1 text-xs text-neo-muted">{t.predictive}</p>
          <div className="mt-4 grid grid-cols-2 gap-3">
            <Stat k={t.rain3} v={`${dash.predictive.precip_next_3d_mm} mm`} />
            <Stat k={t.rain7} v={`${dash.predictive.precip_7d_mm ?? "—"} mm`} />
            <Stat
              k="P(rain)"
              v={probs.length ? probs.map((p) => `${p}%`).join(" · ") : "—"}
            />
            <Stat k={t.balance} v={`${dash.predictive.water_balance_7d_mm ?? "—"} mm`} />
          </div>
        </section>
      </div>

      <section className="neo p-4">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-neo-accent">{t.windProfile}</p>
          <p className="text-sm text-neo-muted">
            {t.fromWind} <strong>{wind.compass || "—"}</strong>
            {wind.direction_deg != null ? ` (${Math.round(Number(wind.direction_deg))}°)` : ""}
            <span className="mx-1.5">·</span>
            {t.flowToward} <strong>{wind.flow_compass || "—"}</strong>
          </p>
        </div>
        <div className="mt-2 flex flex-wrap items-center gap-5">
          <WindRose
            fromDeg={wind.direction_deg ?? null}
            flowDeg={wind.flow_deg ?? null}
            rose={rose}
            compass={wind.compass || "—"}
            flow={wind.flow_compass || "—"}
          />
          <div className="min-w-[180px] flex-1">
            <p className="font-mono text-3xl font-bold text-neo-accent">
              {wind.speed_kmh != null ? `${Number(wind.speed_kmh).toFixed(1)}` : "—"}
              <span className="ml-1 text-sm font-medium text-neo-muted">km/h</span>
            </p>
            <div className="mt-2 flex flex-wrap gap-1">
              {(wind.hourly || []).slice(0, 18).map((h) => (
                <span
                  key={h.t}
                  className="flex h-7 w-4 items-center justify-center text-neo-accent"
                  title={`${hhmm(h.t)} ${h.compass} ${h.speed} km/h → ${h.flow}`}
                >
                  <span className="inline-block text-xs" style={{ transform: `rotate(${h.dir + 180}deg)` }}>
                    ↑
                  </span>
                </span>
              ))}
            </div>
            <div className="mt-3 grid grid-cols-8 gap-1 sm:grid-cols-16">
              {rose.map((b) => (
                <div key={b.dir} className="flex flex-col items-center gap-0.5">
                  <div className="flex h-10 w-full items-end justify-center">
                    <div
                      className="w-1.5 rounded-full bg-neo-rain/80"
                      style={{ height: `${Math.max(6, (b.count / maxRose) * 40)}px` }}
                    />
                  </div>
                  <span className="text-[8px] text-neo-muted">{b.dir}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export function OverviewPlots({ dash, locale }: { dash: DashboardSnapshot; locale: Locale }) {
  const t = COPY[locale];
  const live = dash.live;
  const series = dash.descriptive.series;
  const rain = (series.precip_hourly || []).slice(0, 24).map((p) => ({ t: hhmm(p.t), v: p.value }));
  const temp = (series.temp_hourly || []).slice(0, 24).map((p) => ({ t: hhmm(p.t), v: p.value }));
  const wspd = (series.wind_hourly || []).slice(0, 24).map((p) => ({ t: hhmm(p.t), v: p.value }));
  const aqi = (series.aqi_hourly || []).slice(0, 24).map((p) => ({ t: hhmm(p.t), v: p.value }));
  const aqiHist = (series.aqi_history || []).slice(-24).map((p) => ({ t: hhmm(p.t), v: p.value }));
  const wave = (series.wave_hourly || []).slice(0, 24).map((p) => ({ t: hhmm(p.t), v: p.value }));
  const discharge = (live?.flood?.discharge || dash.predictive.river_discharge || []).map((v, i) => ({
    t: `d+${i}`,
    v,
  }));
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
      <Spark title={`${t.predictive} · 24h rain`} data={rain} color="#3a7ca5" unit="mm" kind="bar" />
      <Spark title="24h temperature" data={temp} color="#c47b17" unit="°C" />
      <Spark title={t.windSpeed} data={wspd} color="#146b7a" unit="km/h" />
      <Spark title={t.discharge} data={discharge} color="#1d4e89" unit="m³/s" />
      <Spark title={t.omAqi} data={aqi} color="#2d6a4f" unit="US AQI" />
      <Spark title={t.histAqi} data={aqiHist.length ? aqiHist : aqi} color="#2d6a4f" unit={aqiHist.length ? "µg/m³" : "US AQI"} />
      <Spark
        title={live?.marine?.nearest_coast ? `${t.waves} · ${live.marine.nearest_coast}` : t.waves}
        data={wave}
        color="#4aa3b5"
        unit="m"
      />
    </div>
  );
}

function Stat({ k, v }: { k: string; v: string }) {
  return (
    <div>
      <p className="text-[10px] uppercase tracking-widest text-neo-muted">{k}</p>
      <p className="font-mono text-lg font-semibold">{v}</p>
    </div>
  );
}

function Spark({
  title,
  data,
  color,
  unit,
  kind = "area",
}: {
  title: string;
  data: { t: string; v: number }[];
  color: string;
  unit: string;
  kind?: "area" | "bar";
}) {
  return (
    <section className="neo p-3">
      <div className="mb-1 flex items-baseline justify-between">
        <h3 className="text-[11px] font-bold uppercase tracking-[0.14em] text-neo-accent">{title}</h3>
        <span className="text-[10px] text-neo-muted">{unit}</span>
      </div>
      <div className="h-32">
        {data.length === 0 ? (
          <p className="flex h-full items-center justify-center text-xs text-neo-muted">—</p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            {kind === "bar" ? (
              <BarChart data={data}>
                <CartesianGrid stroke="#d5dde6" vertical={false} />
                <XAxis dataKey="t" stroke="#6b7c93" fontSize={9} interval={3} />
                <YAxis stroke="#6b7c93" fontSize={9} width={28} />
                <Tooltip contentStyle={tip} />
                <Bar dataKey="v" fill={color} radius={[4, 4, 0, 0]} />
              </BarChart>
            ) : (
              <AreaChart data={data}>
                <CartesianGrid stroke="#d5dde6" vertical={false} />
                <XAxis dataKey="t" stroke="#6b7c93" fontSize={9} interval={3} />
                <YAxis stroke="#6b7c93" fontSize={9} width={28} />
                <Tooltip contentStyle={tip} />
                <Area type="monotone" dataKey="v" stroke={color} fill={color} fillOpacity={0.18} strokeWidth={2} />
              </AreaChart>
            )}
          </ResponsiveContainer>
        )}
      </div>
    </section>
  );
}

function WindRose({
  fromDeg,
  flowDeg,
  rose,
  compass,
  flow,
}: {
  fromDeg: number | null;
  flowDeg: number | null;
  rose: { dir: string; count: number; avg_speed: number }[];
  compass: string;
  flow: string;
}) {
  const max = Math.max(1, ...rose.map((r) => r.count));
  return (
    <svg viewBox="0 0 200 200" className="h-36 w-36 shrink-0">
      <circle cx="100" cy="100" r="86" fill="#e7f1ef" stroke="#c5d5d2" />
      <circle cx="100" cy="100" r="58" fill="none" stroke="#c5d5d2" strokeDasharray="3 4" />
      {["N", "E", "S", "W"].map((lab, i) => {
        const ang = (i * 90 - 90) * (Math.PI / 180);
        const x = 100 + Math.cos(ang) * 74;
        const y = 100 + Math.sin(ang) * 74;
        return (
          <text key={lab} x={x} y={y} textAnchor="middle" dominantBaseline="middle" fontSize="10" fill="#4d6b70">
            {lab}
          </text>
        );
      })}
      {rose.map((b, i) => {
        const ang = i * 22.5;
        const len = 12 + (b.count / max) * 28;
        return (
          <line
            key={b.dir}
            x1="100"
            y1="100"
            x2="100"
            y2={100 - len}
            stroke="#4aa3b5"
            strokeWidth={b.count ? 4 : 1}
            strokeLinecap="round"
            opacity={b.count ? 0.55 : 0.15}
            transform={`rotate(${ang} 100 100)`}
          />
        );
      })}
      {fromDeg != null ? (
        <g transform={`rotate(${fromDeg} 100 100)`}>
          <polygon points="100,22 108,70 100,62 92,70" fill="#c17f2a" />
        </g>
      ) : null}
      {flowDeg != null ? (
        <g transform={`rotate(${flowDeg} 100 100)`}>
          <polygon points="100,34 106,78 100,72 94,78" fill="#146b7a" />
        </g>
      ) : null}
      <circle cx="100" cy="100" r="18" fill="#eef6f4" stroke="#c5d5d2" />
      <text x="100" y="98" textAnchor="middle" fontSize="9" fill="#146b7a" fontWeight="700">
        {compass}
      </text>
      <text x="100" y="110" textAnchor="middle" fontSize="8" fill="#4d6b70">
        →{flow}
      </text>
    </svg>
  );
}

function SkyGlyph({ kind, day }: { kind: string; day: boolean }) {
  const sun = day ? "#e9b44c" : "#c9d4de";
  return (
    <svg viewBox="0 0 88 88" className={`h-24 w-24 shrink-0 sky-glyph sky-${kind}`}>
      {kind === "clear" || kind === "partly" ? (
        <g className={day ? "sky-sun" : ""}>
          <circle cx={kind === "partly" ? 30 : 44} cy={kind === "partly" ? 30 : 40} r="14" fill={sun} />
          {day
            ? [0, 45, 90, 135, 180, 225, 270, 315].map((a) => (
                <line
                  key={a}
                  x1={kind === "partly" ? 30 : 44}
                  y1={kind === "partly" ? 30 : 40}
                  x2={kind === "partly" ? 30 : 44}
                  y2={kind === "partly" ? 8 : 16}
                  stroke={sun}
                  strokeWidth="2"
                  transform={`rotate(${a} ${kind === "partly" ? 30 : 44} ${kind === "partly" ? 30 : 40})`}
                />
              ))
            : null}
        </g>
      ) : null}
      {kind !== "clear" ? (
        <g className="sky-cloud">
          <ellipse cx="40" cy="50" rx="22" ry="14" fill="#d7e4ea" />
          <ellipse cx="56" cy="52" rx="16" ry="12" fill="#c9d8e0" />
          <ellipse cx="28" cy="54" rx="14" ry="10" fill="#e4eef2" />
        </g>
      ) : null}
      {kind === "rain" || kind === "storm" ? (
        <g className="sky-drops">
          <line x1="32" y1="66" x2="28" y2="80" stroke="#3a7ca5" strokeWidth="2" />
          <line x1="44" y1="68" x2="40" y2="82" stroke="#3a7ca5" strokeWidth="2" />
          <line x1="56" y1="66" x2="52" y2="80" stroke="#3a7ca5" strokeWidth="2" />
        </g>
      ) : null}
      {kind === "storm" ? <polygon points="48,48 40,64 46,64 38,78 58,60 50,60 56,48" fill="#c17f2a" /> : null}
      {kind === "fog" ? (
        <g>
          <line x1="18" y1="62" x2="70" y2="62" stroke="#9bb0b6" strokeWidth="3" />
          <line x1="22" y1="70" x2="66" y2="70" stroke="#b7c9ce" strokeWidth="3" />
          <line x1="20" y1="78" x2="68" y2="78" stroke="#9bb0b6" strokeWidth="3" />
        </g>
      ) : null}
    </svg>
  );
}
