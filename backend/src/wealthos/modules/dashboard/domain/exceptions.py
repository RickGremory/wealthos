"""Dashboard domain exceptions."""


class DashboardError(Exception):
    """Base dashboard error."""


class InvalidDateRange(DashboardError):
    """Raised when a date range is empty or inverted."""


class InvalidDashboardPeriod(DashboardError):
    """Raised when a dashboard period value is unsupported."""


class InvalidCashFlowGranularity(DashboardError):
    """Raised when cash-flow granularity is unsupported."""


class InvalidCategoryGrouping(DashboardError):
    """Raised when category grouping mode is unsupported."""


class CustomPeriodRequiresDates(DashboardError):
    """Raised when custom period lacks date_from/date_to."""
