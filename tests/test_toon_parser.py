"""Tests for ToonParser."""
from utils.toon_parser import ToonParser

parser = ToonParser()


class TestConvertValue:
    """Tests for _convert_value static method."""
    def test_true(self):
        """Convert 'true' strings to boolean True."""
        assert parser._convert_value("true") is True
        assert parser._convert_value("TRUE") is True

    def test_false(self):
        """Convert 'false' strings to boolean False."""
        assert parser._convert_value("false") is False
        assert parser._convert_value("FALSE") is False

    def test_int(self):
        """Convert numeric strings to integers."""
        assert parser._convert_value("123") == 123
        assert parser._convert_value("0") == 0
        assert parser._convert_value("-42") == -42

    def test_float(self):
        """Convert decimal strings to floats."""
        assert parser._convert_value("12.5") == 12.5
        assert parser._convert_value("0.99") == 0.99

    def test_string(self):
        """Return non-numeric strings unchanged."""
        assert parser._convert_value("hello") == "hello"
        assert parser._convert_value("abc123") == "abc123"

    def test_strip(self):
        """Strip whitespace from input values."""
        assert parser._convert_value("  abc  ") == "abc"

    def test_int_edge(self):
        """Return mixed alphanumeric strings unchanged."""
        assert parser._convert_value("12abc") == "12abc"

    def test_float_edge(self):
        """Return malformed float strings unchanged."""
        assert parser._convert_value("12.5.5") == "12.5.5"


class TestTokenize:
    """Tests for _tokenize method."""
    def test_simple_lines(self):
        """Tokenize flat key-value lines."""
        tokens = parser._tokenize("key: value\nother: 123")
        assert tokens == [(0, "key: value"), (0, "other: 123")]

    def test_indented_lines(self):
        """Tokenize indented lines with correct level."""
        tokens = parser._tokenize("key:\n  sub: val")
        assert tokens == [(0, "key:"), (1, "sub: val")]

    def test_skip_empty(self):
        """Skip empty lines during tokenization."""
        tokens = parser._tokenize("key: val\n\n\nother: 2")
        assert tokens == [(0, "key: val"), (0, "other: 2")]

    def test_mixed_indent(self):
        """Tokenize multi-level nested indentation."""
        tokens = parser._tokenize("a:\n  b:\n    c: 1")
        assert tokens == [(0, "a:"), (1, "b:"), (2, "c: 1")]

    def test_trailing_whitespace(self):
        """Strip trailing whitespace from tokens."""
        tokens = parser._tokenize("key: val   \n  sub: x   ")
        assert tokens == [(0, "key: val"), (1, "sub: x")]


