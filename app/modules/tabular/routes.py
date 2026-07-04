from app.extensions.log import basic_logger
from robyn import Request, Response

from .services.tabular_service import TabularService


def init_routes(app):
    service = TabularService()

    @app.post("/app/tabular")
    async def generate_tabular_report(request: Request):
        """
        Endpoint para geração de relatório tabular em PDF.
        """
        try:
            # No Robyn, request.json() retorna o corpo processado
            payload = request.json()
            
            pdf_bytes = await service.execute(payload)
            
            return Response(
                status_code=200,
                headers={"Content-Type": "application/pdf"},
                description=pdf_bytes
            )
        except Exception as e:
            basic_logger.error(f"Erro na rota /app/tabular: {str(e)}")
            return Response(
                status_code=500,
                headers={"Content-Type": "application/json"},
                description='{"error": "Falha ao gerar relatório tabular"}'
            )