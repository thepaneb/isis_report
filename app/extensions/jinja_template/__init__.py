"""
Jinja2 template extension.
"""

import os
import pathlib
from typing import Any

from extensions.jinja_template.templating import JinjaTemplate

current_file_path = pathlib.Path(__file__).parent.parent.parent.resolve()
jinja_template = JinjaTemplate(os.path.join(current_file_path, "templates"))


async def render_template(template_name: str, **context: Any) -> str:
    """
    Render a Jinja2 template with the given data.
    """
    return await jinja_template.render_template(template_name, **context)
