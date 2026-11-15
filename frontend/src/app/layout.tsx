import type { Metadata } from "next";
import { Toaster } from "sonner";
import "./globals.css";

export const metadata: Metadata = {
  title: "PS-21 — Conversational Insurance Platform",
  description:
    "AI-powered conversational insurance acquisition, quotation, and onboarding platform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full bg-white light">
      <head>
        <meta name="color-scheme" content="light" />
      </head>
      <body className="min-h-full bg-white font-sans text-slate-900 antialiased flex flex-col">
        {children}
        <Toaster position="top-right" richColors theme="light" />
      </body>
    </html>
  );
}
