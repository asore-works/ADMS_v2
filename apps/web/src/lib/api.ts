/**
 * API client for backend communication
 */

import type { ApiError } from "@/types/auth";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private getAccessToken(): string | null {
    if (typeof window === "undefined") return null;
    const stored = localStorage.getItem("auth-storage");
    if (!stored) return null;
    try {
      const parsed = JSON.parse(stored);
      return parsed.state?.accessToken ?? null;
    } catch {
      return null;
    }
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        detail: "An unexpected error occurred",
        status_code: response.status,
      }));
      throw new Error(error.detail);
    }
    return response.json();
  }

  async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const { body, headers: customHeaders, ...rest } = options;

    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...customHeaders,
    };

    const token = this.getAccessToken();
    if (token) {
      (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
    }

    const config: RequestInit = {
      ...rest,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    };

    const response = await fetch(`${this.baseUrl}${endpoint}`, config);
    return this.handleResponse<T>(response);
  }

  async get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "GET" });
  }

  async post<T>(endpoint: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "POST", body });
  }

  async put<T>(endpoint: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "PUT", body });
  }

  async patch<T>(endpoint: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "PATCH", body });
  }

  async delete<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "DELETE" });
  }

  // OAuth2 form-based login (required for FastAPI OAuth2PasswordBearer)
  async login(email: string, password: string): Promise<Response> {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    return fetch(`${this.baseUrl}/api/v1/auth/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData,
    });
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
