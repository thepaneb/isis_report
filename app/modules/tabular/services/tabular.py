"""
Tabular report service.
"""

import locale
from datetime import datetime

import pandas as pd
from playwright.async_api import async_playwright

from ds.calendario_semanal import ds as ds_calendario
from ds.pedido_cartao import ds as ds_pedido
from extensions.jinja_template import render_template


class TabularService:  # pylint: disable=too-few-public-methods
    """
    Service for generating tabular reports.
    """

    async def __obter_dados(self, query) -> list:
        """
        Simulate data retrieval based on the query.
        """
        if query == "1":
            return ds_calendario
        elif query == "2":
            return ds_pedido
        else:
            return []

    async def __tratar_dados(self, dados_obtidos, data_source_def) -> dict:  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """
        Process the obtained data according to the data source definition.
        """
        result2 = {}
        result3 = []

        agrupamento_0 = data_source_def.get("groupings", {}).get("fields")
        agrupamento_1 = data_source_def.get("groupings", {}).get("groupings", {}).get("fields")

        if agrupamento_0 and agrupamento_1:
            agrupamento = agrupamento_0
            agrupamento = agrupamento + agrupamento_1 if agrupamento and agrupamento_1 else agrupamento or agrupamento_1
            data = pd.DataFrame(dados_obtidos)

            aggs_0 = data_source_def.get("groupings").get("groupings").get("aggregations")
            aggs_1 = data_source_def.get("groupings").get("aggregations")
            aggs_2 = data_source_def.get("summary")
            aggs = aggs_0
            aggs = aggs + aggs_1 if aggs and aggs_1 else aggs or aggs_1
            aggs = aggs + aggs_2 if aggs and aggs_2 else aggs or aggs_2
            aggs = list(dict.fromkeys(aggs))

            for _, df in data.groupby(agrupamento):
                x = df.to_dict("records")
                group_data = {}
                for field in agrupamento_0:
                    group_data.update({field: x[0].get(field)})
                sub_group_data = {}
                for field in agrupamento_1:
                    sub_group_data.update({field: x[0].get(field)})
                sub_group_footer = {}
                for c in x:
                    for field in agrupamento:
                        c.pop(field)
                for item in aggs:
                    if x[0].get(item):
                        soma = sum([data.get(item, {}) or 0 for data in x])
                        sub_group_footer.update({item: soma})
                sub_group_data.update(sub_group_footer)
                item = {"fields": sub_group_data, "detail": x}
                item.update(group_data)
                result3.append(item)

        if agrupamento_0:
            data = pd.DataFrame(result3) if agrupamento_1 else pd.DataFrame(dados_obtidos)
            result3 = []
            agrupamento = agrupamento_0
            aggs_0 = data_source_def.get("groupings").get("aggregations")
            aggs_1 = data_source_def.get("summary")
            aggs = aggs_0
            aggs = aggs + aggs_1 if aggs and aggs_1 else aggs or aggs_1
            aggs = list(dict.fromkeys(aggs))

            for _, df in data.groupby(agrupamento):
                x = df.to_dict("records")
                group_data = {}
                for field in agrupamento:
                    group_data.update({field: x[0].get(field)})
                group_footer = {}
                for item in aggs:
                    if x[0].get("fields", {}).get(item):
                        soma = sum([data.get("fields", {}).get(item) or 0 for data in x])
                        group_footer.update({item: soma})
                group_data.update(group_footer)
                for c in x:
                    for field in agrupamento:
                        c.pop(field)
                result3.append({"fields": group_data, "groups": x})

                result2.update({"groups": result3})

        if data_source_def.get("detail") or not (agrupamento_0 and agrupamento_1):
            result2.update({"detail": dados_obtidos})

        if data_source_def.get("summary"):
            summary = {}
            for item in data_source_def.get("summary"):
                if agrupamento_0:
                    soma = sum([data.get("fields", {}).get(item) or 0 for data in result3])
                else:
                    soma = sum([data.get(item) or 0 for data in dados_obtidos])
                summary.update({item: soma})

            result2.update({"summary": summary})

        return result2

    async def __gerar_html(self, dados_tratados, payload, layout) -> str:
        """
        Generate HTML report using Jinja2 template.
        """
        locale.setlocale(locale.LC_ALL, "")

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
            except:  # pylint: disable=bare-except # noqa: E722
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
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_content(texto_html)
            res = await page.pdf(
                format="A4",
                display_header_footer=True,
                header_template="<span>teste</span>",
                footer_template="""
<div style="width: 100%; text-align: center; font-size: 10px; display: table;">
    <div class="date" style="display: table-cell; text-align: center; vertical-align: middle;"></div>
    <div style="display: table-cell; text-align: center; vertical-align: middle;">
    </div>
    <div style="display: table-cell; text-align: center; vertical-align: middle;">Página <span class="pageNumber"></span> de <span class="totalPages"></span></div>
</div>""",
                margin={"top": ".2in", "bottom": ".5in"},
            )
            await browser.close()

        return res

    async def generate_report(self, data: dict):
        """
        Generate a tabular report based on the provided data.
        """
        data_source_def = data.get("data_source")
        query = data_source_def.get("query")
        response_type = data.get("type")
        dados_obtidos = await self.__obter_dados(query)
        dados_tratados = await self.__tratar_dados(dados_obtidos, data_source_def)

        html_content = await self.__gerar_html(
            dados_tratados=dados_tratados,
            payload=data,
            layout="relatorio_tabular_controller.jinja",
        )

        if response_type == "pdf":
            return await self.__gerar_pdf(html_content), "application/pdf"

        return html_content, "text/html"
