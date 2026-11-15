"""Compliance Monitoring Agent adhering to Section 13 of AGENTS.md."""
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.client.mistral_client import mistral_client
from app.ai.tools.agent_tools import LogComplianceAuditTool
from app.core.logging import logger


class ComplianceAuditInput(BaseModel):
    session_id: str
    workflow_step: str = "quote_presentation"
    messages_text: str
    quote_presented: bool = True
    disclaimer_present: bool = True


class ComplianceAuditResult(BaseModel):
    session_id: str
    is_compliant: bool = Field(description="Whether the interaction satisfies mandatory regulatory standards")
    missing_disclosures: List[str] = Field(description="List of mandated disclosures that were omitted")
    risk_severity: str = Field(description="None, Low, Medium, or High compliance risk")
    recommended_corrective_action: str = Field(description="Immediate remedial step required")


class ComplianceMonitoringAgent(BaseAgent):
    id = "compliance-monitoring-agent"
    name = "Compliance Monitoring Agent"
    description = "Monitors interactions for required regulatory disclosures, process violations, and fair conduct."
    purpose = "Guarantees regulatory adherence by verifying mandatory disclaimers and consumer protections."
    input_schema = ComplianceAuditInput
    output_schema = ComplianceAuditResult
    required_permissions = []
    registered_tools = [LogComplianceAuditTool()]
    temperature = 0.0

    async def run(self, input_data: ComplianceAuditInput, context: Dict[str, Any]) -> ComplianceAuditResult:
        missing = []
        if input_data.quote_presented and not input_data.disclaimer_present:
            missing.append("Mandatory disclaimer: 'Quotes are indicative and subject to medical underwriting approval'")

        prompt = (
            f"You are the Compliance Monitoring Officer AI for PS-21 Insurance.\n"
            f"Audit the following transaction step:\n"
            f"- Step: {input_data.workflow_step}\n"
            f"- Conversation/Output Content: {input_data.messages_text}\n"
            f"- Quote Issued: {input_data.quote_presented}\n"
            f"- Pre-flagged Missing Disclosures: {missing}\n\n"
            f"Requirements:\n"
            f"1. Check if 'indicative quote' or 'subject to underwriting' is clearly stated if pricing is mentioned.\n"
            f"2. Return strict JSON matching ComplianceAuditResult."
        )

        try:
            response = await mistral_client.chat(
                messages=[
                    {"role": "system", "content": "You are a regulatory compliance auditor AI for insurance. Return strict JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            content = response.get("content", "{}")
            result = ComplianceAuditResult.model_validate_json(content)

            # Log to audit trail
            audit_tool = LogComplianceAuditTool()
            tool_ctx = context.get("tool_context")
            await audit_tool.execute(
                tool_ctx,
                session_id=input_data.session_id,
                action_type=input_data.workflow_step,
                disclosure_given=result.is_compliant,
                details=result.recommended_corrective_action,
            )

            return result
        except Exception as e:
            logger.error(f"ComplianceMonitoringAgent execution error: {e}")
            raise
