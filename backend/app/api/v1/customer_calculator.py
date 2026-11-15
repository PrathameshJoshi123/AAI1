"""Customer Deterministic Coverage Calculator Endpoints."""
from fastapi import APIRouter
from app.schemas.calculator import HLVCalculationRequest, HLVCalculationResponse
from app.schemas.common import APIResponse
from app.services.coverage_calculator_service import CoverageCalculatorService

router = APIRouter(prefix="/customer/calculator", tags=["Customer Calculator"])


@router.post("/hlv", response_model=APIResponse[HLVCalculationResponse])
async def calculate_human_life_value(payload: HLVCalculationRequest):
    result = CoverageCalculatorService.calculate_human_life_value(payload)
    return APIResponse(
        data=result,
        message="Human Life Value calculation completed deterministically.",
    )

