"""Tests for SharedReportService."""
from unittest.mock import AsyncMock, patch

import pytest

from modules.shared_report_service import SharedReportService

service = SharedReportService()


class TestObterDados:
    """Tests for _obter_dados method."""
    async def test_has_data(self):
        """Return data list when 'data' key exists."""
        result = await service._obter_dados({"data": [1, 2]})
        assert result == [1, 2]

    async def test_missing_data(self):
        """Return empty list when 'data' key is missing."""
        result = await service._obter_dados({"meta": {}})
        assert result == []


class TestTratarDados:
    """Tests for _tratar_dados method."""
    async def test_with_layout(self):
        """Process data using provided layout definition."""
        payload = {
            "meta": {"title": "Test"},
            "layout": {"nome": {"label": "Nome", "format_mask": "str", "alignment": "left"}},
        }
        result = await service._tratar_dados([{"nome": "João"}], payload)
        assert "ds_items" in result
        assert "layout" in result
        assert result["meta"] == {"title": "Test"}

    async def test_without_layout(self):
        """Infer layout from data when none is provided."""
        payload = {"meta": {"title": "Test"}}
        result = await service._tratar_dados([{"nome": "João", "idade": 30}], payload)
        layout = result["layout"]
        assert len(layout["groups"]["header"]) == 2
        assert layout["groups"]["header"][0]["name"] == "nome"
        assert layout["groups"]["header"][1]["name"] == "idade"
        assert layout["groups"]["header"][1]["format_mask"] == "int"

    async def test_empty_meta(self):
        """Return empty meta dict when meta is not provided."""
        payload = {"layout": {"nome": {"label": "Nome", "format_mask": "str", "alignment": "left"}}}
        result = await service._tratar_dados([{"nome": "João"}], payload)
        assert result["meta"] == {}

    async def test_template_format_data(self):
        """Handle data already in template format."""
        payload = {"meta": {"title": "Test"}}
        result = await service._tratar_dados([{"fields": {"nome": "João"}}], payload)
        assert "ds_items" in result


class TestFmt:
    """Tests for _fmt static method."""
    def test_none(self):
        """Return empty string for None value."""
        assert service._fmt(None, "str") == ""

    def test_int_valid(self):
        """Format integer with thousand separators."""
        assert service._fmt(1234, "int") == "1.234"

    def test_int_invalid(self):
        """Return value as string when int conversion fails."""
        assert service._fmt("abc", "int") == "abc"

    def test_float_valid(self):
        """Format float with decimal comma and thousand separators."""
        result = service._fmt(1234.5, "float")
        assert result == "1.234,50"

    def test_float_invalid(self):
        """Return value as string when float conversion fails."""
        assert service._fmt("abc", "float") == "abc"

    def test_date(self):
        """Return date value as string unchanged."""
        assert service._fmt("2024-01-01", "date") == "2024-01-01"

    def test_unknown_mask(self):
        """Return value as string for unknown format mask."""
        assert service._fmt("hello", "unknown") == "hello"


class TestGerarHtml:
    """Tests for _gerar_html method."""
    @patch("modules.shared_report_service.render_template", new_callable=AsyncMock)
    async def test_render(self, mock_render):
        """Render template with data and return HTML string."""
        mock_render.return_value = "<html>OK</html>"
        data = {"ds_items": {"groups": []}, "layout": {"groups": {"header": []}}, "meta": {"title": "T"}}
        result = await service._gerar_html(data, {})
        assert result == "<html>OK</html>"
        mock_render.assert_awaited_once()


class TestGerarPdf:
    """Tests for _gerar_pdf method."""
    @patch("modules.shared_report_service.get_pdf_from_html", new_callable=AsyncMock)
    async def test_pdf(self, mock_pdf):
        """Generate PDF bytes from HTML content."""
        mock_pdf.return_value = b"%PDF-1.4"
        result = await service._gerar_pdf("<html></html>")
        assert result == b"%PDF-1.4"
        mock_pdf.assert_awaited_once_with("<html></html>")


class TestIsTemplateFormat:
    """Tests for _is_template_format method."""
    def test_empty_list(self):
        """Return False for empty data list."""
        assert service._is_template_format([]) is False

    def test_has_fields(self):
        """Return True when records contain 'fields' key."""
        assert service._is_template_format([{"fields": {"nome": "João"}}]) is True

    def test_no_fields(self):
        """Return False when records lack 'fields' key."""
        assert service._is_template_format([{"nome": "João"}]) is False


