"""Custom exceptions for the automated file organizer."""


class OrganizerError(Exception):
    """Base exception for organizer failures."""


class ConfigurationError(OrganizerError):
    """Raised when configuration cannot be loaded or validated."""


class InvalidDirectoryError(OrganizerError):
    """Raised when the selected directory is invalid."""


class FileOperationError(OrganizerError):
    """Raised when a file operation cannot be completed."""