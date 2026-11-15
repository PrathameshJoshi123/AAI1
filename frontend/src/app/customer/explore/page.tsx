"use client";

import * as React from "react";
import Link from "next/link";
import { Compass, ShieldCheck, Heart, Car, Activity, ArrowRight, Search, CheckCircle2 } from "lucide-react";
import { PageHeader } from "@/components/shared/page-header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { CustomerAPI } from "@/services/customer-api";
import { InsuranceProductItem } from "@/types/customer";

export default function CustomerExplorePage() {
  const [products, setProducts] = React.useState<InsuranceProductItem[]>([]);
  const [selectedCategory, setSelectedCategory] = React.useState<string>("all");
  const [searchQuery, setSearchQuery] = React.useState<string>("");
  const [loading, setLoading] = React.useState<boolean>(true);

  React.useEffect(() => {
    async function loadProducts() {
      try {
        const list = await CustomerAPI.listProducts();
        if (Array.isArray(list)) {
          setProducts(list);
        }
      } catch (err) {
        console.error("Products load error:", err);
      } finally {
        setLoading(false);
      }
    }
    loadProducts();
  }, []);

  const filteredProducts = React.useMemo(() => {
    return products.filter((p) => {
      const matchCat =
        selectedCategory === "all" ||
        p.category.toLowerCase().includes(selectedCategory.toLowerCase());
      const matchQuery =
        !searchQuery ||
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.code.toLowerCase().includes(searchQuery.toLowerCase());
      return matchCat && matchQuery;
    });
  }, [products, selectedCategory, searchQuery]);

  const categories = [
    { id: "all", label: "All Products" },
    { id: "term_life", label: "Term Life" },
    { id: "health", label: "Health & Family" },
    { id: "motor", label: "Motor Insurance" },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Insurance Product Catalog"
        description="Explore approved insurance categories. Calculate indicative pricing with our AI assistant."
        breadcrumbs={[
          { label: "Customer Portal", href: "/customer" },
          { label: "Explore Plans" },
        ]}
        actions={
          <Button size="sm" asChild className="bg-blue-600 hover:bg-blue-700 text-white">
            <Link href="/customer/chat">
              <Compass className="h-4 w-4 mr-1.5" />
              AI Plan Matcher
            </Link>
          </Button>
        }
      />

      {/* Category Pills & Search */}
      <div className="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center justify-between">
        <div className="flex flex-wrap gap-1.5 border border-slate-200 bg-white p-1 rounded-lg">
          {categories.map((c) => (
            <button
              key={c.id}
              onClick={() => setSelectedCategory(c.id)}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                selectedCategory === c.id
                  ? "bg-blue-600 text-white shadow-2xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
              }`}
            >
              {c.label}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-72">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-400" />
          <Input
            placeholder="Search plans by name, code..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8 text-xs bg-white border-slate-200"
          />
        </div>
      </div>

      {/* Product Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {filteredProducts.length === 0 ? (
          <div className="col-span-3 text-center py-12 border border-dashed border-slate-200 rounded-xl bg-white">
            <Compass className="h-8 w-8 text-slate-400 mx-auto mb-2" />
            <h4 className="text-sm font-semibold text-slate-800">No matching plans found</h4>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              Try adjusting your category filter or search keywords, or ask our AI Advisor for recommendations.
            </p>
            <Button size="sm" variant="outline" className="mt-4" onClick={() => { setSelectedCategory("all"); setSearchQuery(""); }}>
              Reset Filters
            </Button>
          </div>
        ) : (
          filteredProducts.map((item) => {
            const isLife = item.category === "term_life";
            const isHealth = item.category === "health";
            const Icon = isLife ? Heart : isHealth ? Activity : Car;
            const defaultSum = item.configurations?.[0]?.min_sum_assured || (isLife ? 2500000 : 500000);
            const defaultTerm = item.configurations?.[0]?.term_options_json?.[0] || (isLife ? 20 : 1);

            return (
              <Card key={item.id} className="flex flex-col justify-between hover:border-blue-200 transition-colors bg-white border-slate-200 shadow-2xs">
                <CardHeader className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Badge variant={isLife ? "default" : isHealth ? "info" : "outline"} className="text-[11px] capitalize">
                      {item.category.replace(/_/g, " ")}
                    </Badge>
                    <div className="p-1.5 rounded-full bg-slate-50 border border-slate-100">
                      <Icon className="h-4 w-4 text-blue-600" />
                    </div>
                  </div>
                  <CardTitle className="text-base font-semibold text-slate-900">{item.name}</CardTitle>
                  <CardDescription className="text-xs text-slate-600 leading-relaxed min-h-[40px]">
                    {item.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-2 text-xs">
                  <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                    Key Protections:
                  </div>
                  <ul className="space-y-1.5">
                    <li className="flex items-center text-slate-700">
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 mr-2 shrink-0" />
                      <span>Compliant with IRDAI product standards</span>
                    </li>
                    <li className="flex items-center text-slate-700">
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 mr-2 shrink-0" />
                      <span>Actuarially approved indicative pricing</span>
                    </li>
                    <li className="flex items-center text-slate-700">
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 mr-2 shrink-0" />
                      <span>Digital KYC & paperless proposal onboarding</span>
                    </li>
                  </ul>
                </CardContent>
                <CardFooter className="pt-2 border-t border-slate-100 flex flex-col gap-2">
                  <div className="flex gap-2 w-full">
                    <Button variant="outline" size="sm" className="flex-1 text-xs" asChild>
                      <Link href={`/customer/needs-assessment?category=${item.category}`}>
                        Assess Eligibility
                      </Link>
                    </Button>
                    <Button size="sm" className="flex-1 text-xs bg-blue-600 hover:bg-blue-700 text-white" asChild>
                      <Link
                        href={`/customer/chat?product_id=${item.id}&product_name=${encodeURIComponent(
                          item.name
                        )}&category=${item.category}&action=quote`}
                      >
                        Get Quote <ArrowRight className="h-3 w-3 ml-1" />
                      </Link>
                    </Button>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-full text-[11px] text-blue-700 hover:text-blue-800 hover:bg-blue-50 h-7 justify-center font-medium"
                    asChild
                  >
                    <Link
                      href={`/customer/quotes?product_id=${item.id}&sum_assured=${defaultSum}&term=${defaultTerm}`}
                    >
                      ⚡ Instant Actuarial Quote (Direct)
                    </Link>
                  </Button>
                </CardFooter>
              </Card>
            );
          })
        )}
      </div>
    </div>
  );
}
