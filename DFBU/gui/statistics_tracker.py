"""
DFBU StatisticsTracker - Operation Statistics Component

Description:
    Tracks statistics for backup and restore operations including counts,
    processing times, and success rates. Part of the refactored MVVM
    architecture following Single Responsibility Principle.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-01-2025
Date Changed: 11-01-2025
License: MIT

Features:
    - Item processing statistics (processed, skipped, failed)
    - Processing time tracking (individual, average, min, max)
    - Statistics reset for new operations
    - Clean separation from business logic

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - Standard library: dataclasses only

Classes:
    - BackupStatistics: Dataclass for operation statistics
    - StatisticsTracker: Manages statistics tracking

Functions:
    None
"""

from dataclasses import dataclass, field


@dataclass
class BackupStatistics:
    """
    Data class for tracking backup operation statistics.

    Attributes:
        total_items: Total number of items to process
        processed_items: Number of successfully processed items
        skipped_items: Number of items skipped (not exist or no permission)
        failed_items: Number of items that failed processing
        total_time: Total elapsed time for operation
        processing_times: Individual processing times for each item
        average_time: Average processing time per item
        min_time: Minimum processing time
        max_time: Maximum processing time
    """

    total_items: int = 0
    processed_items: int = 0
    skipped_items: int = 0
    failed_items: int = 0
    total_time: float = 0.0
    processing_times: list[float] = field(default_factory=list)

    @property
    def average_time(self) -> float:
        """Calculate average processing time per item."""
        if not self.processing_times:
            return 0.0
        return sum(self.processing_times) / len(self.processing_times)

    @property
    def min_time(self) -> float:
        """Get minimum processing time."""
        return min(self.processing_times) if self.processing_times else 0.0

    @property
    def max_time(self) -> float:
        """Get maximum processing time."""
        return max(self.processing_times) if self.processing_times else 0.0

    def reset(self) -> None:
        """Reset statistics to initial state."""
        self.total_items = 0
        self.processed_items = 0
        self.skipped_items = 0
        self.failed_items = 0
        self.total_time = 0.0
        self.processing_times = []


class StatisticsTracker:
    """
    Manages operation statistics tracking.

    Provides simple interface for recording operation results and retrieving
    statistics. Handles statistics storage and calculation.

    Attributes:
        statistics: BackupStatistics instance holding current stats

    Public methods:
        record_item_processed: Record successfully processed item
        record_item_skipped: Record skipped item
        record_item_failed: Record failed item
        reset_statistics: Reset statistics for new operation
        get_statistics: Get current statistics

    Private methods:
        None
    """

    def __init__(self) -> None:
        """Initialize StatisticsTracker with empty statistics."""
        self.statistics = BackupStatistics()

    def record_item_processed(self, processing_time: float) -> None:
        """
        Record successfully processed item.

        Args:
            processing_time: Time taken to process item in seconds
        """
        self.statistics.processed_items += 1
        self.statistics.processing_times.append(processing_time)

    def record_item_skipped(self) -> None:
        """Record skipped item (not exist or no permission)."""
        self.statistics.skipped_items += 1

    def record_item_failed(self) -> None:
        """Record failed item."""
        self.statistics.failed_items += 1

    def reset_statistics(self) -> None:
        """Reset operation statistics for new run."""
        self.statistics.reset()

    def get_statistics(self) -> BackupStatistics:
        """
        Get current operation statistics.

        Returns:
            Current BackupStatistics instance
        """
        return self.statistics
