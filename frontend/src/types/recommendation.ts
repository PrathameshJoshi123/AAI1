export interface RecommendationItem {
  id: string;
  customer_id: string;
  conversation_id?: string | null;
  recommended_product_id: string;
  configuration_id?: number | null;
  match_score: number;
  recommended_sum_assured: number;
  recommended_term_years: number;
  rationale: string;
  match_factors_json?: Record<string, any> | null;
  assumptions_json?: string[] | null;
  limitations_json?: string[] | null;
  alternative_options_json?: Array<{
    tier_name: string;
    min_sum_assured: number;
    max_sum_assured: number;
  }> | null;
  status: string;
  created_at: string;

  // Enriched fields from product
  product_name?: string | null;
  product_code?: string | null;
  product_category?: string | null;
  insurer_name?: string | null;
  insurer_solvency_ratio?: number | null;
}

export interface RecommendationEvaluateResponse {
  recommendations: RecommendationItem[];
  primary_recommendation?: RecommendationItem | null;
  target_category: string;
  recommended_sum_assured: number;
  disclaimer: string;
}

export interface RecommendationExplanation {
  headline: string;
  why_it_fits: string[];
  key_assumptions: string[];
  critical_exclusions_to_note: string[];
  advisor_advice: string;
}

