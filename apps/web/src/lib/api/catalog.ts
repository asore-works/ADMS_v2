/**
 * Catalog API functions
 */

import { apiClient } from "@/lib/api";
import type {
  Catalog,
  CatalogCreate,
  CatalogFilters,
  CatalogListResponse,
  CatalogUpdate,
} from "@/types/catalog";

const BASE_PATH = "/api/v1/catalogs";

export const catalogApi = {
  /**
   * Get catalogs with optional filters
   */
  async getCatalogs(filters?: CatalogFilters): Promise<CatalogListResponse> {
    const params = new URLSearchParams();

    if (filters?.category) params.append("category", filters.category);
    if (filters?.is_active !== undefined) {
      params.append("is_active", String(filters.is_active));
    }
    if (filters?.search) params.append("search", filters.search);
    if (filters?.page) params.append("page", String(filters.page));
    if (filters?.page_size) params.append("page_size", String(filters.page_size));

    const queryString = params.toString();
    const endpoint = queryString ? `${BASE_PATH}?${queryString}` : BASE_PATH;

    return apiClient.get<CatalogListResponse>(endpoint);
  },

  /**
   * Get a single catalog by ID
   */
  async getCatalog(catalogId: string): Promise<Catalog> {
    return apiClient.get<Catalog>(`${BASE_PATH}/${catalogId}`);
  },

  /**
   * Create a new catalog
   */
  async createCatalog(data: CatalogCreate): Promise<Catalog> {
    return apiClient.post<Catalog>(BASE_PATH, data);
  },

  /**
   * Update an existing catalog
   */
  async updateCatalog(catalogId: string, data: CatalogUpdate): Promise<Catalog> {
    return apiClient.patch<Catalog>(`${BASE_PATH}/${catalogId}`, data);
  },

  /**
   * Delete a catalog (soft delete)
   */
  async deleteCatalog(catalogId: string): Promise<void> {
    return apiClient.delete<void>(`${BASE_PATH}/${catalogId}`);
  },
};
