import type { Metadata } from "react";
import { Toaster } from "sonner";
import "./globals.css";

export const metadata: Metadata = {
  title: "VidyaMitra — AI Student Tutor | v2.0",
  description: "AI-powered multi-role student tutor platform. Student, Tutor, Principal, Admin portals.",
  keywords: ["AI tutor", "math learning", "multilingual", "Hindi", "Bengali", "NCERT", "CBSE"],
  authors: [{ name: "VidyaMitra" }],
  openGraph: { title: "VidyaMitra — AI Student Tutor", description: "AI-powered student tutor platform.", type: "website" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="theme-color" content="#4F46E5" />
      </head>
      <body className="min-h-screen bg-gray-900 flex items-center justify-center p-2 sm:p-4">
        {/* Mobile App Frame */}
        <div className="app-frame">
          {/* Status Bar */}
          <div className="status-bar">
            <span className="text-[10px] font-medium">9:41</span>
            <span className="text-[10px]">📶 🔋</span>
          </div>
          {/* App Content */}
          <div className="app-content">
            {children}
            <Toaster position="top-center" richColors />
          </div>
        </div>
      </body>
    </html>
  );
}
