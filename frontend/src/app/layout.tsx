import type { Metadata } from "next";
import { Toaster } from "sonner";
import "./globals.css";

export const metadata: Metadata = {
  title: "GanitMitra — AI Math Tutor | v1.0",
  description:
    "Production-ready AI-powered multilingual math learning companion for Nursery to Class 10. 8 AI agents, 3 languages, voice support.",
  keywords: [
    "math tutor",
    "AI math learning",
    "multilingual math",
    "Hindi math tutor",
    "Bengali math tutor",
    "NCERT math",
    "CBSE math",
    "K-10 math",
    "GanitMitra",
  ],
  authors: [{ name: "GanitMitra" }],
  openGraph: {
    title: "GanitMitra — Your Math Friend",
    description: "AI-powered multilingual math learning companion.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        {children}
        <Toaster position="top-center" richColors />
      </body>
    </html>
  );
}
