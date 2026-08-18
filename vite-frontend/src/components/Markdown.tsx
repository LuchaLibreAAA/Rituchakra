"use client";

import type { ReactNode } from "react";

function inline(text: string): ReactNode[] {
  const parts: ReactNode[] = [];
  const re = /(\*\*[^*]+\*\*|__[^_]+__|\*[^*\n]+\*|`[^`]+`|\[[^\]]+\]\([^)]+\))/g;
  let last = 0;
  let m: RegExpExecArray | null;
  let i = 0;
  while ((m = re.exec(text))) {
    if (m.index > last) parts.push(text.slice(last, m.index));
    const tok = m[0];
    if (tok.startsWith("**") || tok.startsWith("__")) {
      parts.push(
        <strong key={`b${i++}`} className="font-semibold text-neo-ink">
          {tok.slice(2, -2)}
        </strong>
      );
    } else if (tok.startsWith("`")) {
      parts.push(
        <code key={`c${i++}`} className="rounded-md bg-neo-bg px-1 font-mono text-[12px]">
          {tok.slice(1, -1)}
        </code>
      );
    } else if (tok.startsWith("[")) {
      const lm = tok.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
      if (lm) {
        parts.push(
          <a key={`a${i++}`} href={lm[2]} className="text-neo-accent underline" target="_blank" rel="noreferrer">
            {lm[1]}
          </a>
        );
      } else parts.push(tok);
    } else {
      parts.push(
        <em key={`i${i++}`} className="italic">
          {tok.slice(1, -1)}
        </em>
      );
    }
    last = m.index + tok.length;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}

export function Markdown({ text }: { text: string }) {
  const lines = (text || "").replace(/\r\n/g, "\n").split("\n");
  const nodes: ReactNode[] = [];
  let list: { kind: "ul" | "ol"; items: string[] } | null = null;
  let i = 0;

  function flush() {
    if (!list) return;
    const items = list.items;
    const kind = list.kind;
    list = null;
    if (kind === "ul") {
      nodes.push(
        <ul key={`ul${i++}`} className="my-1.5 list-disc space-y-0.5 pl-5">
          {items.map((it, k) => (
            <li key={k}>{inline(it)}</li>
          ))}
        </ul>
      );
    } else {
      nodes.push(
        <ol key={`ol${i++}`} className="my-1.5 list-decimal space-y-0.5 pl-5">
          {items.map((it, k) => (
            <li key={k}>{inline(it)}</li>
          ))}
        </ol>
      );
    }
  }

  for (const raw of lines) {
    const line = raw.replace(/\s+$/, "");
    const ul = line.match(/^\s*[-*]\s+(.+)$/);
    const ol = line.match(/^\s*\d+\.\s+(.+)$/);
    if (ul) {
      if (!list || list.kind !== "ul") {
        flush();
        list = { kind: "ul", items: [] };
      }
      list.items.push(ul[1]);
      continue;
    }
    if (ol) {
      if (!list || list.kind !== "ol") {
        flush();
        list = { kind: "ol", items: [] };
      }
      list.items.push(ol[1]);
      continue;
    }
    flush();
    if (!line.trim()) {
      nodes.push(<div key={`sp${i++}`} className="h-2" />);
      continue;
    }
    const h = line.match(/^(#{1,3})\s+(.+)$/);
    if (h) {
      const level = h[1].length;
      const cls =
        level === 1
          ? "mt-2 text-base font-extrabold text-neo-accent"
          : level === 2
            ? "mt-2 text-sm font-bold text-neo-accent"
            : "mt-1.5 text-sm font-semibold";
      nodes.push(
        <p key={`h${i++}`} className={cls}>
          {inline(h[2])}
        </p>
      );
      continue;
    }
    if (/^---+$/.test(line.trim())) {
      nodes.push(<hr key={`hr${i++}`} className="my-2 border-[#cfe0dd]" />);
      continue;
    }
    nodes.push(
      <p key={`p${i++}`} className="leading-relaxed">
        {inline(line)}
      </p>
    );
  }
  flush();
  return <div className="space-y-0.5">{nodes}</div>;
}
