/**
 * Catalog types
 */

export type CatalogCategory =
  | "drone"
  | "battery"
  | "camera"
  | "controller"
  | "sensor"
  | "accessory"
  | "software"
  | "other";

export type JSONValue =
  | string
  | number
  | boolean
  | null
  | JSONValue[]
  | { [key: string]: JSONValue };

export interface Catalog {
  id: string;
  organization_id: string;
  name: string;
  category: CatalogCategory;
  manufacturer: string | null;
  model_number: string | null;
  sku_code: string | null;
  specifications: Record<string, JSONValue> | null;
  description: string | null;
  weight_grams: number | null;
  max_flight_time_minutes: number | null;
  max_range_meters: number | null;
  price: number | null;
  image_url: string | null;
  spec_document_url: string | null;
  is_active: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface CatalogCreate {
  organization_id: string;
  name: string;
  category: CatalogCategory;
  manufacturer?: string | null;
  model_number?: string | null;
  sku_code?: string | null;
  specifications?: Record<string, JSONValue> | null;
  description?: string | null;
  unit_price?: number | null;
  is_active?: boolean;
}

export interface CatalogUpdate {
  name?: string;
  category?: CatalogCategory;
  manufacturer?: string | null;
  model_number?: string | null;
  sku_code?: string | null;
  specifications?: Record<string, JSONValue> | null;
  description?: string | null;
  unit_price?: number | null;
  is_active?: boolean;
}

export interface CatalogListResponse {
  catalogs: Catalog[];
  total: number;
  page: number;
  page_size: number;
}

export interface CatalogFilters {
  category?: CatalogCategory;
  is_active?: boolean;
  search?: string;
  page?: number;
  page_size?: number;
}
