"use client";

import { useMemo, useState } from "react";
import { COPY, type Locale } from "@/i18n/copy";
import type { DashboardSnapshot, Location } from "@/types/dashboard";
import { MapWrap } from "./MapWrap";

const LAYERS = ["positron", "streets", "satellite", "terrain"] as const;

export function SquareMap({
  dash,
  locale,
  onPick,
}: {
  dash: DashboardSnapshot;
  locale: Locale;
  onPick: (l: Location) => void;
}) {
  const t = COPY[locale];
  const [basemap, setBasemap] = useState<string>("positron");
  const [zoom, setZoom] = useState(dash.map.zoom || 8);
  const [overlays, setOverlays] = useState<string[]>([]);
  const nearby = dash.ogd?.nearby || [];
  const rain = dash.predictive.precip_next_3d_mm;
  const box = useMemo(
    () => (
      <MapWrap
        lat={dash.location.lat}
        lon={dash.location.lon}
        label={dash.location.label}
        rainMm={rain}
        zoom={zoom}
        basemap={basemap}
        nearby={nearby}
        overlays={overlays}
        onPick={onPick}
      />
    ),
    [dash.location, rain, zoom, basemap, nearby, overlays, onPick]
  );

  function toggleOverlay(id: string) {
    setOverlays((cur) => (cur.includes(id) ? cur.filter((x) => x !== id) : [...cur, id]));
  }

  function locate() {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition((pos) => {
      onPick({
        ...dash.location,
        lat: pos.coords.latitude,
        lon: pos.coords.longitude,
        label: "My location",
        id: "geo",
      });
    });
  }

  return (
    <div className="grid gap-4 lg:grid-cols-[minmax(0,520px)_1fr]">
      <div className="neo p-3">
        <div className="aspect-square w-full overflow-hidden rounded-[18px]">{box}</div>
      </div>
      <div className="space-y-3">
        <section className="neo p-4">
          <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-neo-muted">{t.layers}</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {LAYERS.map((id) => (
              <button
                key={id}
                className={`neo-btn ${basemap === id ? "neo-btn-on" : ""}`}
                onClick={() => setBasemap(id)}
              >
                {id}
              </button>
            ))}
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <button className="neo-btn" onClick={() => setZoom((z) => Math.min(14, z + 1))}>
              +
            </button>
            <button className="neo-btn" onClick={() => setZoom((z) => Math.max(5, z - 1))}>
              −
            </button>
            <button className="neo-btn" onClick={() => setZoom(8)}>
              {t.reset}
            </button>
            <button className="neo-btn" onClick={locate}>
              {t.locate}
            </button>
          </div>
          <p className="mt-3 font-mono text-xs text-neo-muted">
            {dash.location.lat.toFixed(4)}, {dash.location.lon.toFixed(4)} · z{zoom}
          </p>
          <p className="mt-3 text-[11px] font-bold uppercase tracking-[0.16em] text-neo-muted">{t.bhuvan}</p>
          <div className="mt-2 flex flex-wrap gap-2">
            <button
              className={`neo-btn ${overlays.includes("bhuvan_geomorph") ? "neo-btn-on" : ""}`}
              onClick={() => toggleOverlay("bhuvan_geomorph")}
            >
              WB 50k
            </button>
            <button
              className={`neo-btn ${overlays.includes("bhuvan_geomorph_in") ? "neo-btn-on" : ""}`}
              onClick={() => toggleOverlay("bhuvan_geomorph_in")}
            >
              India
            </button>
          </div>
          <div className="mt-2 flex flex-col gap-1 text-xs">
            <a
              className="text-neo-accent underline"
              href="https://bhuvan.nrsc.gov.in/ngmaps/thematic?theme1=geomorphology.wb_gm50k_0506_new&tlp=vector&state=WEST+BENGAL&district=ALL#6.28/24.412/87.858"
              target="_blank"
              rel="noreferrer"
            >
              {t.bhuvan} (Bhuvan)
            </a>
            <a
              className="text-neo-accent underline"
              href="https://www.nrsc.gov.in/nrscnew/Dataproducts_Thematic_overview.php"
              target="_blank"
              rel="noreferrer"
            >
              {t.nrsc}
            </a>
          </div>
        </section>
        <section className="neo p-4">
          <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-neo-muted">{t.nearby}</p>
          <ul className="mt-2 space-y-1">
            {nearby.map((n) => (
              <li key={n.id}>
                <button className="text-sm hover:text-neo-accent" onClick={() => onPick(n)}>
                  {n.label}
                </button>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}
