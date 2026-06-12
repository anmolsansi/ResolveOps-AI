from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_current_workspace
from app.models.models import User, Workspace
from app.schemas.governance import PiiMatch, PiiScanRequest, PiiScanResponse
from app.services.pii import detect_pii, redact_pii

router = APIRouter()


@router.post("/scan", response_model=PiiScanResponse)
def scan_pii(
    payload: PiiScanRequest,
    workspace: Workspace = Depends(get_current_workspace),
    user: User = Depends(get_current_user),
) -> PiiScanResponse:
    matches = detect_pii(payload.text)
    redacted, counts = redact_pii(payload.text)
    return PiiScanResponse(
        matches=[PiiMatch(**m) for m in matches],
        counts=counts,
        redacted_text=redacted,
    )