class TestConverterDados:
    """Tests for _converter_dados method."""
    def test_template_format(self):
        """Return data wrapped in groups for template format."""
        data = [{"fields": {"nome": "João"}, "groups": []}]
        result = service._converter_dados(data, {})
        assert result == {"groups": data}

    def test_raw_without_groups(self):
        """Convert flat records without group nesting."""
        data = [{"nome": "João", "idade": 30}]
        layout = {"nome": {"label": "Nome", "format_mask": "str", "alignment": "left"}}
        result = service._converter_dados(data, layout)
        assert result["groups"][0]["fields"] == {"nome": "João", "idade": 30}

    def test_raw_with_group(self):
        """Convert records with nested group data."""
        data = [{"nome": "João", "pedidos": [{"pedido": 1, "valor": 100}]}]
        layout = {
            "nome": {"label": "Nome", "format_mask": "str", "alignment": "left"},
            "pedidos": {
                "pedido": {"label": "Pedido", "format_mask": "int", "alignment": "right"},
            },
        }
        result = service._converter_dados(data, layout)
        group = result["groups"][0]
        assert group["fields"] == {"nome": "João"}
        assert len(group["groups"]) == 1
        assert group["groups"][0]["fields"] == {"pedido": 1}

    def test_raw_with_detail(self):
        """Convert records with nested groups containing detail items."""
        data = [{"titulo": "A", "grupo": [{"campo": "x", "detalhes": [{"sub": 1}, {"sub": 2}]}]}]
        layout = {
            "titulo": {"label": "Título", "format_mask": "str", "alignment": "left"},
            "grupo": {
                "campo": {"label": "Campo", "format_mask": "str", "alignment": "left"},
                "detalhes": {
                    "sub": {"label": "Sub", "format_mask": "int", "alignment": "right"},
                },
            },
        }
        result = service._converter_dados(data, layout)
        group = result["groups"][0]
        assert group["fields"] == {"titulo": "A"}
        subgroup = group["groups"][0]
        assert subgroup["fields"] == {"campo": "x"}
        assert subgroup["detail"] == [{"sub": 1}, {"sub": 2}]

    def test_no_groups_in_fields(self):
        """Handle records where group field key is not in item fields."""
        data = [{"a": 1, "b": [{"c": 2}]}]
        layout = {"b": {"c": {"label": "C", "format_mask": "int", "alignment": "right"}}}
        result = service._converter_dados(data, layout)
        group = result["groups"][0]
        assert group["fields"] == {"a": 1}
        assert len(group["groups"]) == 1
        assert group["groups"][0]["fields"] == {"c": 2}


class TestInferirLayout:
    """Tests for _inferir_layout method."""
    def test_empty_data(self):
        """Return empty header for empty data."""
        result = service._inferir_layout([])
        assert result == {"groups": {"header": []}}

    def test_with_bool(self):
        """Infer boolean field as string type."""
        result = service._inferir_layout([{"ativo": True}])
        assert result["groups"]["header"][0]["format_mask"] == "str"

    def test_with_int(self):
        """Infer integer field with right alignment."""
        result = service._inferir_layout([{"idade": 30}])
        field = result["groups"]["header"][0]
        assert field["format_mask"] == "int"
        assert field["alignment"] == "right"

    def test_with_float(self):
        """Infer float field with right alignment."""
        result = service._inferir_layout([{"preco": 99.9}])
        field = result["groups"]["header"][0]
        assert field["format_mask"] == "float"
        assert field["alignment"] == "right"

    def test_with_str(self):
        """Infer string field with left alignment."""
        result = service._inferir_layout([{"nome": "João"}])
        field = result["groups"]["header"][0]
        assert field["format_mask"] == "str"
        assert field["alignment"] == "left"

    def test_skips_list_field(self):
        """Skip list-typed fields during layout inference."""
        result = service._inferir_layout([{"nome": "João", "itens": [1, 2]}])
        assert len(result["groups"]["header"]) == 1
        assert result["groups"]["header"][0]["name"] == "nome"

    def test_non_dict_first_item(self):
        """Return empty header when first item is not a dict."""
        result = service._inferir_layout(["string"])
        assert result == {"groups": {"header": []}}


class TestExecute:
    """Tests for the execute pipeline."""
    @patch("modules.shared_report_service.render_template", new_callable=AsyncMock)
    @patch("modules.shared_report_service.get_pdf_from_html", new_callable=AsyncMock)
    async def test_execute_success(self, mock_pdf, mock_render):
        """Execute full pipeline and return PDF bytes."""
        mock_render.return_value = "<html>OK</html>"
        mock_pdf.return_value = b"%PDF-1.4"
        result = await service.execute({"data": [{"nome": "João"}], "meta": {"title": "T"}})
        assert result == b"%PDF-1.4"

    @patch("modules.shared_report_service.render_template", new_callable=AsyncMock)
    async def test_execute_error(self, mock_render):
        """Raise exception when template rendering fails."""
        mock_render.side_effect = ValueError("render fail")
        with pytest.raises(ValueError, match="render fail"):
            await service.execute({"data": [{"nome": "João"}], "meta": {"title": "T"}})
