"""
Main entry point for the application.
"""

import importlib.util
import os

from api import Robyn, app
from extensions.log import basic_logger


def init_modules(robyn_app: Robyn):
    """
    Initialize application modules.
    """
    modules_dir = os.path.join(os.path.dirname(__file__), "modules")

    for module_name in [
        name
        for name in os.listdir(modules_dir)
        if os.path.isdir(os.path.join(modules_dir, name))
        and not name.startswith("__")
        and os.path.isfile(os.path.join(modules_dir, name, "__init__.py"))
    ]:
        init_file = os.path.join(modules_dir, module_name, "__init__.py")
        spec = importlib.util.spec_from_file_location(module_name, init_file)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            if hasattr(module, "init_module"):
                module.init_module(robyn_app)
                basic_logger.info("Initialized module: %s", module_name)
        except Exception:  # pylint: disable=broad-except  # noqa: BLE001
            basic_logger.exception("Failed to initialize module %s", module_name)


init_modules(app)


def main():
    """
    Main function to start the application.
    """
    app.start()


if __name__ == "__main__":
    main()
