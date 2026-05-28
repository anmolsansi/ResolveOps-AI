#!/usr/bin/env python3
"""Generate sample support ticket CSV for ResolveOps AI demos and tests."""

import argparse
import csv
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

PRODUCT_AREAS = ["Billing", "Auth", "Integrations", "Dashboard", "Notifications", "API"]
ISSUE_TYPES = ["Bug", "Feature Request", "Question", "Performance", "Security"]
PRIORITIES = ["Critical", "High", "Medium", "Low"]
CUSTOMER_TIERS = ["Enterprise", "Pro", "Starter", "Free"]
STATUSES = ["Open", "In Progress", "Resolved", "Closed"]

TITLES = [
    "Billing charge appears twice on invoice",
    "Cannot log in after password reset",
    "Slack integration not syncing messages",
    "Dashboard takes 30+ seconds to load",
    "Email notifications not being sent",
    "API rate limit hit during normal usage",
    "Subscription downgrade not reflected",
    "SSO login fails with SAML error",
    "Webhook deliveries failing silently",
    "Report export produces empty file",
    "User permissions not applied correctly",
    "Payment method update shows error",
    "Search returns irrelevant results",
    "Mobile app crashes on launch",
    "Two-factor auth codes not accepted",
    "Data export missing recent records",
    "Custom fields not saving",
    "Automated workflow stops midway",
    "Incorrect timezone on timestamps",
    "File upload size limit too restrictive",
]

BODIES = [
    "Customer reports seeing a duplicate charge on their monthly invoice. They were charged "
    "$49.99 twice instead of once. Account ID: {id}. The customer is requesting an immediate "
    "refund for the duplicate charge.",
    "User cannot log in after requesting a password reset. The reset email was received and the "
    "new password was set, but login still fails with 'Invalid credentials'. Browser: Chrome "
    "latest. Cleared cookies and cache already.",
    "The Slack integration stopped syncing messages 3 days ago. No error messages in the "
    "integration dashboard. Other integrations are working fine. Customer has re-authorized "
    "the Slack connection without success.",
    "Main dashboard is loading extremely slowly. Page load time is over 30 seconds. This started "
    "after the last update. Customer has 10,000+ records which may be contributing. Other pages "
    "load normally.",
    "Automated email notifications are not being delivered. Checked spam folders. Internal logs "
    "show the notifications are being queued but not sent. This affects all notification types "
    "for this account.",
    "The API is returning 429 errors during normal usage patterns. Customer is making "
    "approximately 100 requests per minute which should be within their plan limits. Rate limit "
    "headers show incorrect remaining count.",
    "Customer downgraded from Pro to Starter plan but is still being charged the Pro rate. The "
    "plan change shows as successful in the admin panel but billing was not updated. Next invoice "
    "date is approaching.",
    "SSO login fails with a SAML assertion error. The SAML response is being generated correctly "
    "by the IdP but our application rejects it. Error message: 'Invalid SAML response: "
    "audience mismatch'.",
    "Webhook endpoint is configured and was previously working. Now deliveries are failing with "
    "no error feedback to the customer. Server logs show the webhook URL is returning 200 but "
    "our system marks it as failed.",
    "The CSV report export feature generates a file with headers only and no data rows. This "
    "affects all report types. The in-app preview shows data correctly but the export is empty. "
    "File size is only a few bytes.",
]

RESOLUTIONS = [
    "Refund issued and billing system updated to prevent duplicate charges.",
    "Password hash migration issue identified and fixed. User can now log in.",
    "OAuth token refresh was failing. Re-integrated the Slack app with updated scopes.",
    "Added pagination to dashboard query. Load time reduced to under 2 seconds.",
    "Email service credentials had expired. Renewed credentials and cleared queue.",
    "Rate limiter configuration was incorrect for the plan tier. Updated limits.",
    "Billing webhook handler had a race condition. Fixed and applied correct charge.",
    "SAML audience URI was misconfigured. Updated to match the IdP settings.",
    "Webhook delivery retry logic was broken. Fixed the retry mechanism.",
    "Export query had a missing JOIN clause. Fixed and verified output.",
]


def generate_tickets(count: int, seed: int = 42, include_invalid: bool = False) -> list[dict]:
    rng = random.Random(seed)
    base_date = datetime(2025, 1, 1)
    tickets: list[dict] = []

    for i in range(1, count + 1):
        created = base_date + timedelta(
            days=rng.randint(0, 180), hours=rng.randint(0, 23), minutes=rng.randint(0, 59)
        )
        status = rng.choice(STATUSES)
        resolved = None
        resolution = ""
        if status in ("Resolved", "Closed"):
            resolved = created + timedelta(hours=rng.randint(1, 72))
            resolution = rng.choice(RESOLUTIONS)

        ticket = {
            "id": f"TICKET-{i:04d}",
            "title": rng.choice(TITLES),
            "body": rng.choice(BODIES).format(id=f"TICKET-{i:04d}"),
            "product_area": rng.choice(PRODUCT_AREAS),
            "issue_type": rng.choice(ISSUE_TYPES),
            "priority": rng.choice(PRIORITIES),
            "customer_tier": rng.choice(CUSTOMER_TIERS),
            "status": status,
            "resolution": resolution,
            "created_at": created.strftime("%Y-%m-%d %H:%M:%S"),
            "resolved_at": resolved.strftime("%Y-%m-%d %H:%M:%S") if resolved else "",
        }
        tickets.append(ticket)

    if include_invalid:
        tickets.append(
            {
                "id": "",
                "title": "",
                "body": "Missing required fields",
                "product_area": "",
                "issue_type": "",
                "priority": "",
                "customer_tier": "",
                "status": "",
                "resolution": "",
                "created_at": "",
                "resolved_at": "",
            }
        )
        tickets.append(
            {
                "id": "TICKET-BAD-DATE",
                "title": "Bad date ticket",
                "body": "This ticket has an invalid date",
                "product_area": "Auth",
                "issue_type": "Bug",
                "priority": "High",
                "customer_tier": "Enterprise",
                "status": "Open",
                "resolution": "",
                "created_at": "not-a-date",
                "resolved_at": "",
            }
        )

    return tickets


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate sample support tickets CSV")
    parser.add_argument("--count", type=int, default=50, help="Number of tickets (default: 50)")
    parser.add_argument(
        "--output",
        type=str,
        default=str(Path(__file__).parent / "sample_tickets.csv"),
        help="Output CSV path",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument(
        "--include-invalid", action="store_true", help="Include intentionally invalid rows"
    )
    args = parser.parse_args()

    tickets = generate_tickets(args.count, seed=args.seed, include_invalid=args.include_invalid)
    cols = [
        "id", "title", "body", "product_area", "issue_type",
        "priority", "customer_tier", "status", "resolution",
        "created_at", "resolved_at",
    ]

    with open(args.output, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(tickets)

    print(f"Generated {len(tickets)} tickets to {args.output}")


if __name__ == "__main__":
    main()
