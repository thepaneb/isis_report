"""
Sections module routes.
"""

from robyn import Request, Response

from modules.sections.router import router
from modules.sections.services.sections_service import SectionsService

service = SectionsService()


@router.post("", openapi_name="Sections Report", openapi_tags=["sections"])
async def post_root(request: Request):
    """
    Generate a sections report.
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
