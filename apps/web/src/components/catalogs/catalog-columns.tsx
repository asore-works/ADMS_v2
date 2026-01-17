/**
 * Catalog table column definitions
 */

"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown, MoreHorizontal } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { Catalog, CatalogCategory } from "@/types/catalog";

const categoryLabels: Record<CatalogCategory, string> = {
  drone: "ドローン",
  battery: "バッテリー",
  camera: "カメラ",
  sensor: "センサー",
  accessory: "アクセサリー",
  software: "ソフトウェア",
  other: "その他",
};

const categoryColors: Record<CatalogCategory, "default" | "secondary" | "outline"> = {
  drone: "default",
  battery: "secondary",
  camera: "secondary",
  sensor: "secondary",
  accessory: "outline",
  software: "outline",
  other: "outline",
};

interface CatalogColumnsProps {
  onEdit: (catalog: Catalog) => void;
  onDelete: (catalog: Catalog) => void;
}

export function createCatalogColumns({
  onEdit,
  onDelete,
}: CatalogColumnsProps): ColumnDef<Catalog>[] {
  return [
    {
      id: "select",
      header: ({ table }) => (
        <Checkbox
          checked={
            table.getIsAllPageRowsSelected() ||
            (table.getIsSomePageRowsSelected() && "indeterminate")
          }
          onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
          aria-label="すべて選択"
        />
      ),
      cell: ({ row }) => (
        <Checkbox
          checked={row.getIsSelected()}
          onCheckedChange={(value) => row.toggleSelected(!!value)}
          aria-label="行を選択"
        />
      ),
      enableSorting: false,
      enableHiding: false,
    },
    {
      accessorKey: "name",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            カタログ名
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        );
      },
      cell: ({ row }) => <div className="font-medium">{row.getValue("name")}</div>,
    },
    {
      accessorKey: "category",
      header: "カテゴリー",
      cell: ({ row }) => {
        const category = row.getValue("category") as CatalogCategory;
        return <Badge variant={categoryColors[category]}>{categoryLabels[category]}</Badge>;
      },
    },
    {
      accessorKey: "manufacturer",
      header: "メーカー",
      cell: ({ row }) => {
        const manufacturer = row.getValue("manufacturer") as string | null;
        return <div>{manufacturer ?? "-"}</div>;
      },
    },
    {
      accessorKey: "model_number",
      header: "型番",
      cell: ({ row }) => {
        const modelNumber = row.getValue("model_number") as string | null;
        return <div>{modelNumber ?? "-"}</div>;
      },
    },
    {
      accessorKey: "sku_code",
      header: "SKUコード",
      cell: ({ row }) => {
        const skuCode = row.getValue("sku_code") as string | null;
        return <div className="font-mono text-sm">{skuCode ?? "-"}</div>;
      },
    },
    {
      accessorKey: "unit_price",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="ml-auto"
          >
            単価
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        );
      },
      cell: ({ row }) => {
        const price = row.getValue("unit_price") as number | null;
        if (price === null) return <div className="text-right">-</div>;
        const formatted = new Intl.NumberFormat("ja-JP", {
          style: "currency",
          currency: "JPY",
        }).format(price);
        return <div className="text-right font-medium">{formatted}</div>;
      },
    },
    {
      accessorKey: "is_active",
      header: "ステータス",
      cell: ({ row }) => {
        const isActive = row.getValue("is_active") as boolean;
        return (
          <Badge variant={isActive ? "default" : "secondary"}>{isActive ? "有効" : "無効"}</Badge>
        );
      },
    },
    {
      id: "actions",
      enableHiding: false,
      cell: ({ row }) => {
        const catalog = row.original;

        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">メニューを開く</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>アクション</DropdownMenuLabel>
              <DropdownMenuItem onClick={() => navigator.clipboard.writeText(catalog.id)}>
                IDをコピー
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => onEdit(catalog)}>編集</DropdownMenuItem>
              <DropdownMenuItem onClick={() => onDelete(catalog)} className="text-destructive">
                削除
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        );
      },
    },
  ];
}
