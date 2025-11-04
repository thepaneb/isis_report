"""
Hello world module routes."""
from modules.hello_world.router import router


@router.get("", openapi_name="Hello world", openapi_tags=["hello_world"])
async def get_root():
    """
    Returns "Hello, world!" string.
    """
    return "Hello, world!"
