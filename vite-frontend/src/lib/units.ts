import type { UnitSys } from "@/types/dashboard";

export function rain(mm: number | null | undefined, u: UnitSys): string {
  if (mm == null || Number.isNaN(Number(mm))) return "—";
  const n = Number(mm);
  return u === "imperial" ? `${(n / 25.4).toFixed(2)} in` : `${n.toFixed(1)} mm`;
}

export function temp(c: number | null | undefined, u: UnitSys): string {
  if (c == null || Number.isNaN(Number(c))) return "—";
  const n = Number(c);
  return u === "imperial" ? `${((n * 9) / 5 + 32).toFixed(0)} °F` : `${n.toFixed(1)} °C`;
}

export function speed(kmh: number | null | undefined, u: UnitSys): string {
  if (kmh == null || Number.isNaN(Number(kmh))) return "—";
  const n = Number(kmh);
  return u === "imperial" ? `${(n * 0.621).toFixed(0)} mph` : `${n.toFixed(1)} km/h`;
}

export function dist(km: number | null | undefined, u: UnitSys): string {
  if (km == null || Number.isNaN(Number(km))) return "—";
  const n = Number(km);
  return u === "imperial" ? `${(n * 0.621).toFixed(1)} mi` : `${n.toFixed(1)} km`;
}

export function height(m: number | null | undefined, u: UnitSys): string {
  if (m == null || Number.isNaN(Number(m))) return "—";
  const n = Number(m);
  return u === "imperial" ? `${(n * 3.281).toFixed(1)} ft` : `${n.toFixed(1)} m`;
}

export function rainUnit(u: UnitSys) {
  return u === "imperial" ? "in" : "mm";
}
export function tempUnit(u: UnitSys) {
  return u === "imperial" ? "°F" : "°C";
}
