import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Rituchakra — weather and farm advice for India",
  description: "Live rain, flood, air, mandi prices and what to do today — in English, Hindi and Bengali.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-theme="sand">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
