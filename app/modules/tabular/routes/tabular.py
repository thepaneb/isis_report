"""
Tabular module routes.
"""

import json

from robyn import Response

from modules.tabular.router import router
from modules.tabular.services.tabular import TabularService


@router.post("", openapi_name="Tabular Report", openapi_tags=["tabular"])
async def post_root(request):
    """
    Returns "Tabular Report" content.
    """
    json_data = json.loads(request.body)
    service = TabularService()
    response_data, content_type = await service.generate_report(json_data)
    return Response(description=response_data, status_code=200, headers={"Content-Type": content_type})
