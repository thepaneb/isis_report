"""
Status module routes.
"""

from robyn import Headers, Response, jsonify

from modules.status.models.status import StatusResponse
from modules.status.router import router
from modules.status.services.status import StatusService


service = StatusService()


@router.get("", openapi_name="Application Healtcheck", openapi_tags=["status"])
async def get_root() -> StatusResponse:
    """
    Returns the application status.
    """
    try:
        response = await service.processar()

        return Response(
            status_code=200,
            headers=Headers({"Content-Type": "application/json"}),
            description=jsonify(StatusResponse(response)),
        )
    except Exception:  # pylint: disable=broad-except
        return Response(
            status_code=500,
            headers=Headers({"Content-Type": "application/json"}),
            description=jsonify(StatusResponse({"status": "unhealthy"})),
        )
