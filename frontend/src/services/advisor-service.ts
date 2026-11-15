import { WorkspaceDashboardData, FollowUpItem, AppNotification } from "@/types/advisor";

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

export const advisorService = {
  async getWorkspaceDashboard(): Promise<WorkspaceDashboardData> {
    return request<WorkspaceDashboardData>("/api/v1/advisor/workspace/dashboard");
  },

  async getFollowUps(status?: string): Promise<FollowUpItem[]> {
    const qs = status ? `?status=${encodeURIComponent(status)}` : "";
    return request<FollowUpItem[]>(`/api/v1/follow-ups${qs}`);
  },

  async createFollowUp(payload: {
    customer_id?: string;
    prospect_id?: string;
    assigned_advisor_id?: string;
    due_date: string;
    channel: string;
    priority: string;
    notes?: string;
  }): Promise<FollowUpItem> {
    return request<FollowUpItem>("/api/v1/follow-ups", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async updateFollowUpStatus(
    id: number,
    payload: { status?: string; notes?: string; due_date?: string }
  ): Promise<FollowUpItem> {
    return request<FollowUpItem>(`/api/v1/follow-ups/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
  },

  async getDocumentVerificationQueue(status?: string): Promise<any[]> {
    const qs = status ? `?status=${encodeURIComponent(status)}` : "";
    return request<any[]>(`/api/v1/documents/queue${qs}`);
  },

  async verifyDocument(documentId: string, notes?: string): Promise<any> {
    return request(`/api/v1/documents/${documentId}/verify`, {
      method: "POST",
      body: JSON.stringify({ decision: "verified", verification_notes: notes }),
    });
  },

  async rejectDocument(documentId: string, rejectionReason: string): Promise<any> {
    return request(`/api/v1/documents/${documentId}/verify`, {
      method: "POST",
      body: JSON.stringify({ decision: "rejected", rejection_reason: rejectionReason }),
    });
  },

  async getNotifications(): Promise<{ unread_count: number; items: AppNotification[] }> {
    return request<{ unread_count: number; items: AppNotification[] }>("/api/v1/notifications");
  },

  async markNotificationRead(id: number): Promise<AppNotification> {
    return request<AppNotification>(`/api/v1/notifications/${id}/read`, {
      method: "PUT",
    });
  },

  async markAllNotificationsRead(): Promise<any> {
    return request("/api/v1/notifications/mark-all-read", {
      method: "PUT",
    });
  },

  async getApplications(status?: string): Promise<any[]> {
    return request<any[]>("/api/v1/applications");
  },

  async getTimeline(): Promise<any[]> {
    return request<any[]>("/api/v1/advisor/workspace/timeline");
  },

  async getConversations(): Promise<any[]> {
    return request<any[]>("/api/v1/customer/chat/advisor/conversations");
  },

  async getConversation(id: string): Promise<any> {
    return request<any>(`/api/v1/customer/chat/advisor/conversations/${encodeURIComponent(id)}`);
  },
};
