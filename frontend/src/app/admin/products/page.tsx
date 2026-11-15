"use client";

import React, { useEffect, useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Skeleton } from "@/components/ui/skeleton";
import { ProductFormSheet } from "@/components/admin/product-form-sheet";
import { AdminAPI } from "@/services/admin.service";
import { AdminProduct, AdminProductCreatePayload } from "@/types/admin";
import { Plus, RefreshCw, Briefcase, ShieldCheck, AlertCircle } from "lucide-react";

export default function AdminProductsPage() {
  const [products, setProducts] = useState<AdminProduct[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSheetOpen, setIsSheetOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadProducts = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await AdminAPI.listProducts();
      setProducts(data);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to load insurance products.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  const handleCreateProduct = async (payload: AdminProductCreatePayload) => {
    await AdminAPI.createProduct(payload);
    await loadProducts();
  };

  const handleToggleStatus = async (product: AdminProduct) => {
    try {
      const nextStatus = !product.is_active;
      await AdminAPI.toggleProductStatus(product.id, nextStatus);
      setProducts((prev) =>
        prev.map((p) => (p.id === product.id ? { ...p, is_active: nextStatus } : p))
      );
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to toggle product status.");
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Insurance Product Catalog & Pricing Matrices"
        description="Configure product categories, coverage parameters, rate matrices, and underwriting rules."
        breadcrumbs={[
          { label: "Admin Portal", href: "/admin" },
          { label: "Product Management" },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={loadProducts} disabled={isLoading}>
              <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" onClick={() => setIsSheetOpen(true)}>
              <Plus className="w-3.5 h-3.5 mr-1.5" />
              Add Insurance Plan
            </Button>
          </div>
        }
      />

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-lg text-sm text-rose-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      {/* Products Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-64 rounded-lg bg-slate-100" />
          ))
        ) : products.length === 0 ? (
          <div className="col-span-3 p-12 text-center text-slate-400">
            No products found in the catalog. Click &quot;Add Insurance Plan&quot; to configure your first plan.
          </div>
        ) : (
          products.map((p) => (
            <Card key={p.id} className="bg-white border-slate-200 shadow-sm flex flex-col justify-between hover:border-slate-300 transition-colors">
              <CardHeader className="p-5 pb-3">
                <div className="flex items-center justify-between mb-2">
                  <Badge variant="outline" className="text-xs capitalize font-medium">
                    {p.category.replace("_", " ")}
                  </Badge>
                  <div className="flex items-center gap-2">
                    <Switch
                      checked={p.is_active}
                      onCheckedChange={() => handleToggleStatus(p)}
                    />
                    <span className={`text-xs font-semibold ${p.is_active ? "text-emerald-700" : "text-slate-400"}`}>
                      {p.is_active ? "Active" : "Archived"}
                    </span>
                  </div>
                </div>
                <CardTitle className="text-base font-bold text-slate-900 leading-snug">
                  {p.name}
                </CardTitle>
                <CardDescription className="text-xs text-slate-500 line-clamp-2 mt-1">
                  {p.description || "Comprehensive insurance protection plan."}
                </CardDescription>
              </CardHeader>

              <CardContent className="p-5 pt-0 space-y-4">
                <div className="p-3 bg-slate-50/70 rounded-lg space-y-2 border border-slate-100 text-xs">
                  <div className="flex items-center justify-between text-slate-600">
                    <span>Sum Assured Range:</span>
                    <span className="font-semibold text-slate-900">
                      ₹{(p.min_sum_assured / 100000).toFixed(0)}L – ₹{(p.max_sum_assured / 100000).toFixed(0)}L
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-slate-600">
                    <span>Eligible Age:</span>
                    <span className="font-semibold text-slate-900">
                      {p.min_age} – {p.max_age} years
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-slate-600">
                    <span>Base Monthly Premium:</span>
                    <span className="font-bold text-blue-600">
                      From ₹{p.base_premium.toLocaleString()}/mo
                    </span>
                  </div>
                </div>

                {p.benefits_list && p.benefits_list.length > 0 && (
                  <div className="space-y-1">
                    <p className="text-[11px] font-semibold text-slate-400 uppercase">Highlights</p>
                    <div className="flex flex-wrap gap-1">
                      {p.benefits_list.slice(0, 2).map((b, i) => (
                        <span key={i} className="text-[11px] px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                          {b}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>

      <ProductFormSheet
        isOpen={isSheetOpen}
        onClose={() => setIsSheetOpen(false)}
        onSubmit={handleCreateProduct}
      />
    </div>
  );
}
