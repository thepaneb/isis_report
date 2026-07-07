from utils.layout_converter import _format_field, converter_layout_hierarquico


class TestFormatField:
    def test_all_fields(self):
        result = _format_field("nome", {"label": "Nome", "format_mask": "str", "alignment": "left"})
        assert result == {"name": "nome", "label": "Nome", "format_mask": "str", "alignment": "left"}

    def test_missing_label(self):
        result = _format_field("nome", {"format_mask": "int", "alignment": "right"})
        assert result["label"] == "nome"

    def test_missing_format_mask(self):
        result = _format_field("nome", {"label": "Nome"})
        assert result["format_mask"] == "str"

    def test_missing_alignment(self):
        result = _format_field("nome", {"label": "Nome"})
        assert result["alignment"] == "left"


class TestConverterLayoutHierarquico:
    def test_empty(self):
        result = converter_layout_hierarquico({})
        assert result == {"groups": {"header": []}}

    def test_simple_fields(self):
        result = converter_layout_hierarquico({
            "nome": {"label": "Nome", "format_mask": "str", "alignment": "left"},
            "idade": {"label": "Idade", "format_mask": "int", "alignment": "right"},
        })
        assert len(result["groups"]["header"]) == 2
        assert result["groups"]["header"][0]["name"] == "nome"
        assert result["groups"]["header"][1]["name"] == "idade"

    def test_single_group(self):
        result = converter_layout_hierarquico({
            "empresa": {"label": "Empresa", "format_mask": "str", "alignment": "left"},
            "pedidos": {
                "pedido": {"label": "Pedido", "format_mask": "int", "alignment": "right"},
                "valor": {"label": "Valor", "format_mask": "float", "alignment": "right"},
            },
        })
        header = result["groups"]["header"]
        assert header[0]["name"] == "empresa"
        groups = result["groups"]["groups"]
        assert groups["header"][0]["name"] == "pedido"
        assert groups["header"][1]["name"] == "valor"

    def test_group_with_detail(self):
        result = converter_layout_hierarquico({
            "titulo": {"label": "Título", "format_mask": "str", "alignment": "left"},
            "grupo": {
                "campo1": {"label": "Campo 1", "format_mask": "str", "alignment": "left"},
                "detalhes": {
                    "sub1": {"label": "Sub 1", "format_mask": "str", "alignment": "left"},
                    "sub2": {"label": "Sub 2", "format_mask": "int", "alignment": "right"},
                },
            },
        })
        groups = result["groups"]["groups"]
        assert groups["header"][0]["name"] == "campo1"
        assert len(groups["detail"]) == 2
        assert groups["detail"][0]["name"] == "sub1"
        assert groups["detail"][1]["name"] == "sub2"

    def test_only_group_no_simple(self):
        result = converter_layout_hierarquico({
            "pedidos": {
                "pedido": {"label": "Pedido", "format_mask": "int", "alignment": "right"},
            },
        })
        assert result["groups"]["header"] == []
        assert result["groups"]["groups"]["header"][0]["name"] == "pedido"
