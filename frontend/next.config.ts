import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

const PAGE_CACHE = "public, s-maxage=43200, stale-while-revalidate=604800";

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        // Cache all data pages at Vercel's CDN edge per unique URL (including query string).
        // s-maxage=3600: CDN serves cached HTML for 1 hour before revalidating.
        // stale-while-revalidate=86400: CDN continues serving stale for up to 24h while fetching fresh.
        source: "/(data|energy|money|dse)(.*)",
        headers: [{ key: "Cache-Control", value: PAGE_CACHE }],
      },
      {
        // OG images are expensive edge renders — cache them for 24h at CDN and browser.
        source: "/api/og(.*)",
        headers: [
          { key: "Cache-Control", value: "public, max-age=604800, s-maxage=604800, stale-while-revalidate=2592000" },
        ],
      },
    ];
  },
};

export default withNextIntl(nextConfig);
