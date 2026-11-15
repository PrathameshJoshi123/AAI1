"""Agent Initialization and Auto-Registration for Phase 10 Ecosystem."""
from app.ai.agents.registry import agent_registry

# Import all agent implementations
from app.ai.agents.definitions.diagnostic_agent import DiagnosticAgent
from app.ai.agents.definitions.conversational_advisor_agent import ConversationalAdvisorAgent
from app.ai.agents.definitions.conversational_engagement_agent import ConversationalEngagementAgent
from app.ai.agents.definitions.insurance_explainer_agent import InsuranceExplainerAgent
from app.ai.agents.definitions.recommendation_agent import RecommendationAgent
from app.ai.agents.definitions.quote_coordination_agent import QuoteCoordinationAgent
from app.ai.agents.definitions.onboarding_agent import OnboardingAgent
from app.ai.agents.definitions.document_review_agent import DocumentReviewAssistanceAgent
from app.ai.agents.definitions.underwriting_escalation_agent import UnderwritingEscalationAgent
from app.ai.agents.definitions.prospect_intelligence_agent import ProspectIntelligenceAgent
from app.ai.agents.definitions.lead_qualification_agent import LeadQualificationAgent
from app.ai.agents.definitions.needs_assessment_agent import NeedsAssessmentAgent
from app.ai.agents.definitions.risk_information_analysis_agent import RiskInformationAnalysisAgent
from app.ai.agents.definitions.dropoff_detection_agent import DropOffDetectionAgent
from app.ai.agents.definitions.followup_coordination_agent import FollowUpCoordinationAgent
from app.ai.agents.definitions.compliance_monitoring_agent import ComplianceMonitoringAgent
from app.ai.agents.definitions.customer_support_agent import CustomerSupportAgent
from app.ai.agents.definitions.conversion_analytics_agent import ConversionAnalyticsAgent

# 1. Prospect Intelligence Agent
agent_registry.register(ProspectIntelligenceAgent())

# 2. Lead Qualification Agent
agent_registry.register(LeadQualificationAgent())

# 3. Conversational Engagement Agent & Conversational Advisor
agent_registry.register(ConversationalAdvisorAgent())
agent_registry.register(ConversationalEngagementAgent())

# 4. Needs Assessment Agent
agent_registry.register(NeedsAssessmentAgent())

# 5. Risk Information Analysis Agent
agent_registry.register(RiskInformationAnalysisAgent())

# 6. Recommendation Agent & Insurance Explainer
agent_registry.register(RecommendationAgent())
agent_registry.register(InsuranceExplainerAgent())

# 7. Quote Coordination Agent
agent_registry.register(QuoteCoordinationAgent())

# 8. Onboarding Agent
agent_registry.register(OnboardingAgent())

# 9. Document Review Assistance Agent
agent_registry.register(DocumentReviewAssistanceAgent())

# 10. Drop-off Detection Agent
agent_registry.register(DropOffDetectionAgent())

# 11. Follow-up Coordination Agent
agent_registry.register(FollowUpCoordinationAgent())

# 12. Underwriting Escalation Agent
agent_registry.register(UnderwritingEscalationAgent())

# 13. Compliance Monitoring Agent
agent_registry.register(ComplianceMonitoringAgent())

# 14. Customer Support Agent
agent_registry.register(CustomerSupportAgent())

# 15. Conversion Analytics Agent
agent_registry.register(ConversionAnalyticsAgent())

# Diagnostic Agent for system telemetry & health
agent_registry.register(DiagnosticAgent())
