"""Connector abstraction for importing tickets from support tools.

The mock connectors below produce deterministic synthetic tickets so the import
flow can be demoed without external credentials. A real connector simply
implements ``fetch_since`` against the vendor API (paginating by the returned
cursor) and returns the same ``RawTicket`` shape.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RawTicket:
    external_id: str
    title: str
    body: str
    product_area: str
    issue_type: str
    priority: str
    customer_tier: str
    status: str
    resolution: str
    created_at: datetime


class SourceConnector(ABC):
    provider: str = "unknown"

    @abstractmethod
    def fetch_since(
        self, cursor: str | None, limit: int = 6
    ) -> tuple[list[RawTicket], str]:
        """Return the next page of tickets after ``cursor`` and the new cursor.

        Implementations must be incremental: passing the returned cursor back in
        on a subsequent call yields only newer tickets (empty when caught up).
        """
        ...

    def normalize(self, raw: RawTicket) -> dict:
        return {
            "id": f"{self.provider}-{raw.external_id}",
            "title": raw.title,
            "body": raw.body,
            "product_area": raw.product_area,
            "issue_type": raw.issue_type,
            "priority": raw.priority,
            "customer_tier": raw.customer_tier,
            "status": raw.status,
            "resolution": raw.resolution,
            "created_at": raw.created_at,
            "resolved_at": None,
        }
