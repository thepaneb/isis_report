from typing import Any

from modules.shared_report_service import SharedReportService


class TabularJsonService(SharedReportService):

    async def _obter_dados(self, payload: dict[str, Any]) -> Any:
        return payload.get("data", [])
