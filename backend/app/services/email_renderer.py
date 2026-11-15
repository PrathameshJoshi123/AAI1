"""Deterministic HTML and plain-text email template renderer for PS-21."""
from typing import Any, Dict


def render_base_layout(content_html: str, preview_text: str = "") -> str:
    """Wraps body content in a responsive, enterprise fintech white-and-blue email shell."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PS-21 Insurance</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background-color: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      color: #0f172a;
      -webkit-font-smoothing: antialiased;
    }}
    .email-container {{
      max-width: 600px;
      margin: 24px auto;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .header {{
      background-color: #ffffff;
      padding: 24px 32px;
      border-bottom: 2px solid #2563eb;
    }}
    .header-title {{
      font-size: 20px;
      font-weight: 700;
      color: #1e3a8a;
      margin: 0;
      letter-spacing: -0.5px;
    }}
    .header-sub {{
      font-size: 12px;
      color: #64748b;
      margin-top: 4px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .body {{
      padding: 32px;
      font-size: 15px;
      line-height: 1.6;
      color: #334155;
    }}
    .badge {{
      display: inline-block;
      padding: 4px 10px;
      font-size: 12px;
      font-weight: 600;
      border-radius: 9999px;
      background-color: #eff6ff;
      color: #2563eb;
      border: 1px solid #bfdbfe;
    }}
    .info-box {{
      background-color: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 18px;
      margin: 20px 0;
    }}
    .info-row {{
      display: flex;
      justify-content: space-between;
      padding: 6px 0;
      border-bottom: 1px solid #f1f5f9;
      font-size: 14px;
    }}
    .info-row:last-child {{
      border-bottom: none;
    }}
    .info-label {{
      color: #64748b;
    }}
    .info-value {{
      font-weight: 600;
      color: #0f172a;
    }}
    .cta-button {{
      display: inline-block;
      background-color: #2563eb;
      color: #ffffff !important;
      font-weight: 600;
      font-size: 15px;
      padding: 12px 28px;
      border-radius: 6px;
      text-decoration: none;
      margin: 20px 0;
    }}
    .footer {{
      background-color: #f8fafc;
      padding: 20px 32px;
      font-size: 12px;
      color: #94a3b8;
      border-top: 1px solid #e2e8f0;
      text-align: center;
      line-height: 1.5;
    }}
    .footer a {{
      color: #64748b;
      text-decoration: underline;
    }}
  </style>
</head>
<body>
  <div style="display:none;font-size:1px;color:#333333;line-height:1px;max-height:0px;max-width:0px;opacity:0;overflow:hidden;">
    {preview_text}
  </div>
  <div class="email-container">
    <div class="header">
      <div class="header-title">PS-21 Insurance</div>
      <div class="header-sub">Conversational Protection & Onboarding</div>
    </div>
    <div class="body">
      {content_html}
    </div>
    <div class="footer">
      This is a regulated transaction notification from PS-21 Insurance Platform.<br>
      In compliance with IRDAI regulations and DPDP Act 2023.<br>
      To manage your notification preferences, visit your customer profile.
    </div>
  </div>
</body>
</html>"""


def render_quote_summary(context: Dict[str, Any]) -> str:
    """Renders indicative quote summary email."""
    name = context.get("customer_name", "Valued Customer")
    quote_number = context.get("quote_number", "QT-0000")
    product_name = context.get("product_name", "Comprehensive Policy")
    coverage_amount = context.get("coverage_amount", "₹50,00,000")
    base_premium = context.get("base_premium", "₹12,400")
    tax_amount = context.get("tax_amount", "₹2,232")
    final_premium = context.get("final_premium", "₹14,632")
    frequency = context.get("payment_frequency", "Annual")
    portal_url = context.get("portal_url", "http://localhost:3000/customer/quotes")

    body = f"""
    <div style="margin-bottom: 16px;">
      <span class="badge">Official Indicative Quote</span>
    </div>
    <h2 style="font-size: 20px; color: #0f172a; margin-top: 0;">Hello {name},</h2>
    <p>Thank you for exploring your insurance coverage options with PS-21. Here is your official indicative quotation summary:</p>

    <div class="info-box">
      <div class="info-row">
        <span class="info-label">Quote Number:</span>
        <span class="info-value">{quote_number}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Selected Plan:</span>
        <span class="info-value">{product_name}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Coverage (Sum Assured):</span>
        <span class="info-value">{coverage_amount}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Payment Frequency:</span>
        <span class="info-value">{frequency}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Base Premium:</span>
        <span class="info-value">{base_premium}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Statutory GST (18%):</span>
        <span class="info-value">{tax_amount}</span>
      </div>
      <div class="info-row" style="font-size: 16px; font-weight: 700; color: #1e3a8a; border-top: 2px solid #e2e8f0; padding-top: 10px;">
        <span class="info-label" style="color: #1e3a8a; font-weight: 700;">Total Payable:</span>
        <span class="info-value" style="color: #1e3a8a; font-size: 18px;">{final_premium}</span>
      </div>
    </div>

    <p style="font-size: 13px; color: #64748b;">
      * Note: Indicative quote generated deterministically by the PS-21 Actuarial Engine based on your age, tobacco status, and selected coverage. Final premium is subject to formal underwriting review.
    </p>

    <div style="text-align: center; margin-top: 28px;">
      <a href="{portal_url}" class="cta-button">Review Quote & Begin Onboarding</a>
    </div>
    """
    return render_base_layout(body, f"Your Indicative Insurance Quote {quote_number} is ready.")


