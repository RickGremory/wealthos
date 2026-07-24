"""Mexico tax API smoke tests."""

from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from wealthos.core.database import SessionLocal
from wealthos.main import app

AUTH = "/api/v1/auth"
ME = "/api/v1/me"
ORG = "/api/v1/organizations"


@pytest.fixture()
def client() -> Generator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def _cleanup() -> Generator[None]:
    yield
    with SessionLocal() as session:
        session.execute(text("DELETE FROM mx_tax_payment_details"))
        session.execute(text("DELETE FROM mx_tax_calculation_snapshots"))
        session.execute(text("DELETE FROM mx_tax_withholdings"))
        session.execute(text("DELETE FROM mx_transaction_tax_details"))
        session.execute(text("DELETE FROM mx_tax_transaction_overrides"))
        session.execute(text("DELETE FROM mx_tax_category_mappings"))
        session.execute(text("DELETE FROM mx_tax_configurations"))
        session.execute(text("DELETE FROM tax_evidence"))
        session.execute(text("DELETE FROM tax_calculation_lines"))
        session.execute(text("DELETE FROM tax_calculations"))
        session.execute(text("DELETE FROM tax_payments"))
        session.execute(text("DELETE FROM tax_transaction_overrides"))
        session.execute(text("DELETE FROM tax_category_mappings"))
        session.execute(text("DELETE FROM tax_rule_categories"))
        session.execute(text("DELETE FROM tax_periods"))
        session.execute(text("DELETE FROM tax_rules"))
        session.execute(text("DELETE FROM tax_profiles"))
        session.execute(text("DELETE FROM debt_payments"))
        session.execute(text("DELETE FROM debts"))
        session.execute(text("DELETE FROM goal_manual_progress"))
        session.execute(text("DELETE FROM goal_accounts"))
        session.execute(text("DELETE FROM goals"))
        session.execute(text("DELETE FROM transaction_entries"))
        session.execute(text("DELETE FROM transactions"))
        session.execute(text("DELETE FROM categories"))
        session.execute(text("DELETE FROM accounts"))
        session.execute(text("DELETE FROM organization_memberships"))
        session.execute(text("DELETE FROM organizations"))
        session.execute(text("DELETE FROM users"))
        session.commit()


def _register(client: TestClient) -> dict:
    response = client.post(
        f"{AUTH}/register",
        json={
            "email": f"mx-{uuid4().hex[:8]}@example.com",
            "password": "WealthOS-2026-Segura",
            "display_name": "MX Taxes",
            "organization_name": "MX Org",
        },
    )
    assert response.status_code == 201, response.text
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    org_id = client.get(f"{ME}/organizations", headers=headers).json()["items"][0]["id"]
    return {"headers": headers, "org_id": org_id}


