export interface SelectedRiderItem {
  rider_code: string;
  rider_name: string;
  rate_per_k: number;
  annual_cost: number;
}

export interface QuoteCalculationBreakdown {
  matrix_version: string;
  pricing_source: string;
  age_band: string;
  base_annual_rate_per_k: number;
  sum_assured: number;
  factors: {
    gender_multiplier: number;
    smoker_loading_factor: number;
    health_tier_factor: number;
    frequency_multiplier: number;
  };
  annual_amounts: {
    base_premium: number;
    health_loading: number;
    rider_premium: number;
    net_premium: number;
  };
  installment_amounts: {
    payment_frequency: string;
    net_installment_premium: number;
    tax_rate_percent: number;
    tax_amount: number;
    total_premium_payable: number;
  };
  rider_breakdown: SelectedRiderItem[];
}

export interface QuoteItem {
  id: string;
  quote_number: string;
  customer_id: string;
  product_id: string;
  configuration_id?: number | null;
  pricing_matrix_version: string;
  sum_assured: number;
  policy_term_years: number;
  payment_frequency: "monthly" | "quarterly" | "half_yearly" | "annually";
  selected_riders_json?: SelectedRiderItem[] | null;
  base_premium: number;
  health_loading_amount: number;
  rider_premium: number;
  net_premium: number;
  tax_amount: number;
  total_premium: number;
  calculation_breakdown_json?: QuoteCalculationBreakdown | null;
  expires_at: string;
  status: string;
  created_at: string;
  disclaimer: string;

  // Enriched fields
  product?: {
    id: string;
    code: string;
    name: string;
    category: string;
    insurer_name?: string;
  };
}

export interface QuoteCreatePayload {
  product_id: string;
  configuration_id?: number | null;
  sum_assured: number;
  policy_term_years: number;
  payment_frequency: "monthly" | "quarterly" | "half_yearly" | "annually";
  selected_rider_codes?: string[];
}

export interface QuoteRecalculatePayload {
  sum_assured: number;
  policy_term_years: number;
  payment_frequency: "monthly" | "quarterly" | "half_yearly" | "annually";
  selected_rider_codes?: string[];
}

