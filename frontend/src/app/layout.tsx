import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RainFall — India environmental intelligence",
  description: "Proactive environmental dashboard for Indian districts",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
