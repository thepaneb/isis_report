import importlib.util
from pathlib import Path

import pytest


def _load_status_route_module():
    path = Path("app/modules/status/routes/status.py").resolve()
    spec = importlib.util.spec_from_file_location("tests.status_route", str(path))
    module = importlib.util.module_from_spec(spec)
    # Ensure `modules` package imports resolve by adding `app/` to sys.path
    import sys

    app_dir = str(Path("app").resolve())
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)

    # Prevent route registration side-effects by patching the router decorator
    try:
        router_mod = importlib.import_module("modules.status.router")
        original_get = getattr(router_mod.router, "get", None)

        def _noop_get(*_args, **_kwargs):
            def _decorator(fn):
                return fn

            return _decorator

        setattr(router_mod.router, "get", _noop_get)
    except Exception:
        router_mod = None
        original_get = None

    try:
        spec.loader.exec_module(module)
    finally:
        if router_mod is not None and original_get is not None:
            setattr(router_mod.router, "get", original_get)
    return module


@pytest.mark.asyncio
async def test_ready_success(monkeypatch):
    module = _load_status_route_module()

    async def fake_ensure():
        return None

    monkeypatch.setattr(module, "ensure_browser", fake_ensure)

    resp = await module.get_ready()

    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_ready_failure(monkeypatch):
    module = _load_status_route_module()

    async def fake_ensure():
        raise RuntimeError("no browser")

    monkeypatch.setattr(module, "ensure_browser", fake_ensure)

    resp = await module.get_ready()

    assert resp.status_code == 503
