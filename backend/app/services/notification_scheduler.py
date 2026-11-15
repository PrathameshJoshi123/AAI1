"""Background Notification and Follow-up Event Loop Scheduler."""
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.core.logging import logger
from app.models.profile import Advisor, Customer
from app.models.system import FollowUp, Notification
from app.models.application import Application
from app.services.email_service import EmailNotificationService


class NotificationSchedulerState:
    def __init__(self):
        self.is_running: bool = False
        self.interval_seconds: int = 5
        self.ticks_count: int = 0
        self.last_run_at: Optional[datetime] = None
        self.total_dispatched: int = 0
        self.last_run_summary: Dict[str, Any] = {}


scheduler_state = NotificationSchedulerState()


async def process_followup_and_system_notifications() -> Dict[str, Any]:
    """Execute one scan of due follow-ups, SLA countdowns, and pending items."""
    scheduler_state.ticks_count += 1
    scheduler_state.last_run_at = datetime.now(timezone.utc)

    notifications_created = 0
    now = datetime.now(timezone.utc)

    async with AsyncSessionLocal() as session:
        try:
            # 1. Query pending follow-ups that are due (due_date <= now)
            stmt = (
                select(FollowUp)
                .options(
                    selectinload(FollowUp.assigned_advisor).selectinload(Advisor.user),
                    selectinload(FollowUp.customer).selectinload(Customer.user),
                    selectinload(FollowUp.prospect),
                )
                .where(
                    FollowUp.status == "pending",
                    FollowUp.due_date <= now,
                )
            )
            res = await session.execute(stmt)
            due_followups = res.scalars().all()

            for fu in due_followups:
                # Determine target contact name and advisor name
                target_name = "Prospect"
                if fu.customer and fu.customer.user:
                    target_name = f"{fu.customer.user.first_name or ''} {fu.customer.user.last_name or ''}".strip() or "Valued Customer"
                elif fu.prospect:
                    target_name = fu.prospect.full_name or "Prospect"

                advisor_name = "Your Assigned Insurance Advisor"
                if fu.assigned_advisor and fu.assigned_advisor.user:
                    adv_u = fu.assigned_advisor.user
                    advisor_name = f"{adv_u.first_name or ''} {adv_u.last_name or ''}".strip() or "Your Assigned Insurance Advisor"

                due_date_str = fu.due_date.strftime("%Y-%m-%d %H:%M UTC") if fu.due_date else ""

                # 1. Check & notify Advisor (In-App + Email)
                if fu.assigned_advisor and fu.assigned_advisor.user_id:
                    advisor_uid = fu.assigned_advisor.user_id
                    notif_stmt = select(Notification.id).where(
                        Notification.user_id == advisor_uid,
                        Notification.link_url == f"/advisor/follow-ups?id={fu.id}",
                    )
                    existing_notif = (await session.execute(notif_stmt)).scalar_one_or_none()
                    if not existing_notif:
                        advisor_notif = Notification(
                            user_id=advisor_uid,
                            title=f"Follow-up Due: {target_name}",
                            message=f"Follow-up task via {fu.channel.upper()} for {target_name} is due now. Priority: {fu.priority.upper()}. {fu.notes or ''}".strip(),
                            notification_type="followup_reminder",
                            link_url=f"/advisor/follow-ups?id={fu.id}",
                        )
                        session.add(advisor_notif)
                        notifications_created += 1

                        # Dispatched via EmailNotificationService
                        if fu.assigned_advisor.user and fu.assigned_advisor.user.email:
                            try:
                                email_svc = EmailNotificationService(session)
                                await email_svc.send_email(
                                    to_email=fu.assigned_advisor.user.email,
                                    subject=f"[Alert] Follow-up Due: {target_name} ({fu.channel.upper()})",
                                    template_name="followup_reminder",
                                    context={
                                        "target_name": target_name,
                                        "advisor_name": advisor_name,
                                        "channel": fu.channel,
                                        "notes": fu.notes or "Scheduled follow-up reminder.",
                                        "due_date": due_date_str,
                                    },
                                    user_id=advisor_uid,
                                    category="transactional",
                                )
                            except Exception as em_err:
                                logger.warning(f"[NotificationScheduler] Could not send advisor follow-up email: {em_err}")

                # 2. Check & notify Customer if registered (In-App + Email)
                if fu.customer and fu.customer.user_id:
                    cust_uid = fu.customer.user_id
                    cust_notif_stmt = select(Notification.id).where(
                        Notification.user_id == cust_uid,
                        Notification.link_url == f"/customer?followup={fu.id}",
                    )
                    existing_cust_notif = (await session.execute(cust_notif_stmt)).scalar_one_or_none()
                    if not existing_cust_notif:
                        cust_notif = Notification(
                            user_id=cust_uid,
                            title="Advisor Follow-up Scheduled",
                            message=f"Your insurance advisor has scheduled a follow-up via {fu.channel} regarding your application.",
                            notification_type="followup_reminder",
                            link_url=f"/customer?followup={fu.id}",
                        )
                        session.add(cust_notif)
                        notifications_created += 1

                        # Dispatched via EmailNotificationService
                        if fu.customer.user and fu.customer.user.email:
                            try:
                                email_svc = EmailNotificationService(session)
                                await email_svc.send_email(
                                    to_email=fu.customer.user.email,
                                    subject=f"Follow-up Consultation Scheduled: {advisor_name}",
                                    template_name="followup_reminder",
                                    context={
                                        "target_name": target_name,
                                        "advisor_name": advisor_name,
                                        "channel": fu.channel,
                                        "notes": fu.notes or "Your advisor will be contacting you for a scheduled consultation.",
                                        "due_date": due_date_str,
                                    },
                                    user_id=cust_uid,
                                    category="application_updates",
                                )
                            except Exception as em_err:
                                logger.warning(f"[NotificationScheduler] Could not send customer follow-up email: {em_err}")
                elif fu.prospect and fu.prospect.email:
                    # Also dispatch outreach email for prospect
                    try:
                        email_svc = EmailNotificationService(session)
                        await email_svc.send_email(
                            to_email=fu.prospect.email,
                            subject=f"Follow-up Consultation Scheduled: {advisor_name}",
                            template_name="followup_reminder",
                            context={
                                "target_name": target_name,
                                "advisor_name": advisor_name,
                                "channel": fu.channel,
                                "notes": fu.notes or "Your advisor will be contacting you for a scheduled consultation.",
                                "due_date": due_date_str,
                            },
                            category="marketing",
                        )
                    except Exception as em_err:
                        logger.warning(f"[NotificationScheduler] Could not send prospect follow-up email: {em_err}")

            # 2. Check for stalled applications requiring customer action (document re-uploads or more info)
            app_stmt = (
                select(Application)
                .options(selectinload(Application.customer))
                .where(Application.status == "requires_information")
            )
            app_res = await session.execute(app_stmt)
            stalled_apps = app_res.scalars().all()
            for app in stalled_apps:
                if app.customer and app.customer.user_id:
                    chk_stmt = select(Notification.id).where(
                        Notification.user_id == app.customer.user_id,
                        Notification.link_url == f"/customer/applications/{app.id}?reminder=1",
                    )
                    if not (await session.execute(chk_stmt)).scalar_one_or_none():
                        session.add(
                            Notification(
                                user_id=app.customer.user_id,
                                title="Action Required: Application Update Needed",
                                message=f"Application #{app.case_number} requires additional details or documents to continue underwriting.",
                                notification_type="alert",
                                link_url=f"/customer/applications/{app.id}?reminder=1",
                            )
                        )
                        notifications_created += 1

            # 3. AI Follow-up Coordination Agent Execution & Periodic Email Dispatch
            try:
                from app.ai.agents.definitions.followup_coordination_agent import (
                    FollowUpCoordinationAgent,
                    FollowUpCoordinationInput,
                )
                from app.models.auth import User

                # Fetch registered customers or active users to run the Follow-up Coordination Agent
                cust_stmt = (
                    select(Customer)
                    .options(selectinload(Customer.user))
                    .limit(5)
                )
                customers = (await session.execute(cust_stmt)).scalars().all()

                followup_agent = FollowUpCoordinationAgent()

                # Process customers
                targets = []
                for c in customers:
                    if c.user and c.user.email:
                        u_name = f"{c.user.first_name or ''} {c.user.last_name or ''}".strip() or "Valued Customer"
                        targets.append((c.id, c.user.id, c.user.email, u_name))

                # If no customers with users, fall back to any active users
                if not targets:
                    u_stmt = select(User).where(User.is_active == True).limit(3)
                    users = (await session.execute(u_stmt)).scalars().all()
                    for u in users:
                        if u.email:
                            u_name = f"{u.first_name or ''} {u.last_name or ''}".strip() or "Valued Customer"
                            targets.append((u.id, u.id, u.email, u_name))

                for target_cust_id, target_user_id, user_email, full_name in targets:
                    cust_name = full_name or "Valued Customer"

                    # 3a. Execute Follow-up Coordination Agent
                    subject = f"PS-21 Policy Follow-up: Important Update for {cust_name}"
                    notes_content = (
                        f"Hello {cust_name}, our AI Follow-up Coordination Agent noticed you have an active insurance session. "
                        f"We are here to help address your questions, customize riders, or finalize your proposal."
                    )

                    try:
                        agent_input = FollowUpCoordinationInput(
                            customer_id=str(target_cust_id),
                            preferred_channel="email",
                            last_interaction_type="active_policy_inquiry",
                            consent_active=True,
                            hours_since_inquiry=1,
                        )
                        plan = await followup_agent.run(agent_input, context={"user_id": str(target_user_id)})
                        if plan and plan.message_subject:
                            subject = plan.message_subject
                        if plan and plan.message_body_preview:
                            notes_content = plan.message_body_preview
                    except Exception as agent_err:
                        logger.info(f"[NotificationScheduler] Agent fallback used: {agent_err}")

                    # 3b. Dispatch Email via EmailNotificationService
                    try:
                        email_svc = EmailNotificationService(session)
                        due_now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                        await email_svc.send_email(
                            to_email=user_email,
                            subject=subject,
                            template_name="followup_reminder",
                            context={
                                "target_name": cust_name,
                                "advisor_name": "PS-21 Follow-up Coordination Agent",
                                "channel": "EMAIL",
                                "notes": notes_content,
                                "due_date": due_now_str,
                            },
                            user_id=target_user_id,
                            category="application_updates",
                        )
                    except Exception as email_err:
                        logger.warning(f"[NotificationScheduler] Could not send agent email to {user_email}: {email_err}")

                    # 3c. Create matching In-App Notification
                    session.add(
                        Notification(
                            user_id=target_user_id,
                            title=subject[:190],
                            message=notes_content,
                            notification_type="followup_reminder",
                            link_url="/customer",
                        )
                    )
                    notifications_created += 1
                    logger.info(f"[NotificationScheduler] Agent follow-up notification & email dispatched to {user_email}")

            except Exception as loop_agent_err:
                logger.error(f"[NotificationScheduler] Error running agent loop: {loop_agent_err}")

            if notifications_created > 0:
                await session.commit()
                scheduler_state.total_dispatched += notifications_created
                logger.info(
                    f"[NotificationScheduler] Dispatched {notifications_created} notifications in tick #{scheduler_state.ticks_count}"
                )

        except Exception as e:
            await session.rollback()
            logger.error(f"[NotificationScheduler] Error during execution tick: {e}", exc_info=True)

    summary = {
        "ticks_count": scheduler_state.ticks_count,
        "notifications_created": notifications_created,
        "total_dispatched": scheduler_state.total_dispatched,
        "timestamp": scheduler_state.last_run_at.isoformat() if scheduler_state.last_run_at else None,
    }
    scheduler_state.last_run_summary = summary
    return summary


async def start_notification_scheduler(interval_seconds: int = 5):
    """Event loop running every 5 seconds to process follow-ups and notifications."""
    scheduler_state.is_running = True
    scheduler_state.interval_seconds = interval_seconds
    logger.info(f"[NotificationScheduler] Started notification background event loop (interval: {interval_seconds}s)")

    try:
        while scheduler_state.is_running:
            await process_followup_and_system_notifications()
            await asyncio.sleep(interval_seconds)
    except asyncio.CancelledError:
        logger.info("[NotificationScheduler] Background event loop received cancel signal.")
    except Exception as e:
        logger.error(f"[NotificationScheduler] Unexpected error in event loop: {e}", exc_info=True)
    finally:
        scheduler_state.is_running = False
        logger.info("[NotificationScheduler] Background event loop has shut down.")


async def stop_notification_scheduler(task: Optional[asyncio.Task] = None):
    """Gracefully stop the notification scheduler."""
    scheduler_state.is_running = False
    if task and not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
