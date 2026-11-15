"""Conversion Analytics Agent adhering to Section 13 of AGENTS.md."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.ai.agents.base import BaseAgent
from app.ai.client.mistral_client import mistral_client
from app.ai.tools.agent_tools import GetConversionFunnelMetricsTool
from app.core.logging import logger


class ConversionAnalyticsInput(BaseModel):
    reporting_window_days: int = 30
    target_channel: Optional[str] = "all"


class ConversionFunnelAnalysis(BaseModel):
    reporting_window_days: int
    total_prospects: int
    proposals_submitted: int
    underwriting_cases: int
    overall_conversion_rate: float
    primary_bottleneck: str = Field(description="Most significant drop-off stage in the customer journey")
    operational_recommendations: List[str] = Field(description="Actionable business improvements for management")


class ConversionAnalyticsAgent(BaseAgent):
    id = "conversion-analytics-agent"
    name = "Conversion Analytics Agent"
    description = "Analyzes end-to-end multi-agent funnel performance, conversion velocity, and drop-off friction."
    purpose = "Translates operational database metrics into actionable executive conversion insights."
    input_schema = ConversionAnalyticsInput
    output_schema = ConversionFunnelAnalysis
    required_permissions = []
    registered_tools = [GetConversionFunnelMetricsTool()]
    temperature = 0.1

    async def run(self, input_data: ConversionAnalyticsInput, context: Dict[str, Any]) -> ConversionFunnelAnalysis:
        metrics_tool = GetConversionFunnelMetricsTool()
        tool_ctx = context.get("tool_context")
        metrics = await metrics_tool.execute(tool_ctx, days_window=input_data.reporting_window_days)

        prompt = (
            f"You are the Chief Conversion Analytics AI for PS-21 Insurance.\n"
            f"Database Metrics for last {input_data.reporting_window_days} days:\n"
            f"- Total Prospects: {metrics.get('total_prospects', 0)}\n"
            f"- Applications Submitted: {metrics.get('applications_submitted', 0)}\n"
            f"- Underwriting Cases: {metrics.get('underwriting_cases', 0)}\n"
            f"- Conversion Rate: {metrics.get('conversion_rate_percentage', 0.0)}%\n\n"
            f"Analyze the performance, identify the primary bottleneck, and provide 2-3 recommendations.\n"
            f"Return strict JSON matching ConversionFunnelAnalysis."
        )

        try:
            response = await mistral_client.chat(
                messages=[
                    {"role": "system", "content": "You are a quantitative conversion rate optimization AI. Return strict JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            content = response.get("content", "{}")
            return ConversionFunnelAnalysis.model_validate_json(content)
        except Exception as e:
            logger.error(f"ConversionAnalyticsAgent execution error: {e}")
            raise
