"""Tests for BaseReportService pipeline."""
from unittest.mock import patch

import pytest

from modules.base_service import BaseReportService


class ConcreteService(BaseReportService):
    """Concrete implementation of BaseReportService for testing."""
    async def _obter_dados(self, payload):
        return payload.get("data", [])

    async def _tratar_dados(self, data, payload):
        return {"data": data, "meta": payload.get("meta", {})}

    async def _gerar_html(self, data, payload):
        return "<html>OK</html>"

    async def _gerar_pdf(self, html):
        return b"%PDF-1.4"


class TestExecute:
    """Tests for the execute pipeline method."""
    def setup_method(self):
        """Create a fresh service instance for each test."""
        self.service = ConcreteService()

    @patch("modules.base_service.basic_logger")
    async def test_success_path(self, mock_logger):
        """Verify the full pipeline succeeds and returns PDF bytes."""
        result = await self.service.execute({"data": [1, 2], "meta": {"title": "T"}})
        assert result == b"%PDF-1.4"
        assert mock_logger.info.call_count == 2

    @patch("modules.base_service.basic_logger")
    async def test_error_path(self, mock_logger):
        """Verify errors in the pipeline are logged and re-raised."""
        class FailingService(ConcreteService):
            """Failing implementation for error path testing."""

            async def _obter_dados(self, payload):
                raise RuntimeError("fail")

        svc = FailingService()
        with pytest.raises(RuntimeError, match="fail"):
            await svc.execute({"data": []})
        mock_logger.error.assert_called_once()


class TestAbstractMethods:
    """Tests for abstract method enforcement."""
    def test_cannot_instantiate_abstract(self):
        """Verify BaseReportService cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseReportService()
