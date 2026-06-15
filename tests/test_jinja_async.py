import asyncio
from pathlib import Path

from app.extensions.jinja_template.templating import JinjaTemplate


def test_jinja_async_render(tmp_path: Path):
    # create a minimal template
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    tpl = templates_dir / "test.j2"
    tpl.write_text("Hello {{ name }}")

    async def run_render():
        renderer = JinjaTemplate(str(templates_dir))
        result = await renderer.render_template("test.j2", name="World")
        return result

    out = asyncio.run(run_render())
    assert "Hello World" in out
