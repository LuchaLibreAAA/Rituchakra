"use client";

import dynamic from "next/dynamic";
import type { Location } from "@/types/dashboard";

const MapView = dynamic(() => import("./MapView").then((m) => m.MapView), { ssr: false });

export function MapWrap(props: {
  lat: number;
  lon: number;
  label: string;
  rainMm: number;
  zoom: number;
  basemap: string;
  nearby: Location[];
  overlays?: string[];
  onPick: (l: Location) => void;
}) {
  return <MapView {...props} />;
}
