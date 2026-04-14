import type { Metadata } from "next";
import { Navbar } from "@/components/landing/Navbar";
import { Hero } from "@/components/landing/Hero";
import { DataFeatures } from "@/components/landing/DataFeatures";
import { ComingSoon } from "@/components/landing/ComingSoon";
import { Footer } from "@/components/landing/Footer";

export const metadata: Metadata = {
  title: "AQ Data Lab | Tanzania Intelligence Workspace",
  description: "A multi-sector view of Tanzania&apos;s historical records, current signals, and decision-ready intelligence. Uncover the truth with AQ Data Lab.",
  openGraph: {
    title: "AQ Data Lab | Tanzania Intelligence Workspace",
    description: "A multi-sector view of Tanzania&apos;s historical records, current signals, and decision-ready intelligence.",
    url: "https://abdulqadirmsingi.com",
    siteName: "AQ Data Lab",
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "AQ Data Lab | Tanzania Intelligence Workspace",
    description: "A multi-sector view of Tanzania&apos;s historical records, current signals, and decision-ready intelligence.",
  },
};

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-neutral-50 text-neutral-900 selection:bg-neutral-900 selection:text-white font-sans">
      <Navbar />
      <Hero />
      <DataFeatures />
      <ComingSoon />
      <Footer />
    </main>
  );
}