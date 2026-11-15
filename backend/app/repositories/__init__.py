"""Repositories package."""
from app.repositories.base import BaseRepository
from app.repositories.user_repository import UserRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.quote_repository import QuoteRepository
from app.repositories.application_repository import ApplicationRepository
from app.repositories.underwriting_repository import UnderwritingRepository
from app.repositories.audit_repository import AuditRepository
from app.repositories.prospect_repository import ProspectRepository
from app.repositories.signal_repository import SignalRepository
from app.repositories.scoring_rule_repository import ScoringRuleRepository
from app.repositories.consent_repository import ConsentRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "ProductRepository",
    "QuoteRepository",
    "ApplicationRepository",
    "UnderwritingRepository",
    "AuditRepository",
    "ProspectRepository",
    "SignalRepository",
    "ScoringRuleRepository",
    "ConsentRepository",
]