def render_application_status(context: Dict[str, Any]) -> str:
    """Renders application status mutation update email."""
    name = context.get("customer_name", "Valued Customer")
    app_number = context.get("application_number", "APP-0000")
    product_name = context.get("product_name", "Insurance Policy")
    status = context.get("status", "Under Review").replace("_", " ").title()
    remarks = context.get("remarks", "Your application is progressing through our underwriting queue.")
    portal_url = context.get("portal_url", "http://localhost:3000/customer/applications")

    body = f"""
    <div style="margin-bottom: 16px;">
      <span class="badge">Application Update</span>
    </div>
    <h2 style="font-size: 20px; color: #0f172a; margin-top: 0;">Hello {name},</h2>
    <p>There is an update on your insurance application for <strong>{product_name}</strong>.</p>

    <div class="info-box">
      <div class="info-row">
        <span class="info-label">Application Number:</span>
        <span class="info-value">{app_number}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Current Status:</span>
        <span class="info-value" style="color: #2563eb;">{status}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Advisor Remarks:</span>
        <span class="info-value">{remarks}</span>
      </div>
    </div>

    <div style="text-align: center; margin-top: 28px;">
      <a href="{portal_url}" class="cta-button">View Application Status</a>
    </div>
    """
    return render_base_layout(body, f"Status Update for Application {app_number}: {status}")


def render_document_action(context: Dict[str, Any]) -> str:
    """Renders action required email for rejected or requested documents."""
    name = context.get("customer_name", "Valued Customer")
    app_number = context.get("application_number", "APP-0000")
    doc_type = context.get("document_type", "Identity Proof")
    reason = context.get("rejection_reason", "Document was illegible or incomplete.")
    instructions = context.get("instructions", "Please upload a clear, high-resolution copy.")
    portal_url = context.get("portal_url", "http://localhost:3000/customer/documents")

    body = f"""
    <div style="margin-bottom: 16px;">
      <span class="badge" style="background-color: #fff1f2; color: #e11d48; border-color: #fecdd3;">Action Required</span>
    </div>
    <h2 style="font-size: 20px; color: #0f172a; margin-top: 0;">Hello {name},</h2>
    <p>Our verification team reviewed the documents for application <strong>{app_number}</strong> and requires your attention.</p>

    <div class="info-box" style="border-left: 4px solid #e11d48;">
      <div class="info-row">
        <span class="info-label">Document:</span>
        <span class="info-value">{doc_type}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Issue Flagged:</span>
        <span class="info-value" style="color: #e11d48;">{reason}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Instructions:</span>
        <span class="info-value">{instructions}</span>
      </div>
    </div>

    <p>To avoid processing delays, please re-upload your document at your earliest convenience.</p>

    <div style="text-align: center; margin-top: 28px;">
      <a href="{portal_url}" class="cta-button">Upload Document</a>
    </div>
    """
    return render_base_layout(body, f"Action Required: Re-upload {doc_type} for Application {app_number}")


