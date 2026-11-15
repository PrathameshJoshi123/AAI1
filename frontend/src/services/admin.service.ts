import {
  ExecutiveMetrics,
  RecentActivityResponse,
  ChannelPerformance,
  ProductPerformance,
  AdvisorPerformance,
  TurnaroundAnalytics,
  ConversionFunnelResponse,
  AgentTelemetry,
  AgentExecutionLogsResponse,
  Employee,
  EmployeeCreatePayload,
  AdminProduct,
  AdminProductCreatePayload,
  AuditLogSearchResponse,
  IntegrationHealth,
  SystemSetting,
  AdminCustomer,
} from "@/types/admin";

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
    throw new Error(
      errorData.detail || errorData.message || `Request failed with status ${response.status}`
    );
  }

  const json = await response.json();
  return json.data !== undefined ? json.data : json;
}

export const AdminAPI = {
  // 1. Business Overview
  async getMetrics(): Promise<ExecutiveMetrics> {
    return request<ExecutiveMetrics>("/api/v1/admin/overview/metrics");
  },

  async getActivityStream(limit = 15): Promise<RecentActivityResponse> {
    return request<RecentActivityResponse>(`/api/v1/admin/overview/activity-stream?limit=${limit}`);
  },

  async listCustomers(): Promise<AdminCustomer[]> {
    return request<AdminCustomer[]>("/api/v1/admin/overview/customers");
  },

  // 2. Business Analytics & Funnel
  async getChannelAnalytics(): Promise<ChannelPerformance[]> {
    return request<ChannelPerformance[]>("/api/v1/admin/analytics/channels");
  },

  async getProductAnalytics(): Promise<ProductPerformance[]> {
    return request<ProductPerformance[]>("/api/v1/admin/analytics/products");
  },

  async getAdvisorAnalytics(): Promise<AdvisorPerformance[]> {
    return request<AdvisorPerformance[]>("/api/v1/admin/analytics/advisors");
  },

  async getTurnaroundTimes(): Promise<TurnaroundAnalytics> {
    return request<TurnaroundAnalytics>("/api/v1/admin/analytics/turnaround");
  },

  async getConversionFunnel(): Promise<ConversionFunnelResponse> {
    return request<ConversionFunnelResponse>("/api/v1/admin/funnel");
  },

  // 3. Agent Control Centre
  async listAgents(): Promise<AgentTelemetry[]> {
    return request<AgentTelemetry[]>("/api/v1/admin/agents");
  },

  async updateAgentStatus(agentName: string, status: "active" | "paused" | "disabled"): Promise<AgentTelemetry> {
    return request<AgentTelemetry>(`/api/v1/admin/agents/${encodeURIComponent(agentName)}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
  },

  async getAgentExecutions(agentName: string, limit = 50): Promise<AgentExecutionLogsResponse> {
    return request<AgentExecutionLogsResponse>(
      `/api/v1/admin/agents/${encodeURIComponent(agentName)}/executions?limit=${limit}`
    );
  },

  // 4. Employee Management
  async listEmployees(): Promise<Employee[]> {
    return request<Employee[]>("/api/v1/admin/employees");
  },

  async createEmployee(payload: EmployeeCreatePayload): Promise<Employee> {
    return request<Employee>("/api/v1/admin/employees", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async updateEmployeeStatus(userId: string, isActive?: boolean, isAvailable?: boolean): Promise<void> {
    await request<void>(`/api/v1/admin/employees/${userId}/status`, {
      method: "PATCH",
      body: JSON.stringify({ is_active: isActive, is_available: isAvailable }),
    });
  },

  async updateEmployeeRoles(userId: string, roleNames: string[]): Promise<void> {
    await request<void>(`/api/v1/admin/employees/${userId}/roles`, {
      method: "PUT",
      body: JSON.stringify({ role_names: roleNames }),
    });
  },

  // 5. Product Management
  async listProducts(): Promise<AdminProduct[]> {
    return request<AdminProduct[]>("/api/v1/admin/products");
  },

  async createProduct(payload: AdminProductCreatePayload): Promise<AdminProduct> {
    return request<AdminProduct>("/api/v1/admin/products", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async toggleProductStatus(productId: string, isActive: boolean): Promise<void> {
    await request<void>(`/api/v1/admin/products/${productId}/status?is_active=${isActive}`, {
      method: "PATCH",
    });
  },

  // 6. Compliance & Audit Vault
  async searchAuditLogs(params: {
    action?: string;
    resource_type?: string;
    resource_id?: string;
    user_id?: string;
    from_date?: string;
    to_date?: string;
    page?: number;
    size?: number;
  }): Promise<AuditLogSearchResponse> {
    const searchParams = new URLSearchParams();
    if (params.action) searchParams.set("action", params.action);
    if (params.resource_type) searchParams.set("resource_type", params.resource_type);
    if (params.resource_id) searchParams.set("resource_id", params.resource_id);
    if (params.user_id) searchParams.set("user_id", params.user_id);
    if (params.from_date) searchParams.set("from_date", params.from_date);
    if (params.to_date) searchParams.set("to_date", params.to_date);
    searchParams.set("page", String(params.page || 1));
    searchParams.set("size", String(params.size || 25));

    return request<AuditLogSearchResponse>(`/api/v1/admin/audit/search?${searchParams.toString()}`);
  },

  // 7. Integration Management
  async checkIntegrations(): Promise<{ integrations: IntegrationHealth[] }> {
    return request<{ integrations: IntegrationHealth[] }>("/api/v1/admin/integrations/health");
  },

  async testIntegration(serviceKey: string): Promise<Record<string, unknown>> {
    return request<Record<string, unknown>>(`/api/v1/admin/integrations/${serviceKey}/test`, {
      method: "POST",
    });
  },

  // Phase 11: Email Engine Test & Delivery Audit Logs
  async sendTestEmail(recipient_email: string): Promise<any> {
    return request<any>("/api/v1/admin/integrations/email/test", {
      method: "POST",
      body: JSON.stringify({ recipient_email }),
    });
  },

  async getEmailDeliveryLogs(params: {
    page?: number;
    page_size?: number;
    status?: string;
    search?: string;
  } = {}): Promise<any> {
    const searchParams = new URLSearchParams();
    if (params.page) searchParams.set("page", String(params.page));
    if (params.page_size) searchParams.set("page_size", String(params.page_size));
    if (params.status) searchParams.set("status", params.status);
    if (params.search) searchParams.set("search", params.search);
    return request<any>(`/api/v1/admin/integrations/email/logs?${searchParams.toString()}`);
  },

  // 8. Dynamic System Settings
  async listSettings(): Promise<SystemSetting[]> {
    return request<SystemSetting[]>("/api/v1/admin/settings");
  },

  async updateSetting(key: string, valueJson: Record<string, unknown>, description?: string): Promise<SystemSetting> {
    return request<SystemSetting>(`/api/v1/admin/settings/${encodeURIComponent(key)}`, {
      method: "PUT",
      body: JSON.stringify({ value_json: valueJson, description }),
    });
  },
};
