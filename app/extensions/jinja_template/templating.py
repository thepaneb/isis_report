"""
Jinja2 templating interface and implementation.
"""

from abc import ABC, abstractmethod

from jinja2 import Environment, FileSystemLoader


class TemplateInterface(ABC):  # pylint: disable=too-few-public-methods
    """
    Abstract base class for template rendering.
    """

    @abstractmethod
    def __init__(self): ...

    @abstractmethod
    async def render_template(self, *args, **kwargs) -> str: ...  # pylint: disable=missing-function-docstring


class JinjaTemplate(TemplateInterface):  # pylint: disable=too-few-public-methods
    """
    Jinja2 template rendering implementation.
    """

    def __init__(self, directory, encoding="utf-8", followlinks=False):
        """
        Initialize the Jinja2 environment.
        """
        super().__init__()

        self.env = Environment(loader=FileSystemLoader(searchpath=directory, encoding=encoding, followlinks=followlinks))

    async def render_template(self, *args, **kwargs) -> str:
        """
        Render a template with the given name and context.
        """
        return self.env.get_template(args[0]).render(**kwargs)
