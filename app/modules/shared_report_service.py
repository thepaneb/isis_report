"""Shared report service implementing common report generation logic."""
from typing import Any

from extensions.jinja_template import render_template
from extensions.playwright_pool import get_pdf_from_html
from modules.base_service import BaseReportService
from utils.layout_converter import converter_layout_hierarquico


class SharedReportService(BaseReportService):
    """Shared implementation of BaseReportService with layout conversion and data formatting."""

    async def _obter_dados(self, payload: dict[str, Any]) -> Any:
        return payload.get("data", [])

    async def _tratar_dados(self, data: Any, payload: dict[str, Any]) -> dict[str, Any]:
        meta = payload.get("meta", {})
        layout_raw = payload.get("layout")

        if layout_raw:
            layout = converter_layout_hierarquico(layout_raw)
            ds_items = self._converter_dados(data, layout_raw)
        else:
            layout = self._inferir_layout(data)
            ds_items = {"groups": data} if not self._is_template_format(data) else {"groups": data}

        return {
            "ds_items": ds_items,
            "layout": layout,
            "meta": meta,
        }

    async def _gerar_html(self, data: dict[str, Any], payload: dict[str, Any]) -> str:
        ds_items = data["ds_items"]
        layout = data["layout"]
        meta = data["meta"]
        return await render_template(
            "relatorio_tabular.jinja",
            ds_items=ds_items,
            layout=layout,
            meta=meta,
            fmt=self._fmt,
            zip=zip,
        )

    @staticmethod
    def _fmt(value: Any, format_mask: str) -> str:
        if value is None:
            return ""
        if format_mask == "int":
            try:
                return f"{int(value):,}".replace(",", ".")
            except (ValueError, TypeError):
                return str(value)
        if format_mask == "float":
            try:
                return f"{float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except (ValueError, TypeError):
                return str(value)
        if format_mask == "date":
            return str(value)
        return str(value)

    async def _gerar_pdf(self, html: str) -> bytes:
        return await get_pdf_from_html(html)

    def _is_template_format(self, data: list) -> bool:
        return bool(data and isinstance(data[0], dict) and "fields" in data[0])

    def _converter_dados(self, data_raw: list[dict], layout_raw: dict[str, Any]) -> dict[str, Any]:
        if self._is_template_format(data_raw):
            return {"groups": data_raw}

        group_keys = {}
        for k, v in layout_raw.items():
            if isinstance(v, dict) and "label" not in v:
                group_keys[k] = v

        items = []
        for record in data_raw:
            fields = {}
            groups = []

            for key, value in record.items():
                if key in group_keys:
                    sub_layout = group_keys[key]
                    detail_key = next(
                        (sk for sk, sv in sub_layout.items()
                         if isinstance(sv, dict) and "label" not in sv),
                        None
                    )

                    for sub_item in value:
                        sub_fields = {
                            sk: sub_item[sk]
                            for sk in sub_layout
                            if sk != detail_key and sk in sub_item
                        }
                        detail = sub_item.get(detail_key, []) if detail_key else []

                        group_entry = {"fields": sub_fields}
                        if detail:
                            group_entry["detail"] = detail
                        groups.append(group_entry)
                else:
                    fields[key] = value

            item = {"fields": fields}
            if groups:
                item["groups"] = groups
            items.append(item)

        return {"groups": items}

    def _inferir_layout(self, data: list[dict]) -> dict[str, Any]:
        if not data:
            return {"groups": {"header": []}}

        sample = data[0] if isinstance(data[0], dict) else {}
        header = []
        for key, value in sample.items():
            if isinstance(value, list):
                continue
            dtype = "str"
            alignment = "left"
            if isinstance(value, bool):
                dtype = "str"
            elif isinstance(value, int):
                dtype = "int"
                alignment = "right"
            elif isinstance(value, float):
                dtype = "float"
                alignment = "right"
            header.append({
                "name": key,
                "label": key.replace("_", " ").title(),
                "format_mask": dtype,
                "alignment": alignment,
            })

        return {"groups": {"header": header}}
