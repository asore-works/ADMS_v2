/**
 * Catalog form component for create/edit
 */

"use client";

import { useEffect } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { Catalog, CatalogCategory } from "@/types/catalog";

const catalogSchema = z.object({
  name: z.string().min(1, "カタログ名を入力してください"),
  category: z.enum([
    "drone",
    "battery",
    "camera",
    "controller",
    "sensor",
    "accessory",
    "software",
    "other",
  ]),
  manufacturer: z.string().optional(),
  model_number: z.string().optional(),
  sku_code: z.string().optional(),
  description: z.string().optional(),
  price: z.number().nonnegative().optional(),
  is_active: z.boolean().optional(),
});

type CatalogFormValues = z.infer<typeof catalogSchema>;

interface CatalogFormProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  catalog?: Catalog | null;
  onSubmit: (values: CatalogFormValues) => Promise<void>;
  isSubmitting?: boolean;
}

const categoryOptions: { value: CatalogCategory; label: string }[] = [
  { value: "drone", label: "ドローン" },
  { value: "battery", label: "バッテリー" },
  { value: "camera", label: "カメラ" },
  { value: "controller", label: "コントローラー" },
  { value: "sensor", label: "センサー" },
  { value: "accessory", label: "アクセサリー" },
  { value: "software", label: "ソフトウェア" },
  { value: "other", label: "その他" },
];

export function CatalogForm({
  open,
  onOpenChange,
  catalog,
  onSubmit,
  isSubmitting = false,
}: CatalogFormProps) {
  const form = useForm<CatalogFormValues>({
    resolver: zodResolver(catalogSchema),
    defaultValues: {
      name: "",
      category: "drone",
      manufacturer: "",
      model_number: "",
      sku_code: "",
      description: "",
      is_active: true,
    },
  });

  // catalogが変更されたときにフォームをリセット
  useEffect(() => {
    if (catalog) {
      form.reset({
        name: catalog.name,
        category: catalog.category,
        manufacturer: catalog.manufacturer ?? undefined,
        model_number: catalog.model_number ?? undefined,
        sku_code: catalog.sku_code ?? undefined,
        description: catalog.description ?? undefined,
        price: catalog.price ?? undefined,
        is_active: catalog.is_active,
      });
    } else {
      form.reset({
        name: "",
        category: "drone",
        manufacturer: "",
        model_number: "",
        sku_code: "",
        description: "",
        is_active: true,
      });
    }
  }, [catalog, form]);

  const handleSubmit = async (values: CatalogFormValues) => {
    await onSubmit(values);
    form.reset();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{catalog ? "カタログ編集" : "カタログ新規作成"}</DialogTitle>
          <DialogDescription>
            {catalog ? "カタログ情報を編集します" : "新しいカタログを登録します"}
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>カタログ名 *</FormLabel>
                    <FormControl>
                      <Input placeholder="DJI Mavic 3 Pro" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="category"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>カテゴリー *</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="カテゴリーを選択" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {categoryOptions.map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="manufacturer"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>メーカー</FormLabel>
                    <FormControl>
                      <Input placeholder="DJI" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="model_number"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>型番</FormLabel>
                    <FormControl>
                      <Input placeholder="CP.MA.00000123.01" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="sku_code"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>SKUコード</FormLabel>
                    <FormControl>
                      <Input placeholder="DRN-001" {...field} />
                    </FormControl>
                    <FormDescription>内部管理用の商品コード</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="price"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>単価（円）</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        placeholder="300000"
                        min="0"
                        value={field.value ?? ""}
                        onChange={(e) => {
                          const value = e.target.value;
                          field.onChange(value === "" ? undefined : Number(value));
                        }}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>説明</FormLabel>
                  <FormControl>
                    <Input placeholder="カタログの詳細説明" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={isSubmitting}
              >
                キャンセル
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "保存中..." : catalog ? "更新" : "作成"}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
