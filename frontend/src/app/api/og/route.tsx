import { ImageResponse } from "next/og";

import { getSiteUrl } from "@/lib/seo";

export const runtime = "edge";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const title = searchParams.get("title") || "AQ";
  const detail =
    searchParams.get("detail")
    || "Historical records, current signals, and decision-ready intelligence for Tanzania";
  const logoUrl = new URL("/images/aq-logo.jpg", getSiteUrl()).toString();

  return new ImageResponse(
    (
      <div
        style={{
          display: "flex",
          width: "100%",
          height: "100%",
          background:
            "linear-gradient(135deg, rgb(14, 23, 36) 0%, rgb(16, 39, 60) 45%, rgb(226, 160, 47) 100%)",
          color: "white",
          padding: "56px",
          fontFamily: "sans-serif",
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            width: "100%",
            height: "100%",
            border: "1px solid rgba(255,255,255,0.18)",
            borderRadius: "28px",
            padding: "42px",
            background: "rgba(7, 14, 22, 0.34)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "20px",
              }}
            >
              <img
                src={logoUrl}
                width={88}
                height={88}
                alt="AQ logo"
                style={{
                  borderRadius: "20px",
                  objectFit: "cover",
                  border: "2px solid rgba(255,255,255,0.28)",
                }}
              />
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "6px",
                }}
              >
                <span style={{ fontSize: 22, opacity: 0.78 }}>AQ Data Intelligence Hub</span>
                <span style={{ fontSize: 16, letterSpacing: "0.18em", textTransform: "uppercase", opacity: 0.6 }}>
                  Official Data Snapshot
                </span>
              </div>
            </div>
            <div
              style={{
                display: "flex",
                padding: "12px 18px",
                borderRadius: "999px",
                background: "rgba(255,255,255,0.12)",
                fontSize: 18,
              }}
            >
              data.abdulqadirmsingi.com
            </div>
          </div>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "24px",
              maxWidth: "78%",
            }}
          >
            <div style={{ fontSize: 68, lineHeight: 1.02, fontWeight: 700 }}>{title}</div>
            <div style={{ fontSize: 28, lineHeight: 1.35, opacity: 0.82 }}>{detail}</div>
          </div>

          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              fontSize: 20,
              opacity: 0.78,
            }}
          >
            <span>Historical records. Current signals. Multi-sector intelligence.</span>
            <span>Built for decision-ready public intelligence.</span>
          </div>
        </div>
      </div>
    ),
    {
      width: 1200,
      height: 630,
    },
  );
}
