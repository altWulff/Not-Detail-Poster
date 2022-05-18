"""
This module contains custom exceptions to admin panel
"""
import statistics


class UserRoleException(Exception):
    """User role exception"""

    def __str__(self):
        return "User role exception"


class QueryException(statistics.StatisticsError):
    """Query exception"""

    def __str__(self):
        return "Query exception"


class FailedUpdateException(Exception):
    """Failed update exception"""

    def __str__(self):
        return "Failed to update db exception"
