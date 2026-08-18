/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        neo: {
          bg: "var(--bg)",
          card: "var(--card)",
          text: "var(--text)",
          muted: "var(--muted)",
          accent: "var(--accent)",
          accent2: "var(--accent2)",
          warn: "var(--warn)",
          danger: "var(--danger)",
          flood: "var(--flood)",
          ink: "var(--text)",
          rain: "var(--rain)",
          gold: "var(--gold)",
          indigo: "var(--indigo)",
          line: "var(--line)",
        },
      },
      fontFamily: {
        sans: ["Manrope", "Segoe UI", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "monospace"],
      },
      boxShadow: {
        neo: "8px 10px 22px rgba(68, 48, 28, 0.10), -6px -6px 16px rgba(255, 255, 255, 0.85)",
        "neo-sm": "4px 6px 14px rgba(68, 48, 28, 0.10)",
        "neo-in": "inset 4px 4px 10px rgba(68, 48, 28, 0.08), inset -3px -3px 8px rgba(255,255,255,0.8)",
        "neo-in-sm": "inset 2px 2px 6px rgba(68, 48, 28, 0.08)",
      },
      borderRadius: {
        organ: "1.75rem",
      },
      gridTemplateColumns: {
        16: "repeat(16, minmax(0, 1fr))",
      },
    },
  },
  plugins: [],
};
