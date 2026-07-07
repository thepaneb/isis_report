"""Tabular JSON report service."""
from typing import Any

from modules.shared_report_service import SharedReportService


class TabularJsonService(SharedReportService):
    """Service for generating reports from JSON payloads."""

    async def _obter_dados(self, payload: dict[str, Any]) -> Any:
        return payload.get("data", [])
