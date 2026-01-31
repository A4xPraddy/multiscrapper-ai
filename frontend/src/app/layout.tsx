import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const outfit = Outfit({ subsets: ["latin"], variable: "--font-outfit" });

export const metadata: Metadata = {
  title: "MultiScrapper AI | by Prasad",
  description: "Secure Content Intelligence & Web Analysis Portal",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} ${outfit.variable} font-sans antialiased bg-[#0a0a0a] text-[#fcfcfc]`}>
        <div className="min-h-screen">
          {children}
        </div>
      </body>
    </html>
  );
}
