"""
Main entry point for the application.
"""

import asyncio
import atexit
import importlib.util
import os

from api import Robyn, app
from extensions.log import basic_logger
from extensions.playwright_pool import close_browser, ensure_browser_sync


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
        if spec is None or spec.loader is None:
            basic_logger.error("Unable to load spec for module: %s", module_name)
            continue

        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            if hasattr(module, "init_module"):
                module.init_module(robyn_app)
                basic_logger.info("Initialized module: %s", module_name)
        except Exception as e:  # pylint: disable=broad-except
            basic_logger.error("Failed to initialize module %s: %s", module_name, e)


init_modules(app)


def main():
    """
    Main function to start the application.
    """
    # Pre-initialize Playwright browser to reduce first-request latency.
    try:
        ensure_browser_sync()
    except Exception:
        basic_logger.exception("Failed to pre-initialize Playwright browser")

    app.start()


if __name__ == "__main__":
    # Register Playwright browser cleanup at process exit to ensure resources are released.
    def _shutdown_playwright() -> None:
        try:
            asyncio.run(close_browser())
        except RuntimeError:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # event loop still running; schedule closure but cannot await here
                    loop.create_task(close_browser())
                else:
                    loop.run_until_complete(close_browser())
            except Exception:
                basic_logger.exception("Error while closing Playwright browser during shutdown")

    atexit.register(_shutdown_playwright)
    main()
