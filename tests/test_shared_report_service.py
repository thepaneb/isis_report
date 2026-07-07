from unittest.mock import AsyncMock, patch

import pytest

from modules.shared_report_service import SharedReportService

service = SharedReportService()


class TestObterDados:
    async def test_has_data(self):
        result = await service._obter_dados({"data": [1, 2]})
        assert result == [1, 2]

    async def test_missing_data(self):
        result = await service._obter_dados({"meta": {}})
        assert result == []


class TestTratarDados:
    async def test_with_layout(self):
        payload = {
            "meta": {"title": "Test"},
            "layout": {"nome": {"label": "Nome", "format_mask": "str", "alignment": "left"}},
        }
        result = await service._tratar_dados([{"nome": "João"}], payload)
        assert "ds_items" in result
        assert "layout" in result
        assert result["meta"] == {"title": "Test"}

    async def test_without_layout(self):
        payload = {"meta": {"title": "Test"}}
        result = await service._tratar_dados([{"nome": "João", "idade": 30}], payload)
        layout = result["layout"]
        assert len(layout["groups"]["header"]) == 2
        assert layout["groups"]["header"][0]["name"] == "nome"
        assert layout["groups"]["header"][1]["name"] == "idade"
        assert layout["groups"]["header"][1]["format_mask"] == "int"

    async def test_empty_meta(self):
        payload = {"layout": {"nome": {"label": "Nome", "format_mask": "str", "alignment": "left"}}}
        result = await service._tratar_dados([{"nome": "João"}], payload)
        assert result["meta"] == {}

    async def test_template_format_data(self):
        payload = {"meta": {"title": "Test"}}
        result = await service._tratar_dados([{"fields": {"nome": "João"}}], payload)
        assert "ds_items" in result


class TestFmt:
    def test_none(self):
        assert service._fmt(None, "str") == ""

    def test_int_valid(self):
        assert service._fmt(1234, "int") == "1.234"

    def test_int_invalid(self):
        assert service._fmt("abc", "int") == "abc"

    def test_float_valid(self):
        result = service._fmt(1234.5, "float")
        assert result == "1.234,50"

    def test_float_invalid(self):
        assert service._fmt("abc", "float") == "abc"

    def test_date(self):
        assert service._fmt("2024-01-01", "date") == "2024-01-01"

    def test_unknown_mask(self):
        assert service._fmt("hello", "unknown") == "hello"


class TestGerarHtml:
    @patch("modules.shared_report_service.render_template", new_callable=AsyncMock)
    async def test_render(self, mock_render):
        mock_render.return_value = "<html>OK</html>"
        data = {"ds_items": {"groups": []}, "layout": {"groups": {"header": []}}, "meta": {"title": "T"}}
        result = await service._gerar_html(data, {})
        assert result == "<html>OK</html>"
        mock_render.assert_awaited_once()


class TestGerarPdf:
    @patch("modules.shared_report_service.get_pdf_from_html", new_callable=AsyncMock)
    async def test_pdf(self, mock_pdf):
        mock_pdf.return_value = b"%PDF-1.4"
        result = await service._gerar_pdf("<html></html>")
        assert result == b"%PDF-1.4"
        mock_pdf.assert_awaited_once_with("<html></html>")


class TestIsTemplateFormat:
    def test_empty_list(self):
        assert service._is_template_format([]) is False

    def test_has_fields(self):
        assert service._is_template_format([{"fields": {"nome": "João"}}]) is True

    def test_no_fields(self):
        assert service._is_template_format([{"nome": "João"}]) is False


class TestConverterDados:
    def test_template_format(self):
        data = [{"fields": {"nome": "João"}, "groups": []}]
        result = service._converter_dados(data, {})
        assert result == {"groups": data}

    def test_raw_without_groups(self):
        data = [{"nome": "João", "idade": 30}]
        layout = {"nome": {"label": "Nome", "format_mask": "str", "alignment": "left"}}
        result = service._converter_dados(data, layout)
        assert result["groups"][0]["fields"] == {"nome": "João", "idade": 30}

    def test_raw_with_group(self):
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
        data = [{"a": 1, "b": [{"c": 2}]}]
        layout = {"b": {"c": {"label": "C", "format_mask": "int", "alignment": "right"}}}
        result = service._converter_dados(data, layout)
        group = result["groups"][0]
        assert group["fields"] == {"a": 1}
        assert len(group["groups"]) == 1
        assert group["groups"][0]["fields"] == {"c": 2}


class TestInferirLayout:
    def test_empty_data(self):
        result = service._inferir_layout([])
        assert result == {"groups": {"header": []}}

    def test_with_bool(self):
        result = service._inferir_layout([{"ativo": True}])
        assert result["groups"]["header"][0]["format_mask"] == "str"

    def test_with_int(self):
        result = service._inferir_layout([{"idade": 30}])
        field = result["groups"]["header"][0]
        assert field["format_mask"] == "int"
        assert field["alignment"] == "right"

    def test_with_float(self):
        result = service._inferir_layout([{"preco": 99.9}])
        field = result["groups"]["header"][0]
        assert field["format_mask"] == "float"
        assert field["alignment"] == "right"

    def test_with_str(self):
        result = service._inferir_layout([{"nome": "João"}])
        field = result["groups"]["header"][0]
        assert field["format_mask"] == "str"
        assert field["alignment"] == "left"

    def test_skips_list_field(self):
        result = service._inferir_layout([{"nome": "João", "itens": [1, 2]}])
        assert len(result["groups"]["header"]) == 1
        assert result["groups"]["header"][0]["name"] == "nome"

    def test_non_dict_first_item(self):
        result = service._inferir_layout(["string"])
        assert result == {"groups": {"header": []}}


class TestExecute:
    @patch("modules.shared_report_service.render_template", new_callable=AsyncMock)
    @patch("modules.shared_report_service.get_pdf_from_html", new_callable=AsyncMock)
    async def test_execute_success(self, mock_pdf, mock_render):
        mock_render.return_value = "<html>OK</html>"
        mock_pdf.return_value = b"%PDF-1.4"
        result = await service.execute({"data": [{"nome": "João"}], "meta": {"title": "T"}})
        assert result == b"%PDF-1.4"

    @patch("modules.shared_report_service.render_template", new_callable=AsyncMock)
    async def test_execute_error(self, mock_render):
        mock_render.side_effect = ValueError("render fail")
        with pytest.raises(ValueError, match="render fail"):
            await service.execute({"data": [{"nome": "João"}], "meta": {"title": "T"}})
