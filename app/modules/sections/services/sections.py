"""
Sections report service.
"""

import locale
from datetime import datetime

from constants import FOOTER_TEMPLATE, HEADER_TEMPLATE, PAGE_MARGIN
from extensions.jinja_template import render_template
from extensions.playwright_pool import new_page


class SectionsService:  # pylint: disable=too-few-public-methods
    """
    Service for generating sections reports.
    """

    async def __obter_dados(self, payload) -> list:
        """
        Simulate data retrieval based on the query.
        """
        return [
            {
                "data_entrega_empresas": [
                    {
                        "id_cliente": 1,
                        "data_entrega": "01/12/2024",
                        "empresa": "CQ CONSULTORIA ADMINITRATIVA",
                        "pedidos": [
                            {
                                "id_cliente": 1,
                                "data_entrega": "01/12/2024",
                                "pedido":"008750",
                                "data_pedido":"01/12/2024",
                                "nome_produto":"CQ REFEIÇÃO",
                                "cargas": [
                                    {"pedido":"008750","qtde":1,"valor_unitario":1500,"valor_total":1500},
                                    {"pedido":"008750","qtde":1,"valor_unitario":1000,"valor_total":1000}
                                ],
                                "tarifas": [
                                    {"pedido":"008750","qtde":1,"valor_unitario":1500,"valor_total":1500},
                                    {"pedido":"008750","qtde":1,"valor_unitario":1000,"valor_total":1000}
                                ]
                            }
                        ]
                    }
                ]
            }
        ]

    async def __gerar_html(self, dados_tratados, payload, layout) -> str:
        """
        Generate HTML report using Jinja2 template.
        """
        try:
            locale.setlocale(locale.LC_ALL, "")
        except Exception:
            pass

        def fmt(valor, mascara):
            try:
                if mascara == "int":
                    return locale.format_string("%0.0f", valor, grouping=True)
                if mascara == "float":
                    return locale.format_string("%0.2f", valor, grouping=True)
                if mascara == "date":
                    return f"{valor:%d/%m/%y}"
                if mascara == "datetime":
                    return f"{valor:%d/%m/%y %H:%M:%S}"

                return valor
            except Exception:
                return valor

        return await render_template(
            template_name=layout,
            ds_items=dados_tratados,
            layout=payload.get("layout"),
            titulo=payload.get("title"),
            filters=payload.get("filters"),
            zip=zip,
            data_hora_impresssao=f"{datetime.now():%d/%m/%y %H:%M:%S}",
            type=payload.get("type"),
            fmt=lambda d1, d2=None: fmt(d1, d2),
            mode=payload.get("mode", "exact") or "exact",
        )

    async def __gerar_pdf(self, texto_html) -> bytes:
        page = None
        try:
            page = await new_page()
            await page.set_content(texto_html)
            res = await page.pdf(
                format="A4",
                display_header_footer=True,
                header_template=HEADER_TEMPLATE,
                footer_template=FOOTER_TEMPLATE,
                margin=PAGE_MARGIN,  # type: ignore[arg-type]
            )
            return res
        finally:
            if page is not None:
                try:
                    await page.close()
                except Exception:
                    pass

    async def generate_report(self, data: dict):
        """
        Generate a sections report based on the provided data.
        """
        response_type = data.get("type")
        sections_node = data.get("sections", [])
        dados_obtidos = await self.__obter_dados(payload=sections_node)

        html_content = await self.__gerar_html(
            dados_tratados=dados_obtidos,
            payload=data,
            layout="relatorio_sections_controller.j2",
        )

        if response_type == "pdf":
            return await self.__gerar_pdf(html_content), "application/pdf"

        return html_content, "text/html"
