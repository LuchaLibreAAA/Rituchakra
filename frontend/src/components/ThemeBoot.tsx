"use client";

import { useEffect } from "react";
import { applyTheme, readSettings, useApp } from "@/lib/store";

export function ThemeBoot() {
  const setSettings = useApp((s) => s.setSettings);
  const setTab = useApp((s) => s.setTab);
  useEffect(() => {
    const s = readSettings();
    setSettings(s);
    applyTheme(s);
    setTab(s.defaultTab);
  }, [setSettings, setTab]);
  return null;
}
