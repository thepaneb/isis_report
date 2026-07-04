"""
Tabular report service.
"""

from typing import Any

import pandas as pd

from ds.pedido_cartao import ds as mock_ds
from extensions.jinja_template import render_template
from extensions.playwright_pool import get_pdf_from_html
from modules.base_service import BaseReportService


class TabularService(BaseReportService):
    """
    Service for generating tabular reports.
    """

    async def _obter_dados(self, payload: dict[str, Any]) -> list[dict]:
        return mock_ds

    async def _tratar_dados(self, data: list[dict], payload: dict[str, Any]) -> pd.DataFrame:
        df = pd.DataFrame(data)

        if "empresa" in payload:
            df = df[df["empresa"] == payload["empresa"]]

        df = df.sort_values(by=["empresa", "pedido"])
        return df

    async def _gerar_html(self, df: pd.DataFrame, payload: dict[str, Any]) -> str:
        rows = df.to_dict(orient="records")
        return await render_template("relatorio_tabular_controller.jinja", rows=rows, title=payload.get("title", "Relatório Tabular"))

    async def _gerar_pdf(self, html: str) -> bytes:
        return await get_pdf_from_html(html)
