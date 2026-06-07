from pydantic import BaseModel


class SlaRisk(BaseModel):
    ticket_id: str
    title: str
    product_area: str
    priority: str
    customer_tier: str
    status: str
    hours_open: float
    sla_hours: int
    due_in_hours: float
    breached: bool
    risk_score: float
    risk_level: str
    reason: str


class SlaRisksResponse(BaseModel):
    items: list[SlaRisk]
    breached_count: int
    high_risk_count: int
