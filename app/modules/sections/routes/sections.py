"""
Sections module routes.
"""

import json

from robyn import Response

from modules.sections.router import router
from modules.sections.services.sections import SectionsService


@router.post("", openapi_name="Sections Report", openapi_tags=["sections"])
async def post_root(request):
    """
    Returns "Sections Report" content.
    """
    json_data = json.loads(request.body)
    service = SectionsService()
    response_data, content_type = await service.generate_report(json_data)
    return Response(description=response_data, status_code=200, headers={"Content-Type": content_type})
