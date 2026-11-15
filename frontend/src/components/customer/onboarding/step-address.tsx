"use client";

import React from "react";
import { ContactAddressData } from "@/types/application";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { ArrowLeft, ArrowRight, MapPin } from "lucide-react";

interface StepAddressProps {
  initialData?: Partial<ContactAddressData>;
  onNext: (data: ContactAddressData) => void;
  onPrev: () => void;
}

export function StepAddress({ initialData, onNext, onPrev }: StepAddressProps) {
  const [formData, setFormData] = React.useState<ContactAddressData>({
    mobile_number: initialData?.mobile_number || "",
    email: initialData?.email || "",
    residential_address_line1: initialData?.residential_address_line1 || "",
    residential_address_line2: initialData?.residential_address_line2 || "",
    city: initialData?.city || "",
    state: initialData?.state || "Maharashtra",
    pincode: initialData?.pincode || "",
    is_permanent_same: initialData?.is_permanent_same ?? true,
  });
  const [error, setError] = React.useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!/^[6-9]\d{9}$/.test(formData.mobile_number)) {
      setError("Please provide a valid 10-digit Indian mobile number.");
      return;
    }
    if (!formData.email.includes("@")) {
      setError("Please provide a valid email address.");
      return;
    }
    if (formData.residential_address_line1.length < 5) {
      setError("Please enter a complete residential address.");
      return;
    }
    if (!/^[1-9][0-9]{5}$/.test(formData.pincode)) {
      setError("Please provide a valid 6-digit Indian PIN code.");
      return;
    }

    onNext(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="border-b border-slate-200 pb-3">
        <h3 className="text-base font-semibold text-slate-900 flex items-center gap-2">
          <MapPin className="w-5 h-5 text-blue-600" />
          Step 2: Contact Information & Residential Address
        </h3>
        <p className="text-xs text-slate-500 mt-1">
          Policy documents and statutory notices will be delivered to this verified communication address.
        </p>
      </div>

      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-md">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <Label htmlFor="mobile_number" className="text-xs font-medium text-slate-700">
            Primary Mobile Number *
          </Label>
          <Input
            id="mobile_number"
            value={formData.mobile_number}
            onChange={(e) => setFormData({ ...formData, mobile_number: e.target.value.replace(/\D/g, "") })}
            placeholder="9876543210"
            maxLength={10}
            required
            className="text-xs h-9 bg-white"
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="email" className="text-xs font-medium text-slate-700">
            Email Address *
          </Label>
          <Input
            id="email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            placeholder="rajesh.sharma@example.com"
            required
            className="text-xs h-9 bg-white"
          />
        </div>

        <div className="space-y-1.5 sm:col-span-2">
          <Label htmlFor="address1" className="text-xs font-medium text-slate-700">
            Residential Address (Line 1 - Flat / House No., Building Name) *
          </Label>
          <Input
            id="address1"
            value={formData.residential_address_line1}
            onChange={(e) => setFormData({ ...formData, residential_address_line1: e.target.value })}
            placeholder="Flat 402, Sunshine Heights, M.G. Road"
            required
            className="text-xs h-9 bg-white"
          />
        </div>

        <div className="space-y-1.5 sm:col-span-2">
          <Label htmlFor="address2" className="text-xs font-medium text-slate-700">
            Address Line 2 (Area, Landmark)
          </Label>
          <Input
            id="address2"
            value={formData.residential_address_line2}
            onChange={(e) => setFormData({ ...formData, residential_address_line2: e.target.value })}
            placeholder="Near HDFC Bank, Andheri West"
            className="text-xs h-9 bg-white"
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="city" className="text-xs font-medium text-slate-700">
            City *
          </Label>
          <Input
            id="city"
            value={formData.city}
            onChange={(e) => setFormData({ ...formData, city: e.target.value })}
            placeholder="Mumbai"
            required
            className="text-xs h-9 bg-white"
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="state" className="text-xs font-medium text-slate-700">
            State *
          </Label>
          <Input
            id="state"
            value={formData.state}
            onChange={(e) => setFormData({ ...formData, state: e.target.value })}
            placeholder="Maharashtra"
            required
            className="text-xs h-9 bg-white"
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="pincode" className="text-xs font-medium text-slate-700">
            Postal PIN Code *
          </Label>
          <Input
            id="pincode"
            value={formData.pincode}
            onChange={(e) => setFormData({ ...formData, pincode: e.target.value.replace(/\D/g, "") })}
            placeholder="400053"
            maxLength={6}
            required
            className="text-xs h-9 font-mono bg-white"
          />
        </div>

        <div className="sm:col-span-2 pt-2">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="is_permanent_same"
              checked={formData.is_permanent_same}
              onCheckedChange={(checked) => setFormData({ ...formData, is_permanent_same: !!checked })}
            />
            <Label htmlFor="is_permanent_same" className="text-xs text-slate-700 font-normal cursor-pointer">
              Permanent address is identical to current residential address
            </Label>
          </div>
        </div>
      </div>

      <div className="flex justify-between pt-4">
        <Button type="button" variant="outline" size="sm" onClick={onPrev} className="text-xs">
          <ArrowLeft className="w-3.5 h-3.5 mr-1" /> Previous Step
        </Button>
        <Button type="submit" size="sm" className="bg-blue-600 hover:bg-blue-700 text-white text-xs">
          Save & Next Step <ArrowRight className="w-3.5 h-3.5 ml-1" />
        </Button>
      </div>
    </form>
  );
}
