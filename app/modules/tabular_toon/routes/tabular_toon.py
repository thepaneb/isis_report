"""Tabular .toon HTTP routes."""
import json

from robyn import Request, Response

from modules.tabular_toon.models.tabular_toon import ErrorResponse
from modules.tabular_toon.router import router
from modules.tabular_toon.services.tabular_toon_service import TabularToonService
from utils.toon_parser import ToonParser

service = TabularToonService()
parser = ToonParser()


@router.post(
    "",
    openapi_name="Relatório Tabular .toon",
    openapi_tags=["tabular-toon"],
    responses={
        500: {
            "model": ErrorResponse,
            "description": "Erro interno ao gerar o relatório",
        },
    },
)
async def post_root(request: Request):
    """Generate PDF report from .toon text payload."""
    try:
        body = request.body
        text = body.decode("utf-8") if isinstance(body, bytes) else body
        payload = parser.parse(text)

        pdf_bytes = await service.execute(payload)
        return Response(
            status_code=200,
            headers={"Content-Type": "application/pdf"},
            description=pdf_bytes,
        )
    except Exception as e:
        return Response(
            status_code=500,
            headers={"Content-Type": "application/json"},
            description=json.dumps({"error": str(e)}),
        )
