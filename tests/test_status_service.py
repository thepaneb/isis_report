from unittest.mock import patch

from modules.status.services.status import StatusService

service = StatusService()


class TestProcessar:
    async def test_success(self):
        result = await service.processar()
        assert result["status"] == "healthy"
        assert result["uptime"] == 12345.67

    @patch("extensions.log.basic_logger")
    async def test_exception(self, mock_logger):
        original_processar = StatusService.processar

        async def broken_processar(self):
            try:
                raise RuntimeError("unexpected error")
            except Exception as e:
                from extensions.log import basic_logger
                basic_logger.error("Error processing status: %s", e)
                return {"status": "unhealthy", "error": str(e)}

        StatusService.processar = broken_processar
        try:
            result = await service.processar()
            assert result["status"] == "unhealthy"
            assert result["error"] == "unexpected error"
            mock_logger.error.assert_called_once()
        finally:
            StatusService.processar = original_processar
