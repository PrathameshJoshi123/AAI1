"""Automated unit and integration tests for Phase 11 Email Notification Engine."""
import pytest
from tests.conftest import TestSessionLocal
from app.models.auth import User
from app.schemas.email import UserEmailPreferenceUpdate
from app.services.email_service import EmailNotificationService

pytestmark = pytest.mark.anyio


async def test_email_preference_get_and_update():
    """Test creating, fetching, and updating customer email notification preferences."""
    async with TestSessionLocal() as session:
        user = User(
            email="test_pref_user@example.com",
            hashed_password="hashed_pwd_placeholder",
            first_name="Anita",
            last_name="Roy",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        service = EmailNotificationService(session)
        pref = await service.get_or_create_user_preference(user.id)
        assert pref.user_id == user.id
        assert pref.quote_alerts is True
        assert pref.application_updates is True
        assert pref.marketing_consent is False

        # Update preferences
        updated = await service.update_user_preference(
            user.id,
            UserEmailPreferenceUpdate(
                quote_alerts=False,
                marketing_consent=True,
            ),
        )
        assert updated.quote_alerts is False
        assert updated.marketing_consent is True
        assert updated.consent_timestamp is not None


async def test_user_email_provision_and_update():
    """Test user email provisioning and uniqueness checking."""
    async with TestSessionLocal() as session:
        user = User(
            email="initial_email@example.com",
            hashed_password="hashed_pwd_placeholder",
            first_name="Raj",
            last_name="Verma",
        )
        session.add(user)
        await session.commit()

        service = EmailNotificationService(session)
        updated_user = await service.update_user_email(user.id, "new_verified_email@example.com")
        assert updated_user.email == "new_verified_email@example.com"

        pref = await service.get_or_create_user_preference(user.id)
        assert pref.notification_email == "new_verified_email@example.com"


async def test_honest_unconfigured_smtp_logging():
    """Ensure that when SMTP is unconfigured, system does NOT fake success (AGENTS.md Rule 6)."""
    async with TestSessionLocal() as session:
        service = EmailNotificationService(session)
        result = await service.send_email(
            to_email="prospect@example.com",
            subject="Test Quote Summary",
            template_name="quote_summary",
            context={
                "customer_name": "Prospect Test",
                "quote_number": "QT-9999",
                "coverage_amount": "₹25,00,000",
                "final_premium": "₹8,500",
            },
            category="quote",
        )

        assert result.success is False
        assert result.status == "NOT_CONFIGURED"
        assert "SMTP service is unconfigured" in result.message
        assert result.delivery_log_id is not None

        logs_res = await service.list_delivery_logs(page=1, page_size=10)
        assert logs_res.total >= 1
        recent_log = logs_res.items[0]
        assert recent_log.recipient_email == "prospect@example.com"
        assert recent_log.status == "NOT_CONFIGURED"


async def test_marketing_consent_suppression():
    """Ensure outreach is suppressed if the customer has not granted DPDP marketing consent."""
    async with TestSessionLocal() as session:
        user = User(
            email="consent_test_user@example.com",
            hashed_password="hashed_pwd_placeholder",
            first_name="Pooja",
            last_name="Mehta",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        service = EmailNotificationService(session)
        pref = await service.get_or_create_user_preference(user.id)
        assert pref.marketing_consent is False

        result = await service.send_email(
            to_email=user.email,
            subject="Special Renewal Offer",
            template_name="marketing_offer",
            context={"message": "Save 15% on insurance"},
            user_id=user.id,
            category="marketing",
        )

        assert result.success is False
        assert result.status == "SUPPRESSED_NO_CONSENT"
        assert "Customer has not granted active marketing" in result.message
