import { API_BASE_URL, API_DEFAULT_REVALIDATE_SECONDS } from "@/lib/constants";

type QueryValue = string | number | boolean | null | undefined;

export interface ApiRequestOptions extends Omit<RequestInit, "body"> {
  query?: Record<string, QueryValue>;
  revalidate?: number | false;
}

export class ApiClientError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly url: string,
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

export function buildApiUrl(path: string, query?: Record<string, QueryValue>): string {
  const normalizedBaseUrl = API_BASE_URL.endsWith("/") ? API_BASE_URL : `${API_BASE_URL}/`;
  const normalizedPath = path.startsWith("/") ? path.slice(1) : path;
  const url = new URL(normalizedPath, normalizedBaseUrl);

  if (!query) {
    return url.toString();
  }

  Object.entries(query).forEach(([key, value]) => {
    if (value === null || value === undefined || value === "") {
      return;
    }

    url.searchParams.set(key, String(value));
  });

  return url.toString();
}

export async function apiFetch<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const { query, revalidate = API_DEFAULT_REVALIDATE_SECONDS, headers, ...init } = options;
  const url = buildApiUrl(path, query);
  const response = await fetch(url, {
    ...init,
    headers: {
      Accept: "application/json",
      ...headers,
    },
    next: revalidate === false ? undefined : { revalidate },
  });

  if (!response.ok) {
    const responseBody = await response.text().catch(() => "");
    throw new ApiClientError(
      `API request failed with status ${response.status}${responseBody ? `: ${responseBody.slice(0, 300)}` : ""}`,
      response.status,
      url,
    );
  }

  return (await response.json()) as T;
}

export async function simulateFetch<T>(data: T): Promise<T> {
  return structuredClone(data);
}
