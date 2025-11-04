"""
API initialization for the Robyn application.
"""

from robyn import Robyn
from robyn.openapi import OpenAPI, OpenAPIInfo

app = Robyn(
    file_object=__file__,
    openapi=OpenAPI(
        info=OpenAPIInfo(
            title="Isis Report API",
            description="Isis Report with Robyn",
            version="0.1.0",
        )
    ),
)
