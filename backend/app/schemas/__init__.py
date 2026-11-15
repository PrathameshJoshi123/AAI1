"""Pydantic schemas package."""
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserRegisterRequest,
)
from app.schemas.common import (
    PaginatedResponse,
    ResponseEnvelope,
    ErrorResponse,
)
from app.schemas.prospect import (
    ProspectCreate,
    ProspectUpdate,
    ProspectFilterParams,
    ProspectRead,
    ProspectDetailRead,
    LeadScoreRead,
    ScoreFactorRead,
    AdvisorAssignRequest,
    AdvisorOutreachNoteCreate,
    PipelineKPIsRead,
)
from app.schemas.signal import (
    SignalIngestRequest,
    BatchSignalIngestRequest,
    BehavioralSignalRead,
)
from app.schemas.customer import (
    CustomerProfileRead,
    CustomerProfileUpdate,
)
from app.schemas.journey import (
    JourneyStatusResponse,
    JourneyTransitionRequest,
    ResumeJourneyResponse,
)
from app.schemas.conversation import (
    CustomerChatTurnRequest,
    ConversationMessageRead,
    ConversationThreadRead,
    WidgetDataPayload,
)
from app.schemas.needs_assessment import (
    NeedsAssessmentSubmit,
    NeedsAssessmentResponse,
)
from app.schemas.calculator import (
    HLVCalculationRequest,
    HLVCalculationResponse,
)
from app.schemas.pricing_matrix import (
    PricingMatrixRead,
    PricingMatrixCreate,
)
from app.schemas.product import (
    InsuranceProductRead,
    ProductCreate,
    ProductConfigurationRead,
)
from app.schemas.quote import (
    QuoteCreate,
    QuoteRead,
    QuoteRecalculateRequest,
)
from app.schemas.recommendation import (
    RecommendationCreate,
    RecommendationRead,
    RecommendationEvaluateResponse,
)
from app.schemas.admin import (
    ExecutiveMetricsResponse,
    RecentActivityResponse,
    ChannelPerformanceItem,
    ProductPerformanceItem,
    AdvisorPerformanceItem,
    TurnaroundAnalyticsResponse,
    FunnelStage,
    ConversionFunnelResponse,
    AgentTelemetryResponse,
    AgentStatusUpdateRequest,
    AgentExecutionLogsResponse,
    EmployeeCreateRequest,
    EmployeeStatusUpdateRequest,
    EmployeeRoleUpdateRequest,
    EmployeeResponse,
    AdminProductCreateRequest,
    AdminProductUpdateRequest,
    AdminProductResponse,
    AuditLogSearchResponse,
    IntegrationHealthResponse,
    SystemSettingResponse,
    SystemSettingUpdateRequest,
)

__all__ = [
    "LoginRequest",
    "RefreshTokenRequest",
    "TokenResponse",
    "UserRegisterRequest",
    "PaginatedResponse",
    "ResponseEnvelope",
    "ErrorResponse",
    "ProspectCreate",
    "ProspectUpdate",
    "ProspectFilterParams",
    "ProspectRead",
    "ProspectDetailRead",
    "LeadScoreRead",
    "ScoreFactorRead",
    "AdvisorAssignRequest",
    "AdvisorOutreachNoteCreate",
    "PipelineKPIsRead",
    "SignalIngestRequest",
    "BatchSignalIngestRequest",
    "BehavioralSignalRead",
    "ConsentGrantRequest",
    "ConsentRevokeRequest",
    "ConsentRecordRead",
    "ConsentStatusResponse",
]
