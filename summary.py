"""Organization summary models."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class OrganizationSummary:
    """Collect results from a single organizer run."""

    root_directory: Path
    recursive: bool
    dry_run: bool
    moved_files: int = 0
    planned_files: int = 0
    failed_files: int = 0
    category_counts: dict[str, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def processed_files(self) -> int:
        """Return the total number of files handled during the run."""

        return self.moved_files + self.planned_files + self.failed_files

    @property
    def has_failures(self) -> bool:
        """Return whether any file operations failed."""

        return self.failed_files > 0

    def register_move(self, category: str, *, dry_run: bool) -> None:
        """Record a file move or a dry-run plan."""

        self.category_counts[category] = self.category_counts.get(category, 0) + 1
        if dry_run:
            self.planned_files += 1
        else:
            self.moved_files += 1

    def register_error(self, source_path: Path, message: str) -> None:
        """Record an error for a file that could not be processed."""

        self.failed_files += 1
        self.errors.append(f"{source_path}: {message}")
