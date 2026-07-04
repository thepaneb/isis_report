"""
Sections module initialization.
"""

from api import Robyn
from extensions.routes_loader import init_routes
from modules.sections.router import router


def init_module(robyn_app: Robyn):
    """
    Initialize the sections module.
    """
    init_routes(__file__)
    robyn_app.include_router(router)