def render_underwriting_decision(context: Dict[str, Any]) -> str:
    """Renders formal human underwriting decision notice."""
    name = context.get("customer_name", "Valued Customer")
    app_number = context.get("application_number", "APP-0000")
    decision = context.get("decision", "Approved")
    product_name = context.get("product_name", "Insurance Plan")
    loading_percent = context.get("loading_percent", 0.0)
    decision_notes = context.get("decision_notes", "Your case has completed formal underwriting evaluation.")
    portal_url = context.get("portal_url", "http://localhost:3000/customer/applications")

    badge_color = "#10b981" if "approved" in decision.lower() else "#e11d48"

    body = f"""
    <div style="margin-bottom: 16px;">
      <span class="badge" style="color: {badge_color}; border-color: {badge_color}33;">Underwriting Decision</span>
    </div>
    <h2 style="font-size: 20px; color: #0f172a; margin-top: 0;">Hello {name},</h2>
    <p>A certified underwriter has completed the assessment of your insurance proposal for <strong>{product_name}</strong>.</p>

    <div class="info-box">
      <div class="info-row">
        <span class="info-label">Application Number:</span>
        <span class="info-value">{app_number}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Decision:</span>
        <span class="info-value" style="color: {badge_color}; font-weight: 700;">{decision}</span>
      </div>
      {f'<div class="info-row"><span class="info-label">Underwriting Loading:</span><span class="info-value">+{loading_percent}%</span></div>' if loading_percent > 0 else ''}
      <div class="info-row">
        <span class="info-label">Assessor Comments:</span>
        <span class="info-value">{decision_notes}</span>
      </div>
    </div>

    <div style="text-align: center; margin-top: 28px;">
      <a href="{portal_url}" class="cta-button">View Official Decision Letter</a>
    </div>
    """
    return render_base_layout(body, f"Underwriting Decision for Application {app_number}: {decision}")


def render_test_notification(context: Dict[str, Any]) -> str:
    """Renders diagnostic test email for admin verification."""
    target_email = context.get("recipient_email", "admin@ps21-insurance.com")
    host = context.get("smtp_host", "localhost")
    port = context.get("smtp_port", 587)
    now_str = context.get("timestamp", "")

    body = f"""
    <div style="margin-bottom: 16px;">
      <span class="badge">Integration Probe</span>
    </div>
    <h2 style="font-size: 20px; color: #0f172a; margin-top: 0;">Live SMTP Connectivity Test</h2>
    <p>This diagnostic email confirms that the PS-21 Email Notification Engine has successfully established connection and dispatched a message via SMTP.</p>

    <div class="info-box">
      <div class="info-row">
        <span class="info-label">Recipient:</span>
        <span class="info-value">{target_email}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Configured Host:</span>
        <span class="info-value">{host}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Port:</span>
        <span class="info-value">{port}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Handshake Timestamp:</span>
        <span class="info-value">{now_str}</span>
      </div>
    </div>
    """
    return render_base_layout(body, "PS-21 Email Notification Engine Live Probe")


def render_followup_reminder(context: Dict[str, Any]) -> str:
    """Renders empathetic, DPDP-compliant follow-up notification email."""
    name = context.get("target_name", "Valued Customer")
    advisor_name = context.get("advisor_name", "Your PS-21 Insurance Advisor")
    channel = context.get("channel", "call").upper()
    notes = context.get("notes", "Following up on your active insurance consultation and coverage questions.")
    due_date = context.get("due_date", "")

    body = f"""
    <div style="margin-bottom: 16px;">
      <span class="badge">Scheduled Follow-up</span>
    </div>
    <h2 style="font-size: 20px; color: #0f172a; margin-top: 0;">Consultation Follow-up from {advisor_name}</h2>
    <p>Dear {name},</p>
    <p>We are reaching out to help ensure your insurance coverage queries and application details are addressed at your convenience.</p>

    <div class="info-box">
      <div class="info-row">
        <span class="info-label">Assigned Advisor:</span>
        <span class="info-value">{advisor_name}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Follow-up Channel:</span>
        <span class="info-value">{channel}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Scheduled Time:</span>
        <span class="info-value">{due_date}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Purpose / Notes:</span>
        <span class="info-value">{notes}</span>
      </div>
    </div>

    <p style="margin-top: 24px; font-size: 13px; color: #64748b;">
      If you prefer not to receive reminder calls or wish to update your preferred contact channel, you can easily customize your preferences in your customer portal.
    </p>
    """
    return render_base_layout(body, f"PS-21 Scheduled Follow-up with {advisor_name}")


