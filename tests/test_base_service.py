from unittest.mock import patch

import pytest

from modules.base_service import BaseReportService


class ConcreteService(BaseReportService):
    async def _obter_dados(self, payload):
        return payload.get("data", [])

    async def _tratar_dados(self, data, payload):
        return {"data": data, "meta": payload.get("meta", {})}

    async def _gerar_html(self, data, payload):
        return "<html>OK</html>"

    async def _gerar_pdf(self, html):
        return b"%PDF-1.4"


class TestExecute:
    def setup_method(self):
        self.service = ConcreteService()

    @patch("modules.base_service.basic_logger")
    async def test_success_path(self, mock_logger):
        result = await self.service.execute({"data": [1, 2], "meta": {"title": "T"}})
        assert result == b"%PDF-1.4"
        assert mock_logger.info.call_count == 2

    @patch("modules.base_service.basic_logger")
    async def test_error_path(self, mock_logger):
        class FailingService(ConcreteService):
            async def _obter_dados(self, payload):
                raise RuntimeError("fail")

        svc = FailingService()
        with pytest.raises(RuntimeError, match="fail"):
            await svc.execute({"data": []})
        mock_logger.error.assert_called_once()


class TestAbstractMethods:
    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            BaseReportService()
