"use client";

import { useEffect, useMemo, useState } from "react";
import { COPY, type Locale } from "@/i18n/copy";
import { presetsFor } from "@/i18n/presets";
import { streamChat } from "@/lib/api";
import { useApp } from "@/lib/store";
import type { ChatMsg, DashboardSnapshot } from "@/types/dashboard";
import { Markdown } from "./Markdown";

export function ChatDock({ tall = false }: { tall?: boolean }) {
  const {
    locale,
    outputLocale,
    setOutputLocale,
    location,
    chat,
    addChat,
    replaceLastAssistant,
    clearChat,
    streaming,
    setStreaming,
    applySnapshot,
    setTab,
    pendingAsk,
    setPendingAsk,
  } = useApp();
  const t = COPY[locale];
  const [text, setText] = useState("");
  const [preset, setPreset] = useState("");
  const [showEn, setShowEn] = useState(false);
  const presets = presetsFor(locale);

  useEffect(() => {
    setPreset("");
  }, [locale]);

  useEffect(() => {
    if (!pendingAsk) return;
    setText(pendingAsk);
    setPendingAsk(null);
  }, [pendingAsk, setPendingAsk]);

  const lastUser = useMemo(() => [...chat].reverse().find((m) => m.role === "user"), [chat]);

  async function run(message: string, opts?: { regenerate?: boolean }) {
    if (!message || streaming) return;
    const history = opts?.regenerate
      ? chat.filter((m) => m.role === "user" || m.id !== chat[chat.length - 1]?.id)
      : [...chat];
    if (!opts?.regenerate) {
      addChat({ id: `u-${Date.now()}`, role: "user", content: message, locale });
    }
    setStreaming(true);
    try {
      const final = await streamChat(
        message,
        location,
        locale,
        history,
        (ev) => {
          if (ev.type === "widget_patch" && ev.path === "dashboard" && ev.value) {
            applySnapshot(ev.value as DashboardSnapshot);
          }
          if (ev.type === "widget_patch" && ev.path === "compare") {
            setTab("forecast");
          }
        },
        outputLocale,
        opts?.regenerate
      );
      if (final) {
        if (opts?.regenerate) replaceLastAssistant(final);
        else addChat(final);
      }
    } catch (e) {
      const err: ChatMsg = { id: `e-${Date.now()}`, role: "assistant", content: `Chat failed: ${e}` };
      if (opts?.regenerate) replaceLastAssistant(err);
      else addChat(err);
    } finally {
      setStreaming(false);
    }
  }

  return (
    <aside className={`neo flex flex-col ${tall ? "min-h-[680px]" : "min-h-[420px] h-full"}`}>
      <header className="flex flex-wrap items-center justify-between gap-2 px-4 py-3">
        <div>
          <p className="text-sm font-bold">{t.chat}</p>
          <p className="text-[11px] text-neo-muted">{t.chatHint}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button className="neo-btn text-xs" onClick={() => clearChat()} disabled={streaming || !chat.length}>
            {t.clear}
          </button>
          <button
            className="neo-btn text-xs"
            disabled={streaming || !lastUser}
            onClick={() => lastUser && run(lastUser.content, { regenerate: true })}
          >
            {t.regenerate}
          </button>
        </div>
      </header>
      <div className="mx-3 h-px bg-[#cfe0dd]" />

      <div className="grid gap-2 px-3 py-3 sm:grid-cols-2">
        <label className="text-[11px] text-neo-muted">
          {t.presets}
          <select
            className="neo-in mt-1 w-full px-3 py-2 text-sm"
            value={preset}
            onChange={(e) => {
              const id = e.target.value;
              setPreset(id);
              const hit = presets.find((p) => p.id === id);
              if (hit) setText(hit.text);
            }}
          >
            <option value="">{t.pickPreset}</option>
            {presets.map((p) => (
              <option key={p.id} value={p.id}>
                {p.label}
              </option>
            ))}
          </select>
        </label>
        <label className="text-[11px] text-neo-muted">
          {t.replyIn}
          <div className="mt-1 flex gap-1">
            {(["en", "hi", "bn"] as Locale[]).map((l) => (
              <button
                key={l}
                type="button"
                className={`flex-1 rounded-xl py-2 text-xs font-bold ${
                  outputLocale === l ? "bg-neo-accent text-white" : "neo-btn"
                }`}
                onClick={() => setOutputLocale(l)}
              >
                {l.toUpperCase()}
              </button>
            ))}
          </div>
        </label>
      </div>
      <div className="flex flex-wrap gap-1.5 px-3 pb-2">
        {presets.map((p) => (
          <button
            key={p.id}
            type="button"
            className={`chip ${preset === p.id ? "text-neo-accent" : ""}`}
            onClick={() => {
              setPreset(p.id);
              setText(p.text);
            }}
          >
            {p.label}
          </button>
        ))}
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto px-3 py-2">
        {chat.length === 0 ? (
          <p className="text-xs text-neo-muted">{t.pickPreset}</p>
        ) : null}
        {chat.map((m) => (
          <div
            key={m.id}
            className={`max-w-[95%] rounded-3xl px-3 py-2 text-sm ${
              m.role === "user" ? "ml-auto bg-neo-rain/15 shadow-neo-in-sm" : "shadow-neo-sm"
            }`}
          >
            {m.role === "assistant" ? (
              <Markdown text={m.content} />
            ) : (
              <p className="whitespace-pre-wrap">{m.content}</p>
            )}
            {m.role === "assistant" && m.translation && (m.translation.tgt || "en") !== "en" ? (
              <p className="mt-1.5 text-[10px] uppercase tracking-wide text-neo-muted">
                {t.translated} {(m.translation.inbound?.src || "en").toUpperCase()} → EN →{" "}
                {(m.translation.tgt || "en").toUpperCase()}
                {m.translation.outbound?.engine && m.translation.outbound.engine !== "identity"
                  ? ` · ${m.translation.outbound.engine}`
                  : m.translation.engine
                    ? ` · ${m.translation.engine}`
                    : ""}
              </p>
            ) : null}
            {m.role === "assistant" && m.content_en && showEn ? (
              <div className="mt-2 border-t border-[#cfe0dd] pt-2 text-xs text-neo-muted">
                <Markdown text={m.content_en} />
              </div>
            ) : null}
            {m.tool_trace && m.tool_trace.length > 0 ? (
              <div className="mt-2 flex flex-wrap gap-1">
                {m.tool_trace.map((tr, i) => (
                  <span key={`${tr.name}-${i}`} className="chip">
                    {tr.name.replaceAll("_", " ")} {tr.ms}ms
                  </span>
                ))}
              </div>
            ) : null}
          </div>
        ))}
        {streaming ? <p className="text-xs text-neo-accent">…</p> : null}
      </div>

      <div className="p-3">
        <label className="mb-2 flex items-center gap-2 text-[11px] text-neo-muted">
          <input type="checkbox" checked={showEn} onChange={(e) => setShowEn(e.target.checked)} />
          {t.showEn}
        </label>
        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            const msg = text.trim();
            setText("");
            run(msg);
          }}
        >
          <input
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="neo-in flex-1 px-3 py-2 text-sm outline-none"
          />
          <button type="submit" disabled={streaming} className="neo-btn disabled:opacity-50">
            {t.send}
          </button>
        </form>
      </div>
    </aside>
  );
}
