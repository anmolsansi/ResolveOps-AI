from app.services.connectors.base import SourceConnector
from app.services.connectors.mock_sources import (
    FreshdeskMockConnector,
    IntercomMockConnector,
    ZendeskMockConnector,
)

SUPPORTED_PROVIDERS = ("zendesk", "freshdesk", "intercom")

_REGISTRY: dict[str, type[SourceConnector]] = {
    "zendesk": ZendeskMockConnector,
    "freshdesk": FreshdeskMockConnector,
    "intercom": IntercomMockConnector,
}


def get_source_connector(provider: str) -> SourceConnector:
    key = provider.lower().strip()
    if key not in _REGISTRY:
        raise ValueError(
            f"Unsupported connector provider '{provider}'. "
            f"Supported: {', '.join(SUPPORTED_PROVIDERS)}"
        )
    return _REGISTRY[key]()
