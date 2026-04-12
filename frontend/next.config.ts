import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        // Cache /money page at Vercel's CDN edge (per unique URL including query string).
        // s-maxage=300: CDN serves cached HTML for 5 min before revalidating.
        // stale-while-revalidate=600: CDN continues serving stale while fetching fresh in background.
        // This prevents every request from hitting the serverless function.
        source: "/money",
        headers: [
          {
            key: "Cache-Control",
            value: "public, s-maxage=300, stale-while-revalidate=600",
          },
        ],
      },
    ];
  },
};

export default withNextIntl(nextConfig);
