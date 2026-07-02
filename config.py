"""Configuration loading for the automated file organizer."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from .categories import DEFAULT_CATEGORY_EXTENSIONS, DEFAULT_IGNORED_DIRECTORIES, normalize_category_extensions, normalize_extension
from .exceptions import ConfigurationError


@dataclass(slots=True)
class OrganizerConfig:
    """Runtime configuration for an organization run."""

    category_extensions: dict[str, tuple[str, ...]]
    ignored_directories: tuple[str, ...]


def default_config() -> OrganizerConfig:
    """Return the built-in organizer configuration."""

    return OrganizerConfig(
        category_extensions=dict(DEFAULT_CATEGORY_EXTENSIONS),
        ignored_directories=DEFAULT_IGNORED_DIRECTORIES,
    )


def _validate_ignored_directories(values: Iterable[Any]) -> tuple[str, ...]:
    cleaned_values: list[str] = []
    for value in values:
        if not isinstance(value, str):
            raise ConfigurationError("Ignored directory names must be strings.")
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ConfigurationError("Ignored directory names cannot be empty.")
        if any(separator in cleaned_value for separator in ("/", "\\")) or cleaned_value in {".", ".."}:
            raise ConfigurationError(f"Unsafe ignored directory name: {value!r}.")
        cleaned_values.append(cleaned_value)
    return tuple(dict.fromkeys(cleaned_values))


def _merge_category_extensions(
    base_categories: Mapping[str, Iterable[str]],
    override_categories: Mapping[str, Any] | None,
) -> dict[str, tuple[str, ...]]:
    categories = dict(base_categories)
    if override_categories is None:
        return normalize_category_extensions(categories)

    if not isinstance(override_categories, Mapping):
        raise ConfigurationError("The 'categories' entry must be a mapping of names to extension lists.")

    for category_name, extension_values in override_categories.items():
        if not isinstance(extension_values, Iterable) or isinstance(extension_values, (str, bytes)):
            raise ConfigurationError(f"Category {category_name!r} must map to a list of extensions.")
        categories[str(category_name)] = tuple(normalize_extension(str(extension)) for extension in extension_values)

    return normalize_category_extensions(categories)


def load_config(config_path: Path | None) -> OrganizerConfig:
    """Load a configuration file when one is provided.

    Parameters
    ----------
    config_path:
        Optional path to a JSON configuration file.

    Returns
    -------
    OrganizerConfig
        The merged configuration to use for the run.

    Raises
    ------
    ConfigurationError
        If the configuration file is missing or invalid.
    """

    if config_path is None:
        return default_config()

    if not config_path.exists() or not config_path.is_file():
        raise ConfigurationError(f"Configuration file not found: {config_path}")

    try:
        raw_data = json.loads(config_path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise ConfigurationError(f"Configuration file is not valid UTF-8: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"Configuration file is not valid JSON: {config_path}") from exc

    if not isinstance(raw_data, dict):
        raise ConfigurationError("Configuration file must contain a JSON object at the top level.")

    categories = _merge_category_extensions(DEFAULT_CATEGORY_EXTENSIONS, raw_data.get("categories"))

    ignored_directories_raw = raw_data.get("ignored_directories")
    if ignored_directories_raw is None:
        ignored_directories = DEFAULT_IGNORED_DIRECTORIES
    else:
        if not isinstance(ignored_directories_raw, Iterable) or isinstance(ignored_directories_raw, (str, bytes)):
            raise ConfigurationError("The 'ignored_directories' entry must be a list of directory names.")
        ignored_directories = tuple(dict.fromkeys(DEFAULT_IGNORED_DIRECTORIES + _validate_ignored_directories(ignored_directories_raw)))

    return OrganizerConfig(category_extensions=categories, ignored_directories=ignored_directories)