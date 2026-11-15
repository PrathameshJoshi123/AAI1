import {
  UnderwritingCaseSummary,
  UnderwritingCaseDetail,
  UnderwritingReview,
  ReviewSubmissionPayload,
  CaseNote,
} from "@/types/underwriting";

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
  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  const token = getAuthToken();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  const resJson = await response.json();
  if (!response.ok) {
    throw new Error(resJson.detail || resJson.message || `Request failed with status ${response.status}`);
  }

  return resJson.data ?? resJson;
}

export const underwritingService = {
  async getTriageQueue(params?: {
    status?: string;
    priority?: string;
    risk_rating?: string;
  }): Promise<UnderwritingCaseSummary[]> {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.append("status", params.status);
    if (params?.priority) searchParams.append("priority", params.priority);
    if (params?.risk_rating) searchParams.append("risk_rating", params.risk_rating);
    const qs = searchParams.toString();
    return request<UnderwritingCaseSummary[]>(`/api/v1/underwriting/triage${qs ? `?${qs}` : ""}`);
  },

  async getCaseDetail(caseNumber: string): Promise<UnderwritingCaseDetail> {
    return request<UnderwritingCaseDetail>(`/api/v1/underwriting/cases/${encodeURIComponent(caseNumber)}`);
  },

  async submitReview(caseNumber: string, payload: ReviewSubmissionPayload): Promise<UnderwritingReview> {
    return request<UnderwritingReview>(`/api/v1/underwriting/cases/${encodeURIComponent(caseNumber)}/reviews`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async triggerAiRiskSynthesis(caseNumber: string): Promise<any> {
    return request(`/api/v1/underwriting/cases/${encodeURIComponent(caseNumber)}/ai-escalation`, {
      method: "POST",
    });
  },

  async getCaseNotes(caseId: string): Promise<CaseNote[]> {
    return request<CaseNote[]>(`/api/v1/underwriting/cases/${encodeURIComponent(caseId)}/notes`);
  },

  async addCaseNote(caseId: string, payload: { note_type: string; content: string; is_confidential: boolean }): Promise<CaseNote> {
    return request<CaseNote>(`/api/v1/underwriting/cases/${encodeURIComponent(caseId)}/notes`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};

