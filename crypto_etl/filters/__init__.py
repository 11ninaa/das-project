"""
Filters Package - Pipe and Filter Architecture

This package implements the three filters of the pipe-and-filter architecture
Each filter is independent and transforms data, passing it to the next filter.
"""

from .filters import filter1, filter2, filter3

__all__ = ["filter1", "filter2", "filter3"]

