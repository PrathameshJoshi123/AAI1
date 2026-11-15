import { DocumentItem } from "@/types/document";

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

export const DocumentAPI = {
  async uploadDocument(
    applicationId: string,
    documentType: string,
    file: File
  ): Promise<DocumentItem> {
    const formData = new FormData();
    formData.append("application_id", applicationId);
    formData.append("document_type", documentType);
    formData.append("file", file);

    const token = getAuthToken();
    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/api/v1/documents/upload`, {
      method: "POST",
      headers,
      body: formData,
    });

    if (!response.ok) {
      let errorDetail = "Document upload failed";
      try {
        const errJson = await response.json();
        errorDetail = errJson.detail || errJson.message || errorDetail;
      } catch {
        // ignore
      }
      throw new Error(errorDetail);
    }

    const json = await response.json();
    return json.data.document ?? json.data;
  },

  getDownloadUrl(documentId: string): string {
    return `${API_BASE_URL}/api/v1/documents/${documentId}/download`;
  },

  async listCustomerDocuments(): Promise<DocumentItem[]> {
    const token = getAuthToken();
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE_URL}/api/v1/documents/customer`, { headers });
    if (!res.ok) throw new Error("Failed to load customer documents");
    const json = await res.json();
    return json.data ?? [];
  },

  async listApplicationDocuments(applicationId: string): Promise<DocumentItem[]> {
    const token = getAuthToken();
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE_URL}/api/v1/documents/application/${applicationId}`, {
      headers,
    });
    if (!res.ok) throw new Error("Failed to load application documents");
    const json = await res.json();
    return json.data ?? [];
  },
};
