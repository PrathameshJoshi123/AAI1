"""Customer Support Agent adhering to Section 13 of AGENTS.md."""
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.client.mistral_client import mistral_client
from app.ai.tools.agent_tools import QueryApprovedKnowledgeBaseTool
from app.core.logging import logger


class SupportQueryInput(BaseModel):
    customer_id: str
    question: str
    policy_id: Optional[str] = None
    application_id: Optional[str] = None


class SupportQueryAnswer(BaseModel):
    customer_id: str
    answer: str = Field(description="Accurate, empathetic answer based strictly on approved product KB")
    reference_policy_clause: Optional[str] = Field(default=None, description="Official clause reference")
    needs_human_escalation: bool = Field(description="Whether the query involves a dispute or exception needing human desk")
    suggested_followup_question: Optional[str] = Field(default=None, description="Proactive next query suggestion")


class CustomerSupportAgent(BaseAgent):
    id = "customer-support-agent"
    name = "Customer Support Agent"
    description = "Resolves policy queries, claims process questions, and application status inquiries accurately."
    purpose = "Provides prompt, compliant support assistance grounded in verified platform knowledge."
    input_schema = SupportQueryInput
    output_schema = SupportQueryAnswer
    required_permissions = []
    registered_tools = [QueryApprovedKnowledgeBaseTool()]
    temperature = 0.1

    async def run(self, input_data: SupportQueryInput, context: Dict[str, Any]) -> SupportQueryAnswer:
        kb_tool = QueryApprovedKnowledgeBaseTool()
        tool_ctx = context.get("tool_context")
        kb_result = await kb_tool.execute(tool_ctx, query=input_data.question)
        kb_content = kb_result.get("content", "General policy rules apply.")

        prompt = (
            f"You are the Customer Support AI Agent for PS-21 Insurance.\n"
            f"Customer Inquiry: \"{input_data.question}\"\n\n"
            f"VERIFIED KNOWLEDGE BASE CONTENT (DO NOT CONTRADICT):\n"
            f"{kb_content}\n\n"
            f"Rules:\n"
            f"1. Never invent coverage terms, payout amounts, or claim guarantee dates.\n"
            f"2. Escalate to human support desk if the customer expresses frustration or disputes.\n"
            f"3. Return strict JSON matching SupportQueryAnswer."
        )

        try:
            response = await mistral_client.chat(
                messages=[
                    {"role": "system", "content": "You are a licensed customer support assistant for insurance. Return strict JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            content = response.get("content", "{}")
            return SupportQueryAnswer.model_validate_json(content)
        except Exception as e:
            logger.error(f"CustomerSupportAgent execution error: {e}")
            raise
