"""
Lightweight Playwright browser pool (singleton) for reuse across requests.

This module provides helpers to obtain a page instance without launching
Chromium on every request. Call `new_page()` to receive a fresh page and
`close_browser()` on shutdown.
"""
import asyncio
from typing import Optional

from playwright.async_api import async_playwright, Browser, Playwright

_playwright_ctx = None
_playwright: Optional[Playwright] = None
_browser: Optional[Browser] = None
_lock = asyncio.Lock()


async def ensure_browser(headless: bool = True):
    """
    Ensure the shared Playwright browser is started.

    This function is idempotent and safe to call multiple times.
    """
    global _playwright_ctx, _playwright, _browser
    async with _lock:
        if _browser is not None:
            return
        _playwright_ctx = async_playwright()
        _playwright = await _playwright_ctx.__aenter__()
        _browser = await _playwright.chromium.launch(headless=headless)


# Backwards-compatible alias for existing callers that imported the
# internal `_ensure_browser`.
_ensure_browser = ensure_browser


def ensure_browser_sync(headless: bool = True) -> None:
    """
    Synchronous wrapper to ensure the browser is started.

    If called from a running event loop, schedules the coroutine to run
    and returns immediately.
    """
    if _browser is not None:
        return
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(ensure_browser(headless=headless))
    except RuntimeError:
        asyncio.run(ensure_browser(headless=headless))
    except RuntimeError:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(ensure_browser(headless=headless))
            else:
                loop.run_until_complete(ensure_browser(headless=headless))
        except Exception:
            # If even this fails, let the caller handle/log the situation.
            raise


async def new_page():
    """Return a new `Page` instance from the shared browser.

    Caller is responsible for closing the page (`await page.close()`).
    """
    await _ensure_browser()
    return await _browser.new_page()


async def close_browser():
    """Close the shared browser and stop Playwright."""
    global _playwright_ctx, _playwright, _browser
    async with _lock:
        if _browser is not None:
            await _browser.close()
            _browser = None
        if _playwright_ctx is not None:
            await _playwright_ctx.__aexit__(None, None, None)
            _playwright_ctx = None
            _playwright = None
