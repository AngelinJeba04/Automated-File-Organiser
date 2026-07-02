"""File categorization helpers and default extension mappings."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping

from .exceptions import ConfigurationError

DEFAULT_CATEGORY_EXTENSIONS: dict[str, tuple[str, ...]] = {
    "Images": (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff", ".webp", ".heic", ".svg"),
    "Documents": (".doc", ".docx", ".rtf", ".txt", ".md", ".odt"),
    "Videos": (".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".webm", ".m4v"),
    "Audio": (".mp3", ".wav", ".aac", ".flac", ".ogg", ".wma", ".m4a"),
    "Archives": (".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tgz", ".tar.gz"),
    "Executables": (".exe", ".msi", ".bat", ".cmd", ".sh", ".ps1", ".app", ".deb", ".pkg"),
    "Code Files": (".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cc", ".cpp", ".h", ".hpp", ".cs", ".go", ".rb", ".php", ".html", ".css", ".json", ".yaml", ".yml", ".xml", ".sql", ".rs", ".swift", ".kt", ".kts", ".m", ".mm", ".dart"),
    "Spreadsheets": (".xls", ".xlsx", ".csv", ".ods", ".tsv"),
    "Presentations": (".ppt", ".pptx", ".odp"),
    "PDFs": (".pdf",),
}

DEFAULT_IGNORED_DIRECTORIES: tuple[str, ...] = (
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "node_modules",
)


def normalize_extension(extension: str) -> str:
    """Return a normalized file extension.

    Parameters
    ----------
    extension:
        A file extension with or without a leading dot.

    Returns
    -------
    str
        A lower-case extension prefixed with a single dot.

    Raises
    ------
    ConfigurationError
        If the provided extension is empty.
    """

    normalized = extension.strip().lower()
    if not normalized:
        raise ConfigurationError("Category extension values cannot be empty.")
    return normalized if normalized.startswith(".") else f".{normalized}"


def normalize_category_extensions(
    category_extensions: Mapping[str, Iterable[str]]
) -> dict[str, tuple[str, ...]]:
    """Validate and normalize a category-to-extension mapping.

    Parameters
    ----------
    category_extensions:
        Mapping of category names to iterables of extensions.

    Returns
    -------
    dict[str, tuple[str, ...]]
        Normalized category names and extensions.

    Raises
    ------
    ConfigurationError
        If the category names or extensions are invalid.
    """

    normalized: dict[str, tuple[str, ...]] = {}
    for category_name, extensions in category_extensions.items():
        cleaned_name = category_name.strip()
        if not cleaned_name:
            raise ConfigurationError("Category names cannot be empty.")
        if any(separator in cleaned_name for separator in ("/", "\\")) or cleaned_name in {".", ".."}:
            raise ConfigurationError(f"Unsafe category name: {category_name!r}.")

        cleaned_extensions = tuple(normalize_extension(extension) for extension in extensions)
        if not cleaned_extensions:
            raise ConfigurationError(f"Category {cleaned_name!r} must contain at least one extension.")

        normalized[cleaned_name] = cleaned_extensions

    return normalized


def build_extension_lookup(category_extensions: Mapping[str, Iterable[str]]) -> dict[str, str]:
    """Build a reverse lookup from extension to category.

    Parameters
    ----------
    category_extensions:
        Mapping of category names to extension collections.

    Returns
    -------
    dict[str, str]
        A mapping from normalized extension to category name.
    """

    extension_lookup: dict[str, str] = {}
    normalized_categories = normalize_category_extensions(category_extensions)
    for category_name, extensions in normalized_categories.items():
        for extension in extensions:
            extension_lookup[extension] = category_name
    return extension_lookup


def categorize_file(file_path: Path, extension_lookup: Mapping[str, str]) -> str:
    """Determine the category for a file based on its suffix.

    Parameters
    ----------
    file_path:
        The file to categorize.
    extension_lookup:
        Reverse mapping of extension to category name.

    Returns
    -------
    str
        The matching category name or ``Others`` when no match exists.
    """

    suffixes = file_path.suffixes
    if suffixes:
        for start_index in range(0, len(suffixes)):
            candidate = "".join(suffixes[start_index:]).lower()
            matched_category = extension_lookup.get(candidate)
            if matched_category:
                return matched_category

    last_suffix = file_path.suffix.lower()
    if last_suffix:
        matched_category = extension_lookup.get(last_suffix)
        if matched_category:
            return matched_category

    return "Others"