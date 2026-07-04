"""
Initialize routes loader extension.
"""

import importlib.util
import os

from extensions.log import basic_logger


def init_routes(file):
    """
    Initialize routes for the hello_world module.
    """
    routes_dir = os.path.join(os.path.dirname(file), "routes")

    for module_name in [
        name
        for name in os.listdir(routes_dir)
        if name.endswith(".py") and not name.startswith("__") and os.path.isfile(os.path.join(routes_dir, name))
    ]:
        route_file = os.path.join(routes_dir, module_name)
        spec = importlib.util.spec_from_file_location(module_name, route_file)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            basic_logger.info("Loaded route: %s", module_name)
        except Exception:  # pylint: disable=broad-except # noqa: BLE001
            basic_logger.exception("Failed to load route %s", module_name)
