import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "GuardRail AI",
  description: "AI-powered API security testing and self-healing platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-zinc-950 text-zinc-50 min-h-screen`}>
        <nav className="border-b border-zinc-800 bg-zinc-900/50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center">
                <a href="/" className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center font-bold text-white">GR</div>
                  <span className="font-semibold text-lg">GuardRail AI</span>
                </a>
                <div className="hidden md:block ml-10">
                  <div className="flex items-baseline space-x-4">
                    <a href="/" className="hover:bg-zinc-800 px-3 py-2 rounded-md text-sm font-medium">Dashboard</a>
                    <a href="/scans" className="hover:bg-zinc-800 px-3 py-2 rounded-md text-sm font-medium">Scans</a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
