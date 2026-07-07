"""Tabular .toon report service."""
from typing import Any

from modules.shared_report_service import SharedReportService


class TabularToonService(SharedReportService):
    """Service for generating reports from .toon format payloads."""

    async def _obter_dados(self, payload: dict[str, Any]) -> Any:
        return payload.get("data", [])
