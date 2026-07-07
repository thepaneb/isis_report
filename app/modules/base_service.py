from abc import ABC, abstractmethod
from typing import Any, final

from extensions.log import basic_logger


class BaseReportService(ABC):
    """
    Classe base que define o ciclo de vida de geração de relatórios.
    Seguindo o padrão: Obter -> Tratar -> Renderizar HTML -> Gerar PDF.
    """

    @final
    async def execute(self, payload: dict[str, Any]) -> bytes:
        """
        Executa o pipeline completo de geração de relatório.
        Este método é final e garante a ordem correta das operações.
        """
        service_name = self.__class__.__name__
        try:
            basic_logger.info(f"Iniciando processamento do relatório: {service_name}")

            # 1. Recuperação
            raw_data = await self._obter_dados(payload)

            # 2. Transformação (Lógica de Negócio)
            processed_data = await self._tratar_dados(raw_data, payload)

            # 3. Renderização
            html_content = await self._gerar_html(processed_data, payload)

            # 4. Conversão
            pdf_bytes = await self._gerar_pdf(html_content)

            basic_logger.info(f"Relatório {service_name} gerado com sucesso.")
            return pdf_bytes
        except Exception as e:
            basic_logger.error(f"Falha no pipeline do serviço {service_name}: {str(e)}", exc_info=True)
            raise

    @abstractmethod
    async def _obter_dados(self, payload: dict[str, Any]) -> Any:
        """Recupera dados da fonte (Mock ou DB)"""

    @abstractmethod
    async def _tratar_dados(self, data: Any, payload: dict[str, Any]) -> Any:
        """Aplica lógica de agrupamento e agregação"""

    @abstractmethod
    async def _gerar_html(self, data: Any, payload: dict[str, Any]) -> str:
        """Renderiza o template Jinja2 de forma assíncrona"""

    @abstractmethod
    async def _gerar_pdf(self, html: str) -> bytes:
        """Converte HTML para PDF usando o pool do Playwright"""