class TestParseDict:
    """Tests for _parse_dict method."""
    def test_simple_key_value(self):
        """Parse a simple key-value pair."""
        result, i = parser._parse_dict([(0, "key: value")], 0, 0)
        assert result == {"key": "value"}
        assert i == 1

    def test_nested_dict(self):
        """Parse nested dictionary structure."""
        tokens = [(0, "key:"), (1, "sub: val"), (1, "num: 42")]
        result, i = parser._parse_dict(tokens, 0, 0)
        assert result == {"key": {"sub": "val", "num": 42}}

    def test_array_with_count(self):
        """Parse array with count notation."""
        tokens = [(0, "items[2]:"), (1, "- a: 1"), (1, "- b: 2")]
        result, i = parser._parse_dict(tokens, 0, 0)
        assert result == {"items": [{"a": 1}, {"b": 2}]}

    def test_array_with_fields(self):
        """Parse array with inline field definitions."""
        tokens = [(0, 'items[2]{nome,valor}:'), (1, 'foo,10'), (1, 'bar,20')]
        result, i = parser._parse_dict(tokens, 0, 0)
        assert result == {"items": [{"nome": "foo", "valor": 10}, {"nome": "bar", "valor": 20}]}

    def test_inline_layout(self):
        """Parse inline layout field definitions."""
        result, i = parser._parse_dict([(0, 'empresa{Empresa,str,left}')], 0, 0)
        assert result == {"empresa": {"label": "Empresa", "format_mask": "str", "alignment": "left"}}

    def test_dash_line_skipped(self):
        """Skip dash-prefixed lines in dict parsing."""
        result, i = parser._parse_dict([(0, "- item ignorado"), (0, "key: val")], 0, 0)
        assert result == {"key": "val"}

    def test_wrong_level_break(self):
        """Break parsing when token level is lower than expected."""
        tokens = [(0, "ext:"), (1, "sub: val"), (2, "deep: x")]
        result, i = parser._parse_dict(tokens, 1, 0)
        assert result == {}

    def test_empty_dict_value(self):
        """Parse key with empty dict value."""
        tokens = [(0, "key:"), (1, "- item: 1")]
        result, i = parser._parse_dict(tokens, 0, 0)
        assert result == {"key": {}}

    def test_unknown_line_skip(self):
        """Skip unrecognized line formats."""
        result, i = parser._parse_dict([(0, "???")], 0, 0)
        assert result == {}

    def test_int_value(self):
        """Parse integer values from key-value lines."""
        result, i = parser._parse_dict([(0, "num: 42")], 0, 0)
        assert result == {"num": 42}

    def test_float_value(self):
        """Parse float values from key-value lines."""
        result, i = parser._parse_dict([(0, "pi: 3.14")], 0, 0)
        assert result == {"pi": 3.14}

    def test_empty_value_key(self):
        """Handle key with blank value as empty dict."""
        tokens = [(0, "empty:"), (1, "   ")]
        result, i = parser._parse_dict(tokens, 0, 0)
        assert result == {"empty": {}}

    def test_wrong_level_continue(self):
        """Skip deeper level tokens and continue parsing."""
        tokens = [(0, "ext:"), (2, "deep: x")]
        result, i = parser._parse_dict(tokens, 0, 0)
        assert "ext" in result


class TestParseArray:
    """Tests for _parse_array method."""
    def test_simple_items(self):
        """Parse list of simple scalar items."""
        tokens = [(1, "- a"), (1, "- b")]
        result, i = parser._parse_array(tokens, 0, 1)
        assert result == ["a", "b"]

    def test_kv_items(self):
        """Parse list of key-value items."""
        tokens = [(1, "- nome: foo"), (1, "- nome: bar")]
        result, i = parser._parse_array(tokens, 0, 1)
        assert result == [{"nome": "foo"}, {"nome": "bar"}]

    def test_nested_items(self):
        """Parse list with nested dictionary items."""
        tokens = [(1, "- item:"), (2, "sub: val")]
        result, i = parser._parse_array(tokens, 0, 1)
        assert result == [{"item": {"sub": "val"}}]

    def test_wrong_level_break(self):
        """Return empty list when level does not match."""
        tokens = [(0, "key: val")]
        result, i = parser._parse_array(tokens, 0, 1)
        assert result == []

    def test_wrong_level_continue(self):
        """Skip deeper level items and continue."""
        tokens = [(1, "- a"), (2, "  extra")]
        result, i = parser._parse_array(tokens, 0, 1)
        assert result == ["a"]


class TestParse:
    """Tests for parse method."""
    def test_dados_to_data(self):
        """Rename 'dados' key to 'data' in parsed result."""
        result = parser.parse("dados[1]:\n  - item: 1")
        assert "data" in result
        assert "dados" not in result
        assert result["data"] == [{"item": 1}]

    def test_full_parse(self):
        """Parse a complete .toon document with meta, layout and data."""
        text = "meta:\n  title: Teste\nlayout:\n  campo{Label,str,left}\ndados[1]:\n  - nome: foo"
        result = parser.parse(text)
        assert result["meta"] == {"title": "Teste"}
        assert "campo" in result["layout"]
        assert len(result["data"]) == 1

    def test_empty_text(self):
        """Return empty dict for empty input."""
        result = parser.parse("")
        assert result == {}

    def test_no_dados(self):
        """Return parsed dict without 'data' key when 'dados' is absent."""
        result = parser.parse("key: value")
        assert "data" not in result
        assert result == {"key": "value"}
