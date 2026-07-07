"""Tabular JSON HTTP routes."""
import json

from robyn import Request, Response

from modules.tabular_json.models.tabular_json import ErrorResponse, ReportPayload
from modules.tabular_json.router import router
from modules.tabular_json.services.tabular_json_service import TabularJsonService

service = TabularJsonService()


@router.post(
    "",
    openapi_name="Relatório Tabular JSON",
    openapi_tags=["tabular-json"],
    responses={
        500: {
            "model": ErrorResponse,
            "description": "Erro interno ao gerar o relatório",
        },
    },
)
async def post_root(request: Request, payload: ReportPayload):
    """Generate PDF report from JSON payload."""
    try:
        pdf_bytes = await service.execute(payload.model_dump())
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
