"""Tabular .toon report service (delegates to isis-report-lib)."""

from isis_report_lib.service import TabularReportService


class TabularToonService(TabularReportService):
    """.toon text is parsed first; generation uses the library's tabular pipeline."""
