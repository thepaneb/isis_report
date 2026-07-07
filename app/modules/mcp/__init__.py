import base64
import json

from robyn import Robyn

from modules.tabular_json.services.tabular_json_service import TabularJsonService
from modules.tabular_toon.services.tabular_toon_service import TabularToonService
from utils.toon_parser import ToonParser

tabular_json_service = TabularJsonService()
tabular_toon_service = TabularToonService()
toon_parser = ToonParser()


def init_module(robyn_app: Robyn):

    _EXEMPLO_JSON = {
        "meta": {
            "title": "Pedido de Vendas",
            "sub_title": "De 01/01/2024 até 31/12/2024",
            "mode": "exact",
        },
        "layout": {
            "empresa": {"label": "Empresa", "format_mask": "str", "alignment": "left"},
            "data_entrega": {"label": "Data Entrega", "format_mask": "date", "alignment": "center"},
            "pedidos": {
                "pedido": {"label": "Código", "format_mask": "int", "alignment": "right"},
                "data_pedido": {"label": "Data Pedido", "format_mask": "date", "alignment": "center"},
                "nome_produto": {"label": "Produto", "format_mask": "str", "alignment": "left"},
                "total_tarifa": {"label": "Total Tarifa", "format_mask": "float", "alignment": "right"},
                "valor_total": {"label": "Valor Total", "format_mask": "float", "alignment": "right"},
                "cargas": {
                    "qtde": {"label": "Quantidade", "format_mask": "int", "alignment": "right"},
                    "valor_unitario": {"label": "Valor Unitário", "format_mask": "float", "alignment": "right"},
                    "valor_total": {"label": "Valor Total", "format_mask": "float", "alignment": "right"},
                },
            },
        },
        "data": [
            {
                "empresa": "CQ CONSULTORIA ADMINITRATIVA",
                "data_entrega": "01/12/2024",
                "pedidos": [
                    {
                        "pedido": 750,
                        "data_pedido": "01/12/2024",
                        "nome_produto": "CQ REFEIÇÃO",
                        "total_tarifa": 9.01,
                        "valor_total": 4000,
                        "cargas": [
                            {"qtde": 1, "valor_unitario": 1500, "valor_total": 1500},
                            {"qtde": 1, "valor_unitario": 1000, "valor_total": 1000},
                            {"qtde": 1, "valor_unitario": 1500, "valor_total": 1500},
                        ],
                    },
                ],
            },
        ],
    }

    @robyn_app.mcp.tool(
        name="gerar_relatorio_json",
        description="Gera relatório PDF a partir de payload JSON com meta, layout e data",
        input_schema={
            "type": "object",
            "properties": {
                "meta": {
                    "type": "object",
                    "description": "Metadados: title, sub_title, mode (exact|gray)",
                },
                "data": {
                    "type": "array",
                    "description": "Registros do relatório, opcionalmente com groups aninhados",
                },
                "layout": {
                    "type": "object",
                    "description": "Definição hierárquica dos campos (omitir para inferir dos dados)",
                },
            },
            "required": ["meta", "data"],
            "examples": [_EXEMPLO_JSON],
        },
    )
    async def gerar_relatorio_json(meta: dict, data: list, layout: dict | None = None) -> str:
        pdf_bytes = await tabular_json_service.execute({
            "meta": meta,
            "layout": layout,
            "data": data,
        })
        return json.dumps({
            "pdf_base64": base64.b64encode(pdf_bytes).decode(),
            "size_bytes": len(pdf_bytes),
        })

    _EXEMPLO_TOON = """\
meta:
  title: Pedido de Vendas
  sub_title: De 01/01/2024 até 31/12/2024
  mode: exact
layout:
  empresa{Empresa,str,left}
  data_entrega{Data Entrega,date,center}
  pedidos:
    pedido{Código,int,right}
    data_pedido{Data Pedido,date,center}
    nome_produto{Produto,str,left}
    total_tarifa{Total Tarifa,float,right}
    valor_total{Valor Total,float,right}
    cargas:
      qtde{Quantidade,int,right}
      valor_unitario{Valor Unitário,float,right}
      valor_total{Valor Total,float,right}
dados[1]:
  - empresa: CQ CONSULTORIA ADMINITRATIVA
    data_entrega: 01/12/2024
    pedidos[1]:
      - pedido: 750
        data_pedido: 01/12/2024
        nome_produto: CQ REFEIÇÃO
        total_tarifa: 9.01
        valor_total: 4000
        cargas[3]{qtde,valor_unitario,valor_total}:
          1,1500,1500
          1,1000,1000
          1,1500,1500
"""

    @robyn_app.mcp.tool(
        name="gerar_relatorio_toon",
        description="Gera relatório PDF a partir de texto no formato .toon",
        input_schema={
            "type": "object",
            "properties": {
                "conteudo_toon": {
                    "type": "string",
                    "description": "Texto no formato .toon com as seções meta, layout e dados",
                },
            },
            "required": ["conteudo_toon"],
            "examples": [{"conteudo_toon": _EXEMPLO_TOON}],
        },
    )
    async def gerar_relatorio_toon(conteudo_toon: str) -> str:
        payload = toon_parser.parse(conteudo_toon)
        pdf_bytes = await tabular_toon_service.execute(payload)
        return json.dumps({
            "pdf_base64": base64.b64encode(pdf_bytes).decode(),
            "size_bytes": len(pdf_bytes),
        })
