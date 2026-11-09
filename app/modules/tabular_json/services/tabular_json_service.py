"""Tabular JSON report service (delegates to isis-report-lib)."""

from isis_report_lib.service import TabularReportService


class TabularJsonService(TabularReportService):
    """JSON payloads use the library's default tabular pipeline."""