def test_mx_configuration_catalog_and_calculate(client: TestClient) -> None:
    user = _register(client)
    org_id = user["org_id"]
    headers = user["headers"]

    catalogs = client.get(f"{ORG}/{org_id}/taxes/mx/catalogs", headers=headers)
    assert catalogs.status_code == 200, catalogs.text
    assert any(item["code"] == "612" for item in catalogs.json()["catalogs"]["tax_regimes"])

    profile = client.post(
        f"{ORG}/{org_id}/tax-profiles",
        headers=headers,
        json={
            "country_code": "MX",
            "taxpayer_type": "individual",
            "filing_frequency": "monthly",
            "currency": "MXN",
        },
    )
    assert profile.status_code == 201, profile.text
    profile_id = profile.json()["id"]

    config = client.post(
        f"{ORG}/{org_id}/taxes/mx/configuration",
        headers=headers,
        json={
            "rfc": "XAXX010101000",
            "person_type": "individual",
            "tax_regime_code": "612",
            "vat_enabled": True,
            "income_tax_enabled": True,
            "default_vat_rate": "16.00",
            "income_tax_estimation": {
                "method": "configured_rate",
                "base": "gross_taxable_income",
                "rate": "10.00",
            },
            "requires_invoice_evidence": False,
            "effective_from": "2026-01-01",
            "tax_profile_id": profile_id,
        },
    )
    assert config.status_code == 201, config.text

    bank = client.post(
        f"{ORG}/{org_id}/accounts",
        headers=headers,
        json={
            "name": "BBVA",
            "account_type": "checking",
            "currency": "MXN",
            "opening_balance": "200000.00",
        },
    ).json()
    income_cat = next(
        item["id"]
        for item in client.get(
            f"{ORG}/{org_id}/categories", headers=headers, params={"type": "income"}
        ).json()["items"]
        if item["name"] == "Honorarios"
    )
    expense_cat = next(
        item["id"]
        for item in client.get(
            f"{ORG}/{org_id}/categories", headers=headers, params={"type": "expense"}
        ).json()["items"]
        if item["name"] == "Otros gastos"
    )

    for payload in (
        {
            "tax_profile_id": profile_id,
            "category_id": income_cat,
            "vat_treatment": "taxable",
            "income_treatment": "taxable",
        },
        {
            "tax_profile_id": profile_id,
            "category_id": expense_cat,
            "vat_treatment": "taxable",
            "expense_treatment": "deductible",
        },
    ):
        mapped = client.post(
            f"{ORG}/{org_id}/taxes/mx/category-mappings",
            headers=headers,
            json=payload,
        )
        assert mapped.status_code == 201, mapped.text

    income = client.post(
        f"{ORG}/{org_id}/transactions",
        headers=headers,
        json={
            "transaction_type": "income",
            "account_id": bank["id"],
            "category_id": income_cat,
            "amount": "116000.00",
            "description": "Honorarios con IVA",
            "occurred_at": datetime(2026, 7, 10, 12, 0, tzinfo=UTC).isoformat(),
        },
    )
    assert income.status_code == 201, income.text
    expense = client.post(
        f"{ORG}/{org_id}/transactions",
        headers=headers,
        json={
            "transaction_type": "expense",
            "account_id": bank["id"],
            "category_id": expense_cat,
            "amount": "34800.00",
            "description": "Gasto con IVA",
            "occurred_at": datetime(2026, 7, 12, 12, 0, tzinfo=UTC).isoformat(),
        },
    )
    assert expense.status_code == 201, expense.text

    with SessionLocal() as session:
        session.execute(
            text(
                """
                INSERT INTO mx_transaction_tax_details (
                    id, organization_id, transaction_id, subtotal, vat_amount,
                    withheld_income_tax, withheld_vat, other_taxes, total, currency,
                    calculation_source, created_at, updated_at
                ) VALUES
                (
                    :id1, :org, :tx1, 100000, 16000, 1000, 0, 0, 116000, 'MXN',
                    'manual', NOW(), NOW()
                ),
                (
                    :id2, :org, :tx2, 30000, 4800, 0, 0, 0, 34800, 'MXN',
                    'manual', NOW(), NOW()
                )
                """
            ),
            {
                "id1": str(uuid4()),
                "id2": str(uuid4()),
                "org": org_id,
                "tx1": income.json()["id"],
                "tx2": expense.json()["id"],
            },
        )
        session.commit()

    periods = client.get(
        f"{ORG}/{org_id}/tax-periods",
        headers=headers,
        params={"tax_profile_id": profile_id},
    )
    assert periods.status_code == 200, periods.text
    period_id = periods.json()["items"][0]["id"]

    calc = client.post(
        f"{ORG}/{org_id}/taxes/mx/periods/{period_id}/calculate",
        headers=headers,
    )
    assert calc.status_code == 200, calc.text
    body = calc.json()
    assert Decimal(str(body["income"]["taxable"])) == Decimal("100000.00")
    assert Decimal(str(body["vat"]["due"])) == Decimal("11200.00")
    assert Decimal(str(body["income_tax"]["due"])) == Decimal("9000.00")
    assert Decimal(str(body["estimated_total_due"])) == Decimal("20200.00")

    workpaper = client.get(
        f"{ORG}/{org_id}/taxes/mx/periods/{period_id}/workpaper",
        headers=headers,
    )
    assert workpaper.status_code == 200, workpaper.text
    assert workpaper.json()["is_stale"] is False
