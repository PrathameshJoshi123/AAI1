import {
  QuoteItem,
  QuoteCreatePayload,
  QuoteRecalculatePayload,
} from "@/types/quote";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return (
      localStorage.getItem("auth_token") ||
      localStorage.getItem("token") ||
      localStorage.getItem("access_token") ||
      sessionStorage.getItem("auth_token") ||
      null
    );
  } catch {
    return null;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  const response = await fetch(url, { ...options, headers });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || `Request failed with status ${response.status}`);
  }

  const json = await response.json();
  return json.data !== undefined ? json.data : json;
}

export const QuoteAPI = {
  async listQuotes(): Promise<QuoteItem[]> {
    return request<QuoteItem[]>("/api/v1/quotes");
  },

  async getQuote(identifier: string): Promise<QuoteItem> {
    return request<QuoteItem>(`/api/v1/quotes/${identifier}`);
  },

  async createQuote(payload: QuoteCreatePayload): Promise<QuoteItem> {
    return request<QuoteItem>("/api/v1/quotes/calculate", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async recalculateQuote(quoteId: string, payload: QuoteRecalculatePayload): Promise<QuoteItem> {
    return request<QuoteItem>(`/api/v1/quotes/${quoteId}/recalculate`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};

