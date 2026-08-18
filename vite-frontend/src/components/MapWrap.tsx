import React, { Suspense } from "react";
import type { Location } from "@/types/dashboard";

const MapView = React.lazy(() => import("./MapView").then((m) => ({ default: m.MapView })));

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
  return (
    <Suspense fallback={<div className="h-full w-full bg-neo-bg animate-pulse rounded-organ" />}>
      <MapView {...props} />
    </Suspense>
  );
}
