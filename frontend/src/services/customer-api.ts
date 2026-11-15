import {
  CustomerProfile,
  CustomerProfileUpdatePayload,
  JourneyStatus,
  ResumeJourneyData,
  ChatMessage,
  ConversationThread,
  NeedsAssessmentPayload,
  NeedsAssessmentResult,
  HLVCalculationPayload,
  HLVCalculationResult,
  ConsentRecordItem,
  InsuranceProductItem,
} from "@/types/customer";

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

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | string[] | undefined | null>;
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { params, headers, ...customConfig } = options;

  let url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;

  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        if (Array.isArray(value)) {
          value.forEach((v) => searchParams.append(key, String(v)));
        } else {
          searchParams.append(key, String(value));
        }
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }

  const token = getAuthToken();

  const config: RequestInit = {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    ...customConfig,
  };

  const response = await fetch(url, config);

  if (response.status === 401 && typeof window !== "undefined") {
    // Session expired; redirect to login
    window.location.assign("/login");
    throw new Error("Session expired. Please log in again.");
  }

  const data = await response.json();

  if (!response.ok) {
    const errorMessage = data?.error?.message || data?.message || "An API error occurred.";
    throw new Error(errorMessage);
  }

  return (data?.data !== undefined ? data.data : data) as T;
}

export const CustomerAPI = {
  // Profile
  getProfile: () => request<CustomerProfile>("/api/v1/customer/profile"),
  updateProfile: (payload: CustomerProfileUpdatePayload) =>
    request<CustomerProfile>("/api/v1/customer/profile", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),

  // Journey
  getJourneyStatus: () => request<JourneyStatus>("/api/v1/customer/journey/status"),
  transitionStage: (target_stage: string) =>
    request<string>("/api/v1/customer/journey/transition", {
      method: "POST",
      body: JSON.stringify({ target_stage }),
    }),
  resumeJourney: () => request<ResumeJourneyData>("/api/v1/customer/journey/resume", { method: "POST" }),

  // Chat
  sendChatTurn: (payload: { conversation_id?: string; message: string; language?: string }) =>
    request<ChatMessage>("/api/v1/customer/chat/turn", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getChatHistory: (conversation_id?: string) =>
    request<ConversationThread>("/api/v1/customer/chat/history", {
      params: conversation_id ? { conversation_id } : {},
    }),

  // Needs Assessment
  submitNeedsAssessment: (payload: NeedsAssessmentPayload) =>
    request<NeedsAssessmentResult>("/api/v1/customer/needs/assess", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getNeedsSummary: () => request<any>("/api/v1/customer/needs/summary"),

  // Coverage Calculator
  calculateHLV: (payload: HLVCalculationPayload) =>
    request<HLVCalculationResult>("/api/v1/customer/calculator/hlv", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // Consents & Privacy
  listConsents: () => request<ConsentRecordItem[]>("/api/v1/customer/consent"),
  grantConsent: (consent_type: string) =>
    request<ConsentRecordItem>("/api/v1/customer/consent/grant", {
      method: "POST",
      body: JSON.stringify({ consent_type, consent_version: "2026.1" }),
    }),
  revokeConsent: (consent_type: string) =>
    request<{ revoked_count: number }>("/api/v1/customer/consent/revoke", {
      method: "POST",
      body: JSON.stringify({ consent_type }),
    }),

  // Catalog & Quotes
  listProducts: () => request<InsuranceProductItem[]>("/api/v1/products"),
  listQuotes: () => request<any[]>("/api/v1/quotes"),
  listApplications: () => request<any[]>("/api/v1/applications"),

  // Phase 11: Email Notification & Provisioning
  updateEmail: (email: string) =>
    request<{ email: string; user_id: string }>("/api/v1/customer/email/update", {
      method: "POST",
      body: JSON.stringify({ email }),
    }),
  getEmailPreferences: () => request<any>("/api/v1/customer/email/preferences"),
  updateEmailPreferences: (payload: {
    notification_email?: string;
    quote_alerts?: boolean;
    application_updates?: boolean;
    document_requests?: boolean;
    marketing_consent?: boolean;
  }) =>
    request<any>("/api/v1/customer/email/preferences", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  sendQuoteEmail: (quoteId: string, recipient_email?: string) =>
    request<any>(`/api/v1/quotes/${quoteId}/send-email`, {
      method: "POST",
      body: JSON.stringify({ recipient_email }),
    }),
};


