"""Seed default lead sources and deterministic lead scoring rules using sqlite3."""
import json
import sqlite3
from datetime import datetime, timezone

DEFAULT_LEAD_SOURCES = [
    {"name": "web_direct", "channel_type": "web", "utm_campaign": None, "is_active": 1},
    {"name": "google_organic", "channel_type": "organic", "utm_campaign": "organic_search", "is_active": 1},
    {"name": "google_ads_term", "channel_type": "paid_search", "utm_campaign": "term_life_q4", "is_active": 1},
    {"name": "google_ads_health", "channel_type": "paid_search", "utm_campaign": "health_protect_q4", "is_active": 1},
    {"name": "partner_aggregator", "channel_type": "partner", "utm_campaign": "policy_compare", "is_active": 1},
    {"name": "mobile_app", "channel_type": "mobile", "utm_campaign": "app_onboarding", "is_active": 1},
]

DEFAULT_SCORING_RULES = [
    {
        "rule_code": "RULE_PROFILE_PHONE",
        "category": "profile",
        "rule_name": "Provided Verified Mobile Number",
        "description": "Visitor provided a valid phone number for contact verification",
        "point_value": 15,
        "condition_json": json.dumps({"field": "phone", "operator": "is_not_empty"}),
        "is_active": 1,
    },
    {
        "rule_code": "RULE_PROFILE_EMAIL",
        "category": "profile",
        "rule_name": "Provided Valid Email Address",
        "description": "Visitor provided a valid, format-verified email address",
        "point_value": 10,
        "condition_json": json.dumps({"field": "email", "operator": "is_not_empty"}),
        "is_active": 1,
    },
    {
        "rule_code": "RULE_PROFILE_NAME",
        "category": "profile",
        "rule_name": "Provided Full Legal Name",
        "description": "Visitor provided their first and last name",
        "point_value": 5,
        "condition_json": json.dumps({"field": "name", "operator": "is_not_empty"}),
        "is_active": 1,
    },
    {
        "rule_code": "RULE_INTENT_QUOTE_STARTED",
        "category": "intent",
        "rule_name": "Initiated Indicative Quote",
        "description": "Visitor launched the quote calculation engine for a specific product",
        "point_value": 25,
        "condition_json": json.dumps({"signal_type": "quote_attempt", "min_count": 1}),
        "is_active": 1,
    },
    {
        "rule_code": "RULE_INTENT_CALCULATOR_USED",
        "category": "intent",
        "rule_name": "Interacted with Coverage Calculator",
        "description": "Visitor adjusted coverage/tenure sliders to evaluate protection amounts",
        "point_value": 15,
        "condition_json": json.dumps({"signal_type": "coverage_calculator_used", "min_count": 1}),
        "is_active": 1,
    },
    {
        "rule_code": "RULE_INTENT_COMPARISON",
        "category": "intent",
        "rule_name": "Compared Multiple Plans",
        "description": "Visitor used the side-by-side policy comparison matrix",
        "point_value": 15,
        "condition_json": json.dumps({"signal_type": "comparison_viewed", "min_count": 1}),
        "is_active": 1,
    },
    {
        "rule_code": "RULE_ENGAGEMENT_DWELL_TIME",
        "category": "engagement",
        "rule_name": "High Page Dwell Engagement (>120s)",
        "description": "Cumulative engagement on product and discovery pages exceeds 120 seconds",
        "point_value": 10,
        "condition_json": json.dumps({"signal_type": "time_on_page", "min_duration_seconds": 120}),
        "is_active": 1,
    },
    {
        "rule_code": "RULE_ENGAGEMENT_MULTI_PAGE",
        "category": "engagement",
        "rule_name": "Explored 3+ Product Pages",
        "description": "Visitor explored at least 3 distinct insurance product pages",
        "point_value": 10,
        "condition_json": json.dumps({"signal_type": "page_view", "min_distinct_pages": 3}),
        "is_active": 1,
    },
    {
        "rule_code": "RULE_ENGAGEMENT_RETURN_VISIT",
        "category": "engagement",
        "rule_name": "Returned for Session Within 72 Hours",
        "description": "Visitor returned in a separate session within 72 hours",
        "point_value": 15,
        "condition_json": json.dumps({"min_sessions": 2, "max_gap_hours": 72}),
        "is_active": 1,
    },
    {
        "rule_code": "RULE_CONSENT_MARKETING",
        "category": "consent",
        "rule_name": "Granted Marketing & Advisory Consent",
        "description": "Explicit DPDP consent granted for advisory calls and notifications",
        "point_value": 10,
        "condition_json": json.dumps({"consent_type": "marketing_contact", "status": "granted"}),
        "is_active": 1,
    },
    {
        "rule_code": "RULE_CONSENT_REVOKED",
        "category": "penalty",
        "rule_name": "Consent Revocation Penalty",
        "description": "Penalty applied when a prospect explicitly revokes contact consent",
        "point_value": -50,
        "condition_json": json.dumps({"consent_type": "marketing_contact", "status": "revoked"}),
        "is_active": 1,
    },
    {
        "rule_code": "RULE_PENALTY_INACTIVITY_30D",
        "category": "penalty",
        "rule_name": "Inactivity for Over 30 Days",
        "description": "Dormancy penalty applied when no interactions recorded in 30 days",
        "point_value": -20,
        "condition_json": json.dumps({"days_inactive": 30}),
        "is_active": 1,
    },
]


def seed_lead_data_sync(db_path: str = "ps21_insurance.db"):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    now_str = datetime.now(timezone.utc).isoformat()

    # Seed Lead Sources
    for s in DEFAULT_LEAD_SOURCES:
        cur.execute("SELECT id FROM lead_sources WHERE name = ?", (s["name"],))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO lead_sources (name, channel_type, utm_campaign, is_active, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (s["name"], s["channel_type"], s["utm_campaign"], s["is_active"], now_str, now_str)
            )

    # Seed Scoring Rules
    for r in DEFAULT_SCORING_RULES:
        cur.execute("SELECT id FROM lead_scoring_rules WHERE rule_code = ?", (r["rule_code"],))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO lead_scoring_rules (rule_code, category, rule_name, description, point_value, condition_json, is_active, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (r["rule_code"], r["category"], r["rule_name"], r["description"], r["point_value"], r["condition_json"], r["is_active"], now_str, now_str)
            )

    con.commit()
    con.close()
    print("Lead sources and scoring rules seeded successfully.")


if __name__ == "__main__":
    seed_lead_data_sync()
