"""Automated tests for Strict Customer Data Isolation and Scoping Guardrails."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_cross_customer_quote_isolation(
    client: AsyncClient,
    customer_token: dict,
    customer_b_token: dict,
):
    # 1. Fetch available products
    prod_resp = await client.get("/api/v1/products")
    products = prod_resp.json()["data"]
    product_id = products[0]["id"]

    # 2. Customer A generates a quote
    quote_payload = {
        "product_id": product_id,
        "sum_assured": 150000.0,
        "policy_term_years": 20,
        "payment_frequency": "monthly",
    }
    create_resp = await client.post("/api/v1/quotes", json=quote_payload, headers=customer_token)
    assert create_resp.status_code == 201
    quote = create_resp.json()["data"]
    quote_number = quote["quote_number"]

    # Verify calculation: total_premium == base_premium + rider_premium + tax_amount
    assert round(quote["base_premium"] + quote["rider_premium"] + quote["tax_amount"], 2) == quote["total_premium"]

    # 3. Customer A can access their quote
    get_a_resp = await client.get(f"/api/v1/quotes/{quote_number}", headers=customer_token)
    assert get_a_resp.status_code == 200
    assert get_a_resp.json()["data"]["quote_number"] == quote_number

    # 4. Customer B tries to access Customer A's quote -> MUST BE FORBIDDEN (403)
    get_b_resp = await client.get(f"/api/v1/quotes/{quote_number}", headers=customer_b_token)
    assert get_b_resp.status_code == 403
    assert get_b_resp.json()["error"]["code"] == "PERMISSION_DENIED"

    # 5. Customer B tries to submit an application using Customer A's quote -> MUST BE FORBIDDEN (403)
    app_payload = {
        "quote_id": quote["id"],
        "proposal_data": {"beneficiary": "Fraudulent Claim"},
    }
    app_b_resp = await client.post("/api/v1/applications", json=app_payload, headers=customer_b_token)
    assert app_b_resp.status_code == 403
    assert app_b_resp.json()["error"]["code"] == "PERMISSION_DENIED"

    # 6. Customer A submits application -> Succeeded (201)
    app_a_resp = await client.post("/api/v1/applications", json=app_payload, headers=customer_token)
    assert app_a_resp.status_code == 201
    assert app_a_resp.json()["data"]["status"] == "submitted"

