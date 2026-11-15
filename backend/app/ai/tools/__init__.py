"""Tool Initialization and Auto-Registration."""
from app.ai.tools.registry import tool_registry
from app.ai.tools.system_tools import (
    GetProductCatalogTool,
    CalculateDeterministicQuoteTool,
    GetCustomerContextTool,
)
from app.ai.tools.agent_tools import (
    QueryProspectSignalsTool,
    EvaluateLeadQualificationTool,
    RecordCustomerNeedsTool,
    ValidateRiskDeclarationsTool,
    ScheduleFollowupReminderTool,
    LogComplianceAuditTool,
    QueryApprovedKnowledgeBaseTool,
    GetConversionFunnelMetricsTool,
)

# Register default foundational tools
tool_registry.register(GetProductCatalogTool())
tool_registry.register(CalculateDeterministicQuoteTool())
tool_registry.register(GetCustomerContextTool())

# Register Phase 10 multi-agent tools
tool_registry.register(QueryProspectSignalsTool())
tool_registry.register(EvaluateLeadQualificationTool())
tool_registry.register(RecordCustomerNeedsTool())
tool_registry.register(ValidateRiskDeclarationsTool())
tool_registry.register(ScheduleFollowupReminderTool())
tool_registry.register(LogComplianceAuditTool())
tool_registry.register(QueryApprovedKnowledgeBaseTool())
tool_registry.register(GetConversionFunnelMetricsTool())
