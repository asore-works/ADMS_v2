/**
 * Authentication hooks using TanStack Query
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import type {
  CurrentUser,
  LoginCredentials,
  TokenResponse,
  PasswordChangeRequest,
} from "@/types/auth";

// Query keys
export const authKeys = {
  all: ["auth"] as const,
  me: () => [...authKeys.all, "me"] as const,
};

// Fetch current user
export function useCurrentUserQuery() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return useQuery({
    queryKey: authKeys.me(),
    queryFn: () => apiClient.get<CurrentUser>("/api/v1/auth/me"),
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: false,
  });
}

// Login mutation
export function useLoginMutation() {
  const queryClient = useQueryClient();
  const { setTokens, setUser } = useAuthStore();

  return useMutation({
    mutationFn: async (credentials: LoginCredentials) => {
      const response = await apiClient.login(credentials.email, credentials.password);

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          detail: "Login failed",
        }));
        throw new Error(error.detail);
      }

      return response.json() as Promise<TokenResponse>;
    },
    onSuccess: async (data) => {
      setTokens(data.access_token, data.refresh_token);

      // Fetch user data after successful login
      try {
        const user = await apiClient.get<CurrentUser>("/api/v1/auth/me");
        setUser(user);
        queryClient.setQueryData(authKeys.me(), user);
      } catch {
        // User fetch failed, but tokens are set
      }
    },
  });
}

// Logout mutation
export function useLogoutMutation() {
  const queryClient = useQueryClient();
  const { logout } = useAuthStore();

  return useMutation({
    mutationFn: async () => {
      try {
        await apiClient.post("/api/v1/auth/logout");
      } catch {
        // Logout endpoint might fail, but we still want to clear local state
      }
    },
    onSettled: () => {
      logout();
      queryClient.clear();
    },
  });
}

// Refresh token mutation
export function useRefreshTokenMutation() {
  const { refreshToken, setTokens } = useAuthStore();

  return useMutation({
    mutationFn: async () => {
      if (!refreshToken) {
        throw new Error("No refresh token available");
      }

      return apiClient.post<TokenResponse>("/api/v1/auth/refresh", {
        refresh_token: refreshToken,
      });
    },
    onSuccess: (data) => {
      setTokens(data.access_token, data.refresh_token);
    },
  });
}

// Change password mutation
export function useChangePasswordMutation() {
  return useMutation({
    mutationFn: (data: PasswordChangeRequest) =>
      apiClient.post<{ message: string }>("/api/v1/auth/change-password", data),
  });
}
