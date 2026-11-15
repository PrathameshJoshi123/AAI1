"""SQLAlchemy models registry for PS-21."""
from app.models.base import Base, TimestampMixin
from app.models.auth import (
    User,
    Role,
    Permission,
    UserRole,
    RolePermission,
    RevokedToken,
)
from app.models.profile import (
    Customer,
    Advisor,
    Underwriter,
)
from app.models.prospect import (
    LeadSource,
    Prospect,
    BehavioralSignal,
    LeadScore,
    LeadScoringRule,
)
from app.models.conversation import (
    Conversation,
    ConversationMessage,
)
from app.models.product import (
    InsuranceProduct,
    ProductConfiguration,
)
from app.models.pricing_matrix import ProductPricingMatrix
from app.models.recommendation import (
    CustomerQualification,
    Recommendation,
    Quote,
)
from app.models.application import (
    Application,
    ApplicationDocument,
)
from app.models.underwriting import (
    UnderwritingCase,
    UnderwritingReview,
    CaseNote,
)
from app.models.agent import (
    AgentConfiguration,
    AgentExecution,
)
from app.models.audit import (
    AuditLog,
    ConsentRecord,
)
from app.models.system import (
    FollowUp,
    Notification,
    SystemSetting,
)
from app.models.email import (
    EmailDeliveryLog,
    UserEmailPreference,
)

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "Role",
    "Permission",
    "UserRole",
    "RolePermission",
    "RevokedToken",
    "Customer",
    "Advisor",
    "Underwriter",
    "LeadSource",
    "Prospect",
    "BehavioralSignal",
    "LeadScore",
    "LeadScoringRule",
    "Conversation",
    "ConversationMessage",
    "InsuranceProduct",
    "ProductConfiguration",
    "ProductPricingMatrix",
    "CustomerQualification",
    "Recommendation",
    "Quote",
    "Application",
    "ApplicationDocument",
    "UnderwritingCase",
    "UnderwritingReview",
    "CaseNote",
    "AgentConfiguration",
    "AgentExecution",
    "AuditLog",
    "ConsentRecord",
    "FollowUp",
    "Notification",
    "SystemSetting",
    "EmailDeliveryLog",
    "UserEmailPreference",
]


