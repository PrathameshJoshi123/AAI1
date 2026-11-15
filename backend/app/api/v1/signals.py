"""FastAPI router for Behavioral Signal Ingestion."""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.common import ResponseEnvelope
from app.schemas.signal import BatchSignalIngestRequest, BehavioralSignalRead, SignalIngestRequest
from app.services.lead_service import LeadService

router = APIRouter(prefix="/signals", tags=["Behavioral Signals"])


@router.post("", response_model=ResponseEnvelope[BehavioralSignalRead], status_code=status.HTTP_201_CREATED)
async def ingest_single_signal(
    payload: SignalIngestRequest,
    session: AsyncSession = Depends(get_db),
):
    """Client beacon endpoint for recording real-time user engagement events."""
    service = LeadService(session)
    signal = await service.ingest_signal(payload)
    return ResponseEnvelope(data=BehavioralSignalRead.model_validate(signal))


@router.post("/batch", response_model=ResponseEnvelope[List[BehavioralSignalRead]], status_code=status.HTTP_201_CREATED)
async def ingest_batch_signals(
    payload: BatchSignalIngestRequest,
    session: AsyncSession = Depends(get_db),
):
    """Batch ingestion endpoint for buffered client-side engagement events."""
    service = LeadService(session)
    results = []
    for event in payload.events:
        sig = await service.ingest_signal(event)
        if sig:
            results.append(BehavioralSignalRead.model_validate(sig))
    return ResponseEnvelope(data=results)

