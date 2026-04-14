import type { Metadata } from "next";

const DEFAULT_SITE_URL = "https://data.abdulqadirmsingi.com";
const DEFAULT_TITLE = "AQ";
const TITLE_TEMPLATE = "%s | AQ";
const DEFAULT_DESCRIPTION =
  "AQ is a multi-sector data intelligence hub for Tanzania, combining historical records, current signals, and actionable insight.";
const DEFAULT_KEYWORDS = [
  "AQ",
  "AQ Data Lab",
  "AQ Data",
  "AQ Data Dashboard",
  "AQ Data Intelligence",
  "AQ Data Intelligence Hub",
  "AQ Data Intelligence Workspace",
  "AQ Data Intelligence Workspace",
  "Tanzania data",
  "historical data",
  "data intelligence",
  "economic data",
  "fuel prices",
  "exchange rates",
  "EWURA",
  "Bank of Tanzania",
  "CRDB",
  "NMB",
  "market intelligence",
];

type QueryParams = Record<string, string | string[] | undefined>;

interface BuildMetadataOptions {
  title: string;
  description?: string;
  path?: string;
  query?: QueryParams;
  imageTitle?: string;
  imageDetail?: string;
  keywords?: string[];
}

export function getSiteUrl(): string {
  return (process.env.NEXT_PUBLIC_SITE_URL?.trim() || DEFAULT_SITE_URL).replace(/\/$/, "");
}

export function getBaseMetadata(): Metadata {
  const siteUrl = getSiteUrl();
  const defaultImage = buildOgImageUrl();

  return {
    metadataBase: new URL(siteUrl),
    applicationName: DEFAULT_TITLE,
    title: {
      default: `${DEFAULT_TITLE} | Data Intelligence Hub`,
      template: TITLE_TEMPLATE,
    },
    description: DEFAULT_DESCRIPTION,
    keywords: DEFAULT_KEYWORDS,
    referrer: "origin-when-cross-origin",
    category: "data analytics",
    alternates: {
      canonical: "/",
    },
    openGraph: {
      type: "website",
      siteName: DEFAULT_TITLE,
      title: `${DEFAULT_TITLE} | Data Intelligence Hub`,
      description: DEFAULT_DESCRIPTION,
      url: siteUrl,
      images: [
        {
          url: defaultImage,
          width: 1200,
          height: 630,
          alt: "AQ social preview",
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title: `${DEFAULT_TITLE} | Data Intelligence Hub`,
      description: DEFAULT_DESCRIPTION,
      images: [defaultImage],
    },
    robots: {
      index: true,
      follow: true,
      googleBot: {
        index: true,
        follow: true,
        "max-image-preview": "large",
        "max-snippet": -1,
        "max-video-preview": -1,
      },
    },
    other: {
      "theme-color": "#10273c",
    },
    icons: {
      icon: "/images/aq-logo.png",
      shortcut: "/images/aq-logo.png",
      apple: "/images/aq-logo.png",
    },
    formatDetection: {
      telephone: false,
      address: false,
      email: false,
    },
  };
}

export function buildPageMetadata({
  title,
  description = DEFAULT_DESCRIPTION,
  path = "/",
  query,
  imageTitle,
  imageDetail,
  keywords = [],
}: BuildMetadataOptions): Metadata {
  const canonicalPath = buildCanonicalPath(path, query);
  const ogImageUrl = buildOgImageUrl({
    title: imageTitle ?? title,
    detail: imageDetail,
  });

  return {
    title,
    description,
    keywords: [...DEFAULT_KEYWORDS, ...keywords],
    alternates: {
      canonical: canonicalPath,
    },
    openGraph: {
      title: `${title} | AQ`,
      description,
      url: canonicalPath,
      images: [
        {
          url: ogImageUrl,
          width: 1200,
          height: 630,
          alt: `${title} social preview`,
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title: `${title} | AQ`,
      description,
      images: [ogImageUrl],
    },
  };
}

export function readQueryValue(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

function buildCanonicalPath(path: string, query?: QueryParams): string {
  if (!query) {
    return path;
  }

  const params = new URLSearchParams();

  Object.entries(query).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach((entry) => {
        if (entry) {
          params.append(key, entry);
        }
      });
      return;
    }

    if (value) {
      params.set(key, value);
    }
  });

  const serialized = params.toString();
  return serialized ? `${path}?${serialized}` : path;
}

function buildOgImageUrl(input?: { title?: string; detail?: string }): string {
  const siteUrl = getSiteUrl();
  const url = new URL("/api/og", siteUrl);

  if (input?.title) {
    url.searchParams.set("title", input.title);
  }

  if (input?.detail) {
    url.searchParams.set("detail", input.detail);
  }

  return url.toString();
}
