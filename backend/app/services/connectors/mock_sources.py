"""Deterministic mock connectors for Zendesk, Freshdesk, and Intercom.

Each provider exposes a fixed catalog of synthetic tickets. ``fetch_since`` uses
an integer offset cursor so repeated syncs are incremental. Each catalog
intentionally contains one near-duplicate ticket to exercise semantic dedup.
"""
from datetime import datetime, timedelta

from app.services.connectors.base import RawTicket, SourceConnector

_BASE_DATE = datetime(2025, 3, 1, 9, 0, 0)

_TEMPLATES = [
    {
        "title": "Cannot log in after password reset",
        "body": "Customer reset their password but login still fails with an invalid credentials error.",  # noqa: E501
        "product_area": "Auth",
        "issue_type": "Bug",
        "priority": "High",
        "resolution": "Cleared cached session tokens and forced a fresh password reset link.",
    },
    {
        "title": "Duplicate charge on monthly invoice",
        "body": "Customer was billed twice for the same subscription invoice this billing cycle.",
        "product_area": "Billing",
        "issue_type": "Bug",
        "priority": "High",
        "resolution": "Refunded the duplicate charge and corrected the billing schedule.",
    },
    {
        "title": "API returns 500 on bulk export",
        "body": "The bulk export endpoint throws a 500 error when exporting over 1000 records.",
        "product_area": "API",
        "issue_type": "Bug",
        "priority": "Critical",
        "resolution": "Added pagination to the export job and raised the gateway timeout.",
    },
    {
        "title": "Dashboard loads slowly for large accounts",
        "body": "Dashboard takes over 30 seconds to render for accounts with many tickets.",
        "product_area": "Performance",
        "issue_type": "Performance",
        "priority": "Medium",
        "resolution": "Added an index on the reporting query and enabled response caching.",
    },
    {
        "title": "How do I enable two-factor authentication?",
        "body": "Customer asks how to turn on 2FA for their team members.",
        "product_area": "Auth",
        "issue_type": "Question",
        "priority": "Low",
        "resolution": "Shared the security settings guide for enabling 2FA per user.",
    },
    {
        "title": "Webhook deliveries are delayed",
        "body": "Outbound webhooks are arriving several minutes late during peak hours.",
        "product_area": "API",
        "issue_type": "Bug",
        "priority": "High",
        "resolution": "Scaled the webhook worker pool and added a retry backoff.",
    },
]

# A near-duplicate of template[0] (same content) to exercise semantic dedup.
_DUPLICATE = dict(_TEMPLATES[0])

_TIERS = ["Enterprise", "Pro", "Free"]


class _MockSource(SourceConnector):
    """Builds a deterministic catalog seeded by the provider name."""

    id_prefix = "100"

    def _catalog(self) -> list[RawTicket]:
        entries = [*_TEMPLATES, _DUPLICATE]
        tickets: list[RawTicket] = []
        for i, tpl in enumerate(entries):
            tickets.append(
                RawTicket(
                    external_id=f"{self.id_prefix}{i}",
                    title=tpl["title"],
                    body=tpl["body"],
                    product_area=tpl["product_area"],
                    issue_type=tpl["issue_type"],
                    priority=tpl["priority"],
                    customer_tier=_TIERS[i % len(_TIERS)],
                    status="Resolved",
                    resolution=tpl["resolution"],
                    created_at=_BASE_DATE + timedelta(hours=i),
                )
            )
        return tickets

    def fetch_since(
        self, cursor: str | None, limit: int = 6
    ) -> tuple[list[RawTicket], str]:
        offset = int(cursor) if cursor and cursor.isdigit() else 0
        catalog = self._catalog()
        page = catalog[offset : offset + limit]
        new_cursor = str(min(offset + limit, len(catalog)))
        return page, new_cursor


class ZendeskMockConnector(_MockSource):
    provider = "zendesk"
    id_prefix = "ZD-"


class FreshdeskMockConnector(_MockSource):
    provider = "freshdesk"
    id_prefix = "FD-"


class IntercomMockConnector(_MockSource):
    provider = "intercom"
    id_prefix = "IC-"
