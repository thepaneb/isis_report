from robyn import Headers, Response, jsonify

from modules.status.models.status import StatusErrorResponse, StatusResponse
from modules.status.router import router
from modules.status.services.status import StatusService

service = StatusService()


@router.get(
    "",
    openapi_name="Application Healtcheck",
    openapi_tags=["status"],
    responses={
        500: {
            "model": StatusErrorResponse,
            "description": "Aplicação indisponível",
        },
    },
)
async def get_root() -> StatusResponse:
    try:
        response = await service.processar()

        return Response(
            status_code=200,
            headers=Headers({"Content-Type": "application/json"}),
            description=jsonify(StatusResponse(response)),
        )
    except Exception:
        return Response(
            status_code=500,
            headers=Headers({"Content-Type": "application/json"}),
            description=jsonify(StatusErrorResponse({"status": "unhealthy"})),
        )
