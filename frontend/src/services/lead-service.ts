import {
  AdvisorSummary,
  AssignedLeadItem,
  LeadRecord,
  LeadScore,
  LeadTimelineEvent,
  OutreachLogRequest,
  PaginatedLeadsResponse,
  ProspectDetail,
  ProspectFilterParams,
} from "@/types/lead";

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
      url += (url.includes("?") ? "&" : "?") + queryString;
    }
  }

  const token = getAuthToken();
  const defaultHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
  };

  if (token) {
    defaultHeaders["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    headers: {
      ...defaultHeaders,
      ...(headers as Record<string, string>),
    },
    ...customConfig,
  });

  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        errorMessage =
          typeof errorJson.detail === "string"
            ? errorJson.detail
            : JSON.stringify(errorJson.detail);
      } else if (errorJson.message) {
        errorMessage = errorJson.message;
      }
    } catch {
      // Fallback to response.statusText
    }
    throw new Error(errorMessage);
  }

  // If response is 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  const result = await response.json();

  // If envelope format { success: true, data: ... }
  if (result && typeof result === "object" && "data" in result && result.data !== undefined) {
    return result.data as T;
  }

  return result as T;
}

export const leadService = {
  /**
   * Admin: List and filter prospects with pagination
   */
  async getProspects(params: ProspectFilterParams = {}): Promise<PaginatedLeadsResponse> {
    const res = await request<PaginatedLeadsResponse | LeadRecord[]>("/api/v1/prospects", {
      method: "GET",
      params: {
        query: params.query,
        status: params.status,
        segment: params.segment,
        source_id: params.source_id,
        source_name: params.source_name,
        assigned_advisor_id: params.assigned_advisor_id,
        min_score: params.min_score,
        max_score: params.max_score,
        consented_only: params.consented_only,
        date_from: params.date_from,
        date_to: params.date_to,
        page: params.page || 1,
        page_size: params.page_size || 20,
        sort_by: params.sort_by || "last_activity_at",
        sort_order: params.sort_order || "desc",
      },
    });

    // Normalize if backend returned direct array or paginated object
    if (Array.isArray(res)) {
      return {
        items: res,
        total: res.length,
        page: params.page || 1,
        page_size: params.page_size || 20,
        total_pages: Math.max(1, Math.ceil(res.length / (params.page_size || 20))),
      };
    }

    if (res && typeof res === "object" && Array.isArray(res.items)) {
      return {
        items: res.items,
        total: res.total ?? res.items.length,
        page: res.page ?? params.page ?? 1,
        page_size: res.page_size ?? params.page_size ?? 20,
        total_pages: res.total_pages ?? Math.max(1, Math.ceil((res.total ?? res.items.length) / (res.page_size || 20))),
      };
    }

    return {
      items: [],
      total: 0,
      page: 1,
      page_size: 20,
      total_pages: 1,
    };
  },

  /**
   * Admin / Advisor: Get full detailed prospect inspector data
   */
  async getProspectById(id: string): Promise<ProspectDetail> {
    return request<ProspectDetail>(`/api/v1/prospects/${encodeURIComponent(id)}`, {
      method: "GET",
    });
  },

  /**
   * Ingest / create a new prospect
   */
  async createProspect(payload: {
    name?: string;
    email?: string;
    phone?: string;
    source_name?: string;
    utm_source?: string;
    utm_medium?: string;
    utm_campaign?: string;
    utm_term?: string;
    utm_content?: string;
    target_insurance_type?: string;
    initial_session_id: string;
  }): Promise<ProspectDetail> {
    return request<ProspectDetail>("/api/v1/prospects", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * Update prospect details
   */
  async updateProspect(id: string, payload: Partial<ProspectDetail>): Promise<ProspectDetail> {
    return request<ProspectDetail>(`/api/v1/prospects/${encodeURIComponent(id)}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  /**
   * Manually assign or reassign advisor with audit note
   */
  async assignAdvisor(
    prospectId: string,
    advisorId: string,
    reassignmentReason?: string
  ): Promise<{ success: boolean; message: string }> {
    return request<{ success: boolean; message: string }>(
      `/api/v1/prospects/${encodeURIComponent(prospectId)}/assign`,
      {
        method: "POST",
        body: JSON.stringify({
          advisor_id: advisorId,
          reason: reassignmentReason || "Manual administrative assignment",
        }),
      }
    );
  },

  /**
   * On-demand recalculate deterministic lead score
   */
  async recalculateScore(prospectId: string): Promise<LeadScore> {
    return request<LeadScore>(
      `/api/v1/prospects/${encodeURIComponent(prospectId)}/recalculate-score`,
      {
        method: "POST",
      }
    );
  },

  /**
   * Get chronological unified activity timeline
   */
  async getProspectTimeline(prospectId: string): Promise<LeadTimelineEvent[]> {
    const res = await request<LeadTimelineEvent[]>(
      `/api/v1/prospects/${encodeURIComponent(prospectId)}/timeline`,
      {
        method: "GET",
      }
    );
    return Array.isArray(res) ? res : [];
  },

  /**
   * Fetch active advisors with workload & capacity stats
   */
  async getAvailableAdvisors(): Promise<AdvisorSummary[]> {
    try {
      const res = await request<AdvisorSummary[]>("/api/v1/roles/advisors", {
        method: "GET",
      });
      if (Array.isArray(res)) return res;
    } catch {
      // Fallback endpoint if under /prospects/advisors
      try {
        const fallback = await request<AdvisorSummary[]>("/api/v1/prospects/advisors/available", {
          method: "GET",
        });
        if (Array.isArray(fallback)) return fallback;
      } catch {
        // Return empty array
      }
    }
    return [];
  },

  /**
   * Ingest client-side behavioral signal
   */
  async recordSignal(payload: {
    session_id: string;
    prospect_id?: string;
    signal_type: string;
    payload?: Record<string, unknown>;
    client_timestamp?: string;
  }): Promise<{ success: boolean; id?: number }> {
    return request<{ success: boolean; id?: number }>("/api/v1/signals", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * Batch ingest client-side behavioral signals
   */
  async recordSignalBatch(payload: {
    events: Array<{
      session_id: string;
      prospect_id?: string;
      signal_type: string;
      payload?: Record<string, unknown>;
      client_timestamp?: string;
    }>;
  }): Promise<{ success: boolean; count: number }> {
    return request<{ success: boolean; count: number }>("/api/v1/signals/batch", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * Record explicit legal consent grant
   */
  async grantConsent(payload: {
    prospect_id: string;
    consent_type: string;
    consent_version?: string;
    ip_address?: string;
    user_agent?: string;
  }): Promise<{ success: boolean; consent_id?: number }> {
    return request<{ success: boolean; consent_id?: number }>("/api/v1/consent", {
      method: "POST",
      body: JSON.stringify({
        consent_version: "2026.1",
        ...payload,
      }),
    });
  },

  /**
   * Record explicit consent revocation
   */
  async revokeConsent(payload: {
    prospect_id: string;
    consent_type: string;
    reason?: string;
  }): Promise<{ success: boolean }> {
    return request<{ success: boolean }>("/api/v1/consent/revoke", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  /**
   * Advisor-scoped: List leads assigned to currently authenticated advisor
   */
  async getAdvisorLeads(params?: {
    priority?: string;
    type?: string;
    search?: string;
  }): Promise<AssignedLeadItem[]> {
    const res = await request<AssignedLeadItem[]>("/api/v1/advisor/leads", {
      method: "GET",
      params,
    });
    return Array.isArray(res) ? res : [];
  },

  /**
   * Advisor: Log customer outreach notes & follow-up task
   */
  async logAdvisorOutreach(
    leadId: string,
    payload: OutreachLogRequest
  ): Promise<{ success: boolean; message?: string }> {
    return request<{ success: boolean; message?: string }>(
      `/api/v1/advisor/leads/${encodeURIComponent(leadId)}/notes`,
      {
        method: "POST",
        body: JSON.stringify(payload),
      }
    );
  },

  /**
   * Advisor: Transition lead status (contacted, qualified, disqualified)
   */
  async updateAdvisorLeadStatus(
    leadId: string,
    status: string,
    notes?: string
  ): Promise<{ success: boolean; message?: string }> {
    return request<{ success: boolean; message?: string }>(
      `/api/v1/advisor/leads/${encodeURIComponent(leadId)}/status`,
      {
        method: "POST",
        body: JSON.stringify({ status, notes }),
      }
    );
  },
};
