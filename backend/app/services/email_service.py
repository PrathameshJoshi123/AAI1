"""Production-grade deterministic Email Notification Service for PS-21."""
import asyncio
from datetime import datetime, timezone
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import smtplib
import socket
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.auth import User
from app.models.base import utc_now
from app.models.email import EmailDeliveryLog, UserEmailPreference
from app.schemas.email import (
    EmailDeliveryLogRead,
    EmailDeliveryResult,
    PaginatedEmailLogsResponse,
    UserEmailPreferenceRead,
    UserEmailPreferenceUpdate,
)
from app.services.email_renderer import (
    render_application_status,
    render_document_action,
    render_followup_reminder,
    render_quote_summary,
    render_test_notification,
    render_underwriting_decision,
)

logger = logging.getLogger("app.services.email_service")


class EmailNotificationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_user_preference(self, user_id: str) -> UserEmailPreference:
        """Fetch or initialize default email preferences for a user."""
        stmt = select(UserEmailPreference).where(UserEmailPreference.user_id == user_id)
        res = await self.session.execute(stmt)
        pref = res.scalar_one_or_none()
        if not pref:
            # fetch user email
            user_stmt = select(User).where(User.id == user_id)
            user_res = await self.session.execute(user_stmt)
            user = user_res.scalar_one_or_none()
            email_addr = user.email if user else None

            pref = UserEmailPreference(
                user_id=user_id,
                notification_email=email_addr,
                quote_alerts=True,
                application_updates=True,
                document_requests=True,
                marketing_consent=False,
            )
            self.session.add(pref)
            await self.session.commit()
            await self.session.refresh(pref)
        return pref

    async def update_user_email(self, user_id: str, new_email: str) -> User:
        """Update user's primary email address and sync with notification preferences."""
        user_stmt = select(User).where(User.id == user_id)
        user_res = await self.session.execute(user_stmt)
        user = user_res.scalar_one_or_none()
        if not user:
            raise ValueError(f"User {user_id} not found.")

        # Check if email is already in use by another user
        conflict_stmt = select(User).where(User.email == new_email, User.id != user_id)
        conflict_res = await self.session.execute(conflict_stmt)
        if conflict_res.scalar_one_or_none():
            raise ValueError(f"Email address '{new_email}' is already registered to another account.")

        user.email = new_email

        # Also update notification preferences
        pref = await self.get_or_create_user_preference(user_id)
        pref.notification_email = new_email

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_user_preference(
        self, user_id: str, update_data: UserEmailPreferenceUpdate
    ) -> UserEmailPreferenceRead:
        """Update granular notification categories and consent timestamp."""
        pref = await self.get_or_create_user_preference(user_id)

        if update_data.notification_email is not None:
            pref.notification_email = str(update_data.notification_email)
        if update_data.quote_alerts is not None:
            pref.quote_alerts = update_data.quote_alerts
        if update_data.application_updates is not None:
            pref.application_updates = update_data.application_updates
        if update_data.document_requests is not None:
            pref.document_requests = update_data.document_requests
        if update_data.marketing_consent is not None:
            pref.marketing_consent = update_data.marketing_consent
            pref.consent_timestamp = utc_now() if update_data.marketing_consent else None

        await self.session.commit()
        await self.session.refresh(pref)
        return UserEmailPreferenceRead.model_validate(pref)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
        user_id: Optional[str] = None,
        category: str = "transactional",
    ) -> EmailDeliveryResult:
        """Render and asynchronously dispatch an email notification via SMTP with honest logging."""
        to_email = to_email.strip()

        # 1. Check user preferences & DPDP consent if user_id is provided
        if user_id:
            pref = await self.get_or_create_user_preference(user_id)
            if category == "marketing" and not pref.marketing_consent:
                log = EmailDeliveryLog(
                    user_id=user_id,
                    recipient_email=to_email,
                    subject=subject,
                    template_name=template_name,
                    status="SUPPRESSED_NO_CONSENT",
                    error_message="Recipient has not granted marketing email consent.",
                    payload_json=context,
                    sent_at=None,
                )
                self.session.add(log)
                await self.session.commit()
                return EmailDeliveryResult(
                    success=False,
                    status="SUPPRESSED_NO_CONSENT",
                    message="Dispatch suppressed: Customer has not granted active marketing/follow-up email consent.",
                    delivery_log_id=log.id,
                )

            if category == "quote" and not pref.quote_alerts:
                log = EmailDeliveryLog(
                    user_id=user_id,
                    recipient_email=to_email,
                    subject=subject,
                    template_name=template_name,
                    status="SUPPRESSED_USER_OPT_OUT",
                    error_message="Recipient opted out of quote alerts in preferences.",
                    payload_json=context,
                )
                self.session.add(log)
                await self.session.commit()
                return EmailDeliveryResult(
                    success=False,
                    status="SUPPRESSED_USER_OPT_OUT",
                    message="Dispatch suppressed: Customer opted out of quote notification emails.",
                    delivery_log_id=log.id,
                )

        # 2. Render HTML body deterministically
        if template_name == "quote_summary":
            html_content = render_quote_summary(context)
        elif template_name == "application_status":
            html_content = render_application_status(context)
        elif template_name == "document_action":
            html_content = render_document_action(context)
        elif template_name == "underwriting_decision":
            html_content = render_underwriting_decision(context)
        elif template_name == "followup_reminder":
            html_content = render_followup_reminder(context)
        elif template_name == "test_notification":
            html_content = render_test_notification(context)
        else:
            html_content = f"<p>{context.get('message', 'Notification from PS-21 Insurance.')}</p>"

        # 3. Check configuration honesty - AGENTS.md Rule 6: Never pretend notifications were sent
        smtp_host = getattr(settings, "SMTP_HOST", None)
        smtp_user = getattr(settings, "SMTP_USER", None)
        smtp_pass = getattr(settings, "SMTP_PASSWORD", None)

        is_placeholder = (
            not smtp_host
            or not smtp_user
            or "your_" in (smtp_user or "").lower()
            or "your_" in (smtp_pass or "").lower()
        )

        if is_placeholder:
            # Explicitly log unconfigured status without faking success
            log = EmailDeliveryLog(
                user_id=user_id,
                recipient_email=to_email,
                subject=subject,
                template_name=template_name,
                status="NOT_CONFIGURED",
                error_message="SMTP credentials (SMTP_HOST, SMTP_USER, SMTP_PASSWORD) are missing or placeholder in backend/.env.",
                payload_json=context,
            )
            self.session.add(log)
            await self.session.commit()
            await self.session.refresh(log)

            logger.warning(
                f"[EmailService] Notification to '{to_email}' recorded as NOT_CONFIGURED. SMTP is unconfigured."
            )
            return EmailDeliveryResult(
                success=False,
                status="NOT_CONFIGURED",
                message="SMTP service is unconfigured. The notification was logged to email_delivery_logs, but not sent over the network.",
                delivery_log_id=log.id,
                details={
                    "recipient": to_email,
                    "subject": subject,
                    "template": template_name,
                    "reason": "SMTP_USER or SMTP_PASSWORD is placeholder in backend/.env",
                },
            )

        # 4. Construct MIME Message
        effective_from = smtp_user if ("gmail.com" in (smtp_host or "").lower() and smtp_user) else settings.SMTP_FROM_EMAIL
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = email.utils.formataddr((settings.SMTP_FROM_NAME, effective_from))
        msg["To"] = to_email
        msg["Date"] = email.utils.formatdate(localtime=True)
        msg["Message-ID"] = email.utils.make_msgid(domain="ps21-insurance.com")

        # Text fallback & HTML
        plain_text = f"{subject}\n\nPlease view this message in an HTML-compatible email client."
        msg.attach(MIMEText(plain_text, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        # 5. Dispatch via SMTP synchronously in worker thread to prevent event loop blocking
        def _sync_smtp_dispatch() -> Tuple[bool, Optional[str]]:
            try:
                port = int(getattr(settings, "SMTP_PORT", 587))
                timeout = int(getattr(settings, "SMTP_TIMEOUT_SECONDS", 10))

                if port == 465:
                    server = smtplib.SMTP_SSL(smtp_host, port, timeout=timeout)
                else:
                    server = smtplib.SMTP(smtp_host, port, timeout=timeout)
                    server.ehlo()
                    if getattr(settings, "SMTP_USE_TLS", True):
                        server.starttls()
                        server.ehlo()

                if smtp_user and smtp_pass:
                    # Strip any cosmetic spaces from app passwords (e.g. Google 16-char app passwords)
                    clean_pass = smtp_pass.replace(" ", "") if ("gmail.com" in (smtp_host or "").lower()) else smtp_pass
                    server.login(smtp_user, clean_pass)

                sender_addr = smtp_user if ("gmail.com" in (smtp_host or "").lower() and smtp_user) else settings.SMTP_FROM_EMAIL
                server.sendmail(sender_addr, [to_email], msg.as_string())
                server.quit()
                return True, None
            except Exception as exc:
                return False, str(exc)

        # Run non-blocking in thread pool
        success, err = await asyncio.to_thread(_sync_smtp_dispatch)

        if success:
            log = EmailDeliveryLog(
                user_id=user_id,
                recipient_email=to_email,
                subject=subject,
                template_name=template_name,
                status="SENT",
                payload_json=context,
                sent_at=utc_now(),
            )
            self.session.add(log)
            await self.session.commit()
            await self.session.refresh(log)
            logger.info(f"[EmailService] Notification successfully sent to '{to_email}'.")
            return EmailDeliveryResult(
                success=True,
                status="SENT",
                message=f"Email notification successfully delivered to {to_email}.",
                delivery_log_id=log.id,
            )
        else:
            log = EmailDeliveryLog(
                user_id=user_id,
                recipient_email=to_email,
                subject=subject,
                template_name=template_name,
                status="FAILED",
                error_message=err,
                payload_json=context,
            )
            self.session.add(log)
            await self.session.commit()
            await self.session.refresh(log)
            logger.error(f"[EmailService] SMTP dispatch to '{to_email}' failed: {err}")
            return EmailDeliveryResult(
                success=False,
                status="FAILED",
                message=f"SMTP transmission failed: {err}",
                delivery_log_id=log.id,
                details={"error": err},
            )

    async def check_smtp_health(self) -> Dict[str, Any]:
        """Conduct live socket probe to inspect SMTP connectivity without faking success."""
        smtp_host = getattr(settings, "SMTP_HOST", None)
        smtp_port = int(getattr(settings, "SMTP_PORT", 587))
        smtp_user = getattr(settings, "SMTP_USER", None)

        if not smtp_host or not smtp_user or "your_" in (smtp_user or "").lower():
            return {
                "service_key": "email_smtp",
                "name": "Email Notification Engine",
                "category": "comms",
                "status": "not_configured",
                "details": "SMTP credentials (SMTP_HOST, SMTP_USER, SMTP_PASSWORD) are placeholder or unconfigured in backend/.env.",
                "endpoint_or_host": f"{smtp_host or 'None'}:{smtp_port}",
                "authenticated_user": smtp_user or "None",
            }

        # Perform live non-blocking TCP socket check
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(smtp_host, smtp_port), timeout=3.0
            )
            writer.close()
            await writer.wait_closed()
            return {
                "service_key": "email_smtp",
                "name": "Email Notification Engine",
                "category": "comms",
                "status": "active",
                "details": f"Live socket connection to {smtp_host}:{smtp_port} confirmed. Ready for outbound delivery.",
                "endpoint_or_host": f"{smtp_host}:{smtp_port}",
                "authenticated_user": smtp_user,
            }
        except Exception as e:
            return {
                "service_key": "email_smtp",
                "name": "Email Notification Engine",
                "category": "comms",
                "status": "error",
                "details": f"Could not establish TCP socket connection to {smtp_host}:{smtp_port}: {str(e)}",
                "endpoint_or_host": f"{smtp_host}:{smtp_port}",
                "authenticated_user": smtp_user,
            }

    async def list_delivery_logs(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> PaginatedEmailLogsResponse:
        """Query paginated delivery logs with optional filtering by status or recipient search."""
        query = select(EmailDeliveryLog)
        count_query = select(func.count(EmailDeliveryLog.id))

        if status:
            query = query.where(EmailDeliveryLog.status == status.upper())
            count_query = count_query.where(EmailDeliveryLog.status == status.upper())

        if search:
            search_pattern = f"%{search.strip()}%"
            query = query.where(
                (EmailDeliveryLog.recipient_email.ilike(search_pattern))
                | (EmailDeliveryLog.subject.ilike(search_pattern))
                | (EmailDeliveryLog.template_name.ilike(search_pattern))
            )
            count_query = count_query.where(
                (EmailDeliveryLog.recipient_email.ilike(search_pattern))
                | (EmailDeliveryLog.subject.ilike(search_pattern))
                | (EmailDeliveryLog.template_name.ilike(search_pattern))
            )

        # Count
        count_res = await self.session.execute(count_query)
        total = count_res.scalar() or 0

        # Items
        query = query.order_by(desc(EmailDeliveryLog.created_at)).offset((page - 1) * page_size).limit(page_size)
        items_res = await self.session.execute(query)
        items = items_res.scalars().all()

        return PaginatedEmailLogsResponse(
            total=total,
            page=page,
            page_size=page_size,
            items=[EmailDeliveryLogRead.model_validate(item) for item in items],
        )

