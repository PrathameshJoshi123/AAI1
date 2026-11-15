"use client";

import React, { useState } from "react";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetFooter } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { AdminProductCreatePayload } from "@/types/admin";

interface ProductFormSheetProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (payload: AdminProductCreatePayload) => Promise<void>;
}

export const ProductFormSheet: React.FC<ProductFormSheetProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [name, setName] = useState("");
  const [category, setCategory] = useState("term_life");
  const [description, setDescription] = useState("");
  const [basePremium, setBasePremium] = useState(499);
  const [minSum, setMinSum] = useState(2500000);
  const [maxSum, setMaxSum] = useState(20000000);
  const [minAge, setMinAge] = useState(18);
  const [maxAge, setMaxAge] = useState(65);
  const [benefits, setBenefits] = useState("Terminal Illness Benefit, Accidental Death Rider");
  const [exclusions, setExclusions] = useState("Pre-existing conditions (24m), Adventure sports");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !category) {
      setError("Please fill in the product name and category.");
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      await onSubmit({
        name,
        category,
        description: description || undefined,
        base_premium: Number(basePremium),
        min_sum_assured: Number(minSum),
        max_sum_assured: Number(maxSum),
        min_age: Number(minAge),
        max_age: Number(maxAge),
        is_active: true,
        benefits_list: benefits.split(",").map((s) => s.trim()).filter(Boolean),
        exclusions_list: exclusions.split(",").map((s) => s.trim()).filter(Boolean),
        required_declarations: ["Medical History", "Tobacco Usage", "Occupation Hazard"],
        required_documents: ["Identity Proof (Aadhaar/Passport)", "Income Proof (ITR/Form 16)"],
      });
      onClose();
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Failed to create insurance product.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent side="right" className="w-full sm:max-w-lg bg-white border-slate-200 overflow-y-auto">
        <SheetHeader>
          <SheetTitle className="text-lg font-bold text-slate-900">
            Configure Insurance Product
          </SheetTitle>
        </SheetHeader>

        <form onSubmit={handleSubmit} className="space-y-4 pt-4">
          {error && (
            <div className="p-3 text-xs bg-rose-50 text-rose-700 border border-rose-200 rounded-md">
              {error}
            </div>
          )}

          <div className="space-y-1">
            <Label className="text-xs">Product Name *</Label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Star Shield Pure Term Life"
              required
            />
          </div>

          <div className="space-y-1">
            <Label className="text-xs">Category *</Label>
            <Select value={category} onValueChange={setCategory}>
              <SelectTrigger>
                <SelectValue placeholder="Select category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="term_life">Term Life</SelectItem>
                <SelectItem value="health">Comprehensive Health</SelectItem>
                <SelectItem value="critical_illness">Critical Illness</SelectItem>
                <SelectItem value="motor">Private Motor</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1">
            <Label className="text-xs">Description</Label>
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Detailed product positioning and target customer segment"
              rows={3}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label className="text-xs">Min Sum Assured (₹)</Label>
              <Input
                type="number"
                value={minSum}
                onChange={(e) => setMinSum(Number(e.target.value))}
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Max Sum Assured (₹)</Label>
              <Input
                type="number"
                value={maxSum}
                onChange={(e) => setMaxSum(Number(e.target.value))}
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="space-y-1">
              <Label className="text-xs">Base Premium (₹)</Label>
              <Input
                type="number"
                value={basePremium}
                onChange={(e) => setBasePremium(Number(e.target.value))}
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Min Age</Label>
              <Input
                type="number"
                value={minAge}
                onChange={(e) => setMinAge(Number(e.target.value))}
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Max Age</Label>
              <Input
                type="number"
                value={maxAge}
                onChange={(e) => setMaxAge(Number(e.target.value))}
              />
            </div>
          </div>

          <div className="space-y-1">
            <Label className="text-xs">Key Policy Benefits (comma separated)</Label>
            <Textarea
              value={benefits}
              onChange={(e) => setBenefits(e.target.value)}
              rows={2}
            />
          </div>

          <div className="space-y-1">
            <Label className="text-xs">Exclusions (comma separated)</Label>
            <Textarea
              value={exclusions}
              onChange={(e) => setExclusions(e.target.value)}
              rows={2}
            />
          </div>

          <SheetFooter className="pt-4">
            <Button type="button" variant="outline" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white" disabled={isSubmitting}>
              {isSubmitting ? "Saving..." : "Save Product"}
            </Button>
          </SheetFooter>
        </form>
      </SheetContent>
    </Sheet>
  );
};

