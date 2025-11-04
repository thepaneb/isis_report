"""
Hello world module initialization.
"""

from api import Robyn

from extensions.routes_loader import init_routes
from modules.hello_world.router import router


def init_module(robyn_app: Robyn):
    """
    Initialize the hello_world module.
    """
    init_routes(__file__)
    robyn_app.include_router(router)
