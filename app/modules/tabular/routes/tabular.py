"""
Tabular module routes.
"""

from robyn import Request, Response

from modules.tabular.router import router
from modules.tabular.services.tabular_service import TabularService

service = TabularService()


@router.post("", openapi_name="Tabular Report", openapi_tags=["tabular"])
async def post_root(request: Request):
    """
    Generate a tabular report.
    """
    try:
        payload = request.json()
        pdf_bytes = await service.execute(payload)
        return Response(
            status_code=200,
            headers={"Content-Type": "application/pdf"},
            description=pdf_bytes,
        )
    except Exception as e:  # pylint: disable=broad-except
        return Response(
            status_code=500,
            headers={"Content-Type": "application/json"},
            description=f'{{"error": "{str(e)}"}}',
        )
