"""Tabular JSON module initialization."""
from api import Robyn
from extensions.routes_loader import init_routes
from modules.tabular_json.router import router


def init_module(robyn_app: Robyn):
    """Initialize tabular JSON module routes."""
    init_routes(__file__)
    robyn_app.include_router(router)
