/**
 * Catalog management page
 */

"use client";

import * as React from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { toast } from "sonner";

import { CatalogForm } from "@/components/catalogs/catalog-form";
import { CatalogTable } from "@/components/catalogs/catalog-table";
import { createCatalogColumns } from "@/components/catalogs/catalog-columns";
import { Button } from "@/components/ui/button";
import { catalogApi } from "@/lib/api/catalog";
import { useCurrentUser } from "@/stores/auth";
import type { Catalog, CatalogCreate, CatalogFilters } from "@/types/catalog";

export default function CatalogsPage() {
  const queryClient = useQueryClient();
  const currentUser = useCurrentUser();

  const [isFormOpen, setIsFormOpen] = React.useState(false);
  const [selectedCatalog, setSelectedCatalog] = React.useState<Catalog | null>(null);
  const [filters, setFilters] = React.useState<CatalogFilters>({
    page: 1,
    page_size: 20,
    is_active: true,
  });

  // Fetch catalogs
  const { data, isLoading } = useQuery({
    queryKey: ["catalogs", filters],
    queryFn: () => catalogApi.getCatalogs(filters),
    enabled: !!currentUser,
  });

  // Create catalog mutation
  const createMutation = useMutation({
    mutationFn: (data: CatalogCreate) => catalogApi.createCatalog(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["catalogs"] });
      toast.success("カタログを作成しました");
      setIsFormOpen(false);
      setSelectedCatalog(null);
    },
    onError: (error: Error) => {
      toast.error(`作成に失敗しました: ${error.message}`);
    },
  });

  // Update catalog mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CatalogCreate> }) =>
      catalogApi.updateCatalog(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["catalogs"] });
      toast.success("カタログを更新しました");
      setIsFormOpen(false);
      setSelectedCatalog(null);
    },
    onError: (error: Error) => {
      toast.error(`更新に失敗しました: ${error.message}`);
    },
  });

  // Delete catalog mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => catalogApi.deleteCatalog(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["catalogs"] });
      toast.success("カタログを削除しました");
    },
    onError: (error: Error) => {
      toast.error(`削除に失敗しました: ${error.message}`);
    },
  });

  const handleEdit = React.useCallback((catalog: Catalog) => {
    setSelectedCatalog(catalog);
    setIsFormOpen(true);
  }, []);

  const handleDelete = React.useCallback(
    (catalog: Catalog) => {
      if (window.confirm(`「${catalog.name}」を削除しますか？`)) {
        deleteMutation.mutate(catalog.id);
      }
    },
    [deleteMutation]
  );

  const handleSubmit = async (values: Partial<CatalogCreate>) => {
    if (!currentUser?.organization_id) {
      toast.error("組織IDが取得できません");
      return;
    }

    if (selectedCatalog) {
      await updateMutation.mutateAsync({
        id: selectedCatalog.id,
        data: values,
      });
    } else {
      await createMutation.mutateAsync({
        ...values,
        organization_id: currentUser.organization_id,
      } as CatalogCreate);
    }
  };

  const handleSearchChange = (value: string) => {
    setFilters((prev) => ({
      ...prev,
      search: value || undefined,
      page: 1,
    }));
  };

  const columns = React.useMemo(
    () =>
      createCatalogColumns({
        onEdit: handleEdit,
        onDelete: handleDelete,
      }),
    [handleEdit, handleDelete]
  );

  if (!currentUser) {
    return (
      <div className="flex h-full items-center justify-center">
        <p className="text-muted-foreground">ユーザー情報を読み込んでいます...</p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col space-y-4 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">カタログ管理</h1>
          <p className="text-muted-foreground">機材カタログの登録・管理</p>
        </div>
        <Button onClick={() => setIsFormOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          カタログ追加
        </Button>
      </div>

      <CatalogTable
        columns={columns}
        data={data?.catalogs ?? []}
        onSearchChange={handleSearchChange}
        isLoading={isLoading}
      />

      <CatalogForm
        open={isFormOpen}
        onOpenChange={(open) => {
          setIsFormOpen(open);
          if (!open) setSelectedCatalog(null);
        }}
        catalog={selectedCatalog}
        onSubmit={handleSubmit}
        isSubmitting={createMutation.isPending || updateMutation.isPending}
      />
    </div>
  );
}
