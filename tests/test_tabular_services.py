"""Integration tests for the tabular services backed by isis-report-lib."""

from unittest.mock import AsyncMock, patch

import pytest
from isis_report_lib.toon import ToonParser

from modules.tabular_json.services.tabular_json_service import TabularJsonService
from modules.tabular_toon.services.tabular_toon_service import TabularToonService

PDF = b"%PDF-1.7\n%%EOF\n"

PAYLOAD = {
    "meta": {"title": "Pedido", "sub_title": "2024", "mode": "exact"},
    "layout": {
        "empresa": {"label": "Empresa", "format_mask": "str", "alignment": "left"},
        "pedidos": {
            "pedido": {"label": "Código", "format_mask": "int", "alignment": "right"},
            "total": {"label": "Total", "format_mask": "float", "alignment": "right"},
        },
    },
    "data": [{"empresa": "ACME", "pedidos": [{"pedido": 1, "total": 10}]}],
}

TOON = """meta:
  title: Pedido
  mode: exact
layout:
  empresa: {label: Empresa, format_mask: str, alignment: left}
data[1]:
  - empresa: ACME
"""


@pytest.mark.asyncio
async def test_json_service_delegates_to_lib():
    captured = {}

    async def fake_pdf(html, **options):
        captured["html"] = html
        return PDF

    with patch("isis_report_lib.pdf.get_pdf_from_html", new=fake_pdf):
        out = await TabularJsonService().execute(PAYLOAD)
    assert out == PDF
    assert "ACME" in captured["html"]


def test_toon_parser_from_lib():
    payload = ToonParser().parse(TOON)
    assert payload["meta"]["title"] == "Pedido"
    assert payload["data"][0]["empresa"] == "ACME"


@pytest.mark.asyncio
async def test_toon_service_generates_pdf():
    payload = ToonParser().parse(TOON)
    with patch("isis_report_lib.pdf.get_pdf_from_html", new=AsyncMock(return_value=PDF)):
        out = await TabularToonService().execute(payload)
    assert out == PDF
