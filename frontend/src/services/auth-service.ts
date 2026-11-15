const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

export interface UserProfile {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string | null;
  is_active: boolean;
  is_verified: boolean;
  roles: Array<{ id: number; name: string }>;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: UserProfile;
}

export interface RegisterPayload {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
  role?: "Customer" | "Advisor" | "Underwriter" | "Admin" | "Owner";
}

export const AuthService = {
  saveTokens(data: TokenResponse) {
    if (typeof window === "undefined") return;
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("auth_token", data.access_token);
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    localStorage.setItem("user", JSON.stringify(data.user));
  },

  clearTokens() {
    if (typeof window === "undefined") return;
    localStorage.removeItem("token");
    localStorage.removeItem("auth_token");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
  },

  getUser(): UserProfile | null {
    if (typeof window === "undefined") return null;
    const raw = localStorage.getItem("user");
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  },

  async login(credentials: { email: string; password: string }): Promise<TokenResponse> {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
    });

    const json = await res.json();
    if (!res.ok) {
      const msg = json?.error?.message || json?.detail || "Authentication failed.";
      throw new Error(msg);
    }

    const tokenData: TokenResponse = json.data || json;
    AuthService.saveTokens(tokenData);
    return tokenData;
  },

  async register(payload: RegisterPayload): Promise<UserProfile> {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: payload.email,
        password: payload.password,
        first_name: payload.first_name,
        last_name: payload.last_name,
        phone: payload.phone || null,
        role: payload.role || "Customer",
      }),
    });

    const json = await res.json();
    if (!res.ok) {
      const msg = json?.error?.message || json?.detail || "Registration failed.";
      throw new Error(msg);
    }

    return json.data || json;
  },

  async logout() {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    try {
      if (token) {
        await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });
      }
    } catch {
      // ignore logout network errors
    } finally {
      AuthService.clearTokens();
    }
  },
};

