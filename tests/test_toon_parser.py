
from utils.toon_parser import ToonParser

parser = ToonParser()


class TestConvertValue:
    def test_true(self):
        assert parser._convert_value("true") is True
        assert parser._convert_value("TRUE") is True

    def test_false(self):
        assert parser._convert_value("false") is False
        assert parser._convert_value("FALSE") is False

    def test_int(self):
        assert parser._convert_value("123") == 123
        assert parser._convert_value("0") == 0
        assert parser._convert_value("-42") == -42

    def test_float(self):
        assert parser._convert_value("12.5") == 12.5
        assert parser._convert_value("0.99") == 0.99

    def test_string(self):
        assert parser._convert_value("hello") == "hello"
        assert parser._convert_value("abc123") == "abc123"

    def test_strip(self):
        assert parser._convert_value("  abc  ") == "abc"

    def test_int_edge(self):
        assert parser._convert_value("12abc") == "12abc"

    def test_float_edge(self):
        assert parser._convert_value("12.5.5") == "12.5.5"


class TestTokenize:
    def test_simple_lines(self):
        tokens = parser._tokenize("key: value\nother: 123")
        assert tokens == [(0, "key: value"), (0, "other: 123")]

    def test_indented_lines(self):
        tokens = parser._tokenize("key:\n  sub: val")
        assert tokens == [(0, "key:"), (1, "sub: val")]

    def test_skip_empty(self):
        tokens = parser._tokenize("key: val\n\n\nother: 2")
        assert tokens == [(0, "key: val"), (0, "other: 2")]

    def test_mixed_indent(self):
        tokens = parser._tokenize("a:\n  b:\n    c: 1")
        assert tokens == [(0, "a:"), (1, "b:"), (2, "c: 1")]

    def test_trailing_whitespace(self):
        tokens = parser._tokenize("key: val   \n  sub: x   ")
        assert tokens == [(0, "key: val"), (1, "sub: x")]


class TestParseDict:
    def test_simple_key_value(self):
        result, i = parser._parse_dict([(0, "key: value")], 0, 0)
        assert result == {"key": "value"}
        assert i == 1

    def test_nested_dict(self):
        tokens = [(0, "key:"), (1, "sub: val"), (1, "num: 42")]
        result, i = parser._parse_dict(tokens, 0, 0)
        assert result == {"key": {"sub": "val", "num": 42}}

    def test_array_with_count(self):
        tokens = [(0, "items[2]:"), (1, "- a: 1"), (1, "- b: 2")]
        result, i = parser._parse_dict(tokens, 0, 0)
        assert result == {"items": [{"a": 1}, {"b": 2}]}

    def test_array_with_fields(self):
        tokens = [(0, 'items[2]{nome,valor}:'), (1, 'foo,10'), (1, 'bar,20')]
        result, i = parser._parse_dict(tokens, 0, 0)
        assert result == {"items": [{"nome": "foo", "valor": 10}, {"nome": "bar", "valor": 20}]}

    def test_inline_layout(self):
        result, i = parser._parse_dict([(0, 'empresa{Empresa,str,left}')], 0, 0)
        assert result == {"empresa": {"label": "Empresa", "format_mask": "str", "alignment": "left"}}

    def test_dash_line_skipped(self):
        result, i = parser._parse_dict([(0, "- item ignorado"), (0, "key: val")], 0, 0)
        assert result == {"key": "val"}

    def test_wrong_level_break(self):
        tokens = [(0, "ext:"), (1, "sub: val"), (2, "deep: x")]
        result, i = parser._parse_dict(tokens, 1, 0)
        assert result == {}

    def test_empty_dict_value(self):
        tokens = [(0, "key:"), (1, "- item: 1")]
        result, i = parser._parse_dict(tokens, 0, 0)
        assert result == {"key": {}}

    def test_unknown_line_skip(self):
        result, i = parser._parse_dict([(0, "???")], 0, 0)
        assert result == {}

    def test_int_value(self):
        result, i = parser._parse_dict([(0, "num: 42")], 0, 0)
        assert result == {"num": 42}

    def test_float_value(self):
        result, i = parser._parse_dict([(0, "pi: 3.14")], 0, 0)
        assert result == {"pi": 3.14}

    def test_empty_value_key(self):
        tokens = [(0, "empty:"), (1, "   ")]
        result, i = parser._parse_dict(tokens, 0, 0)
        assert result == {"empty": {}}

    def test_wrong_level_continue(self):
        tokens = [(0, "ext:"), (2, "deep: x")]
        result, i = parser._parse_dict(tokens, 0, 0)
        assert "ext" in result


class TestParseArray:
    def test_simple_items(self):
        tokens = [(1, "- a"), (1, "- b")]
        result, i = parser._parse_array(tokens, 0, 1)
        assert result == ["a", "b"]

    def test_kv_items(self):
        tokens = [(1, "- nome: foo"), (1, "- nome: bar")]
        result, i = parser._parse_array(tokens, 0, 1)
        assert result == [{"nome": "foo"}, {"nome": "bar"}]

    def test_nested_items(self):
        tokens = [(1, "- item:"), (2, "sub: val")]
        result, i = parser._parse_array(tokens, 0, 1)
        assert result == [{"item": {"sub": "val"}}]

    def test_wrong_level_break(self):
        tokens = [(0, "key: val")]
        result, i = parser._parse_array(tokens, 0, 1)
        assert result == []

    def test_wrong_level_continue(self):
        tokens = [(1, "- a"), (2, "  extra")]
        result, i = parser._parse_array(tokens, 0, 1)
        assert result == ["a"]


class TestParse:
    def test_dados_to_data(self):
        result = parser.parse("dados[1]:\n  - item: 1")
        assert "data" in result
        assert "dados" not in result
        assert result["data"] == [{"item": 1}]

    def test_full_parse(self):
        text = "meta:\n  title: Teste\nlayout:\n  campo{Label,str,left}\ndados[1]:\n  - nome: foo"
        result = parser.parse(text)
        assert result["meta"] == {"title": "Teste"}
        assert "campo" in result["layout"]
        assert len(result["data"]) == 1

    def test_empty_text(self):
        result = parser.parse("")
        assert result == {}

    def test_no_dados(self):
        result = parser.parse("key: value")
        assert "data" not in result
        assert result == {"key": "value"}
