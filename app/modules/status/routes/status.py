"""
Status module routes.
"""

from robyn import Headers, Response, jsonify

from extensions.playwright_pool import ensure_browser
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


@router.get("/ready", openapi_name="Readiness Probe", openapi_tags=["status"])
async def get_ready() -> StatusResponse:
    """
    Readiness endpoint that ensures Playwright browser can be started.
    Returns 200 when browser is available, 503 otherwise.
    """
    try:
        await ensure_browser()
        return Response(
            status_code=200,
            headers=Headers({"Content-Type": "application/json"}),
            description=jsonify(StatusResponse({"status": "ready"})),
        )
    except Exception:  # pylint: disable=broad-except
        return Response(
            status_code=503,
            headers=Headers({"Content-Type": "application/json"}),
            description=jsonify(StatusResponse({"status": "not ready"})),
        )
