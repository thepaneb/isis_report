"""
Sections report service.
"""

from typing import Any

import pandas as pd

from ds.pedido_cartao import ds as mock_ds
from extensions.jinja_template import render_template
from extensions.playwright_pool import get_pdf_from_html
from modules.base_service import BaseReportService


class SectionsService(BaseReportService):
    """
    Service for generating section-grouped reports (Empresa/Pedido).
    """

    async def _obter_dados(self, payload: dict[str, Any]) -> list[dict]:
        return mock_ds

    async def _tratar_dados(self, data: list[dict], payload: dict[str, Any]) -> dict:
        df = pd.DataFrame(data)

        result = {}

        for empresa, e_df in df.groupby("empresa"):
            pedidos_list = []

            for pedido, p_df in e_df.groupby("pedido"):
                pedidos_list.append(
                    {
                        "numero": pedido,
                        "data_pedido": p_df["data_pedido"].iloc[0],
                        "itens": p_df.to_dict("records"),
                        "total_pedido": p_df["valor_total"].sum(),
                    }
                )

            result[str(empresa)] = {
                "nome": empresa,
                "pedidos": pedidos_list,
                "total_empresa": e_df["valor_total"].sum(),
            }

        return result

    async def _gerar_html(self, structured_data: dict, payload: dict[str, Any]) -> str:
        return await render_template(
            "relatorio_tabular_sections.jinja",
            empresas=structured_data,
            payload=payload,
        )

    async def _gerar_pdf(self, html: str) -> bytes:
        return await get_pdf_from_html(html)
