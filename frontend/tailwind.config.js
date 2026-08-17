/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        neo: {
          bg: "#e7f1ef",
          card: "#eef6f4",
          text: "#14323a",
          muted: "#4d6b70",
          accent: "#146b7a",
          accent2: "#2d6a4f",
          warn: "#c17f2a",
          danger: "#b42318",
          flood: "#1d4e89",
          ink: "#14323a",
          rain: "#4aa3b5",
        },
      },
      fontFamily: {
        sans: ["Manrope", "Segoe UI", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "monospace"],
      },
      boxShadow: {
        neo: "8px 8px 18px #c5d5d2, -8px -8px 18px #ffffff",
        "neo-sm": "5px 5px 10px #c5d5d2, -5px -5px 10px #ffffff",
        "neo-in": "inset 5px 5px 10px #c5d5d2, inset -5px -5px 10px #ffffff",
        "neo-in-sm": "inset 3px 3px 6px #c5d5d2, inset -3px -3px 6px #ffffff",
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
