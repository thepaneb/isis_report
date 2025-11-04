"""
Status module initialization.
"""

from api import Robyn

from extensions.routes_loader import init_routes
from modules.status.router import router


def init_module(robyn_app: Robyn):
    """
    Initialize the status module.
    """
    init_routes(__file__)
    robyn_app.include_router(router)
