from typing import Any


def _format_field(name: str, field_def: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "label": field_def.get("label", name),
        "format_mask": field_def.get("format_mask", "str"),
        "alignment": field_def.get("alignment", "left"),
    }


def converter_layout_hierarquico(layout_raw: dict[str, Any]) -> dict[str, Any]:
    header = []
    groups = None

    for key, value in layout_raw.items():
        if isinstance(value, dict) and "label" in value:
            header.append(_format_field(key, value))
        elif isinstance(value, dict):
            field_header = []
            detail = []
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, dict) and "label" in sub_value:
                    field_header.append(_format_field(sub_key, sub_value))
                elif isinstance(sub_value, dict):
                    for inner_key, inner_value in sub_value.items():
                        if isinstance(inner_value, dict) and "label" in inner_value:
                            detail.append(_format_field(inner_key, inner_value))
            if groups is None:
                groups = {}
            groups["header"] = field_header
            if detail:
                groups["detail"] = detail

    result = {"groups": {"header": header}}
    if groups:
        result["groups"]["groups"] = groups

    return result
