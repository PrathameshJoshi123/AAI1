import {
  ApplicationDetail,
  ApplicationItem,
  DynamicRequirements,
} from "@/types/application";

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

  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    let errorDetail = "Application request failed";
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.message || errorDetail;
    } catch {
      // ignore
    }
    throw new Error(errorDetail);
  }

  const json = await response.json();
  return json.data ?? json;
}

export const ApplicationAPI = {
  async getOrCreateDraft(quoteId: string): Promise<ApplicationItem> {
    return request<ApplicationItem>("/api/v1/applications/draft", {
      method: "POST",
      body: JSON.stringify({ quote_id: quoteId }),
    });
  },

  async saveDraftStep(
    applicationId: string,
    currentStep: number,
    stepKey: string,
    stepData: Record<string, any>
  ): Promise<ApplicationItem> {
    return request<ApplicationItem>(`/api/v1/applications/${applicationId}/draft`, {
      method: "PUT",
      body: JSON.stringify({
        current_step: currentStep,
        step_key: stepKey,
        step_data: stepData,
      }),
    });
  },

  async getRequirements(applicationId: string): Promise<DynamicRequirements> {
    return request<DynamicRequirements>(`/api/v1/applications/${applicationId}/requirements`);
  },

  async getApplication(applicationId: string): Promise<ApplicationDetail> {
    return request<ApplicationDetail>(`/api/v1/applications/${applicationId}`);
  },

  async submitProposal(
    applicationId: string,
    eSignatureName: string
  ): Promise<ApplicationItem> {
    return request<ApplicationItem>(`/api/v1/applications/${applicationId}/submit`, {
      method: "POST",
      body: JSON.stringify({
        e_signature_name: eSignatureName,
        acknowledged_declarations: true,
      }),
    });
  },

  async listApplications(): Promise<ApplicationItem[]> {
    return request<ApplicationItem[]>("/api/v1/applications");
  },
};
