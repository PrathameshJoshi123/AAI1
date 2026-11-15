import {
  RecommendationEvaluateResponse,
  RecommendationExplanation,
} from "@/types/recommendation";

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

export const RecommendationAPI = {
  async getRecommendations(category?: string, amount?: number): Promise<RecommendationEvaluateResponse> {
    const params = new URLSearchParams();
    if (category) params.append("category", category);
    if (amount) params.append("amount", amount.toString());
    const query = params.toString();
    const endpoint = query ? `/api/v1/recommendations?${query}` : `/api/v1/recommendations`;
    return request<RecommendationEvaluateResponse>(endpoint);
  },

  async evaluateRecommendations(targetCategory?: string, amount?: number): Promise<RecommendationEvaluateResponse> {
    return request<RecommendationEvaluateResponse>("/api/v1/recommendations/evaluate", {
      method: "POST",
      body: JSON.stringify({ target_category: targetCategory, recommended_sum_assured: amount }),
    });
  },

  async explainRecommendation(recId: string): Promise<RecommendationExplanation> {
    return request<RecommendationExplanation>(`/api/v1/recommendations/${recId}/explain`);
  },
};

