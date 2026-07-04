"""
Lightweight Playwright browser pool (singleton) for reuse across requests.

This module provides helpers to obtain a page instance without launching
Chromium on every request. Call `new_page()` to receive a fresh page and
`close_browser()` on shutdown.
"""
import asyncio

from playwright.async_api import Browser, Playwright, async_playwright

_playwright_ctx = None
_playwright: Playwright | None = None
_browser: Browser | None = None
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
        if loop.is_running():
            loop.create_task(ensure_browser(headless=headless))
        else:
            loop.run_until_complete(ensure_browser(headless=headless))
    except RuntimeError:
        asyncio.run(ensure_browser(headless=headless))


async def new_page():
    """Return a new `Page` instance from the shared browser.

    Caller is responsible for closing the page (`await page.close()`).
    """
    await _ensure_browser()
    return await _browser.new_page()


async def get_pdf_from_html(html: str, **kwargs) -> bytes:
    """
    Render HTML to PDF using the shared browser pool.

    Args:
        html: The HTML content to render.
        **kwargs: Additional arguments passed to ``page.pdf()``.

    Returns:
        The PDF bytes.
    """
    page = await new_page()
    try:
        await page.set_content(html)
        return await page.pdf(
            format=kwargs.get("format", "A4"),
            display_header_footer=kwargs.get("display_header_footer", True),
            header_template=kwargs.get("header_template", ""),
            footer_template=kwargs.get(
                "footer_template",
                '<div style="width:100%;text-align:center;font-size:10px;">'
                "Página <span class='pageNumber'></span> de <span class='totalPages'></span></div>",
            ),
            margin=kwargs.get("margin", {"top": ".2in", "bottom": ".5in", "left": ".2in", "right": ".2in"}),
        )
    finally:
        await page.close()


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
