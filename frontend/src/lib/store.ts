import { create } from "zustand";
import type { ChatMsg, DashboardSnapshot, Location, TabId } from "@/types/dashboard";
import type { Locale } from "@/i18n/copy";
import { fetchDashboard } from "./api";

type State = {
  locale: Locale;
  tab: TabId;
  location: Location | null;
  dashboard: DashboardSnapshot | null;
  status: "idle" | "loading" | "ready" | "error";
  error?: string;
  chat: ChatMsg[];
  streaming: boolean;
  outputLocale: Locale;
  sidebarOpen: boolean;
  pendingAsk: string | null;
  setSidebarOpen: (v: boolean) => void;
  setPendingAsk: (q: string | null) => void;
  setLocale: (l: Locale) => void;
  setOutputLocale: (l: Locale) => void;
  setTab: (t: TabId) => void;
  setLocation: (l: Location) => Promise<void>;
  refresh: () => Promise<void>;
  quietRefresh: () => Promise<void>;
  applySnapshot: (d: DashboardSnapshot) => void;
  addChat: (m: ChatMsg) => void;
  replaceLastAssistant: (m: ChatMsg) => void;
  clearChat: () => void;
  setStreaming: (v: boolean) => void;
};

export const useApp = create<State>((set, get) => ({
  locale: "en",
  tab: "overview",
  location: null,
  dashboard: null,
  status: "idle",
  chat: [],
  streaming: false,
  outputLocale: "en",
  sidebarOpen: true,
  pendingAsk: null,
  setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
  setPendingAsk: (pendingAsk) => set({ pendingAsk }),
  setLocale: (locale) => set({ locale, outputLocale: locale }),
  setOutputLocale: (outputLocale) => set({ outputLocale }),
  setTab: (tab) => set({ tab }),
  applySnapshot: (dashboard) =>
    set({ dashboard, location: dashboard.location, status: "ready" }),
  setLocation: async (location) => {
    set({ location, status: "loading" });
    try {
      const dashboard = await fetchDashboard(location);
      set({ dashboard, location: dashboard.location, status: "ready" });
    } catch (e) {
      set({ status: "error", error: String(e) });
    }
  },
  refresh: async () => {
    set({ status: "loading" });
    try {
      const dashboard = await fetchDashboard(get().location || undefined);
      set({ dashboard, location: dashboard.location, status: "ready" });
    } catch (e) {
      set({ status: "error", error: String(e) });
    }
  },
  quietRefresh: async () => {
    try {
      const dashboard = await fetchDashboard(get().location || undefined);
      set({ dashboard, location: dashboard.location, status: "ready" });
    } catch (e) {
      if (!get().dashboard) set({ status: "error", error: String(e) });
    }
  },
  addChat: (m) => set({ chat: [...get().chat, m] }),
  replaceLastAssistant: (m) => {
    const chat = [...get().chat];
    for (let i = chat.length - 1; i >= 0; i--) {
      if (chat[i].role === "assistant") {
        chat[i] = m;
        break;
      }
    }
    set({ chat });
  },
  clearChat: () => set({ chat: [] }),
  setStreaming: (streaming) => set({ streaming }),
}));
