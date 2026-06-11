from fastapi import APIRouter

from app.schemas.governance import PiiMatch, PiiScanRequest, PiiScanResponse
from app.services.pii import detect_pii, redact_pii

router = APIRouter()


@router.post("/scan", response_model=PiiScanResponse)
def scan_pii(payload: PiiScanRequest) -> PiiScanResponse:
    matches = detect_pii(payload.text)
    redacted, counts = redact_pii(payload.text)
    return PiiScanResponse(
        matches=[PiiMatch(**m) for m in matches],
        counts=counts,
        redacted_text=redacted,
    )
