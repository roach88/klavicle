"""CLI commands for managing configuration."""

import json
from typing import Any

from rich.console import Console
from rich.table import Table

from ..config import get_config

console = Console()


def get_config_impl() -> None:
    """Implementation of get-config command."""
    config = get_config()

    # Get the full configuration
    data = config.get()

    # Create a pretty table with configuration entries
    table = Table(title="Klavicle Configuration")
    table.add_column("Section")
    table.add_column("Key")
    table.add_column("Value")

    # Add rows for AI configuration
    ai_config = data.get("ai", {})

    # Default provider
    default_provider = ai_config.get("default_provider", "mock")
    table.add_row("AI", "Default Provider", default_provider)

    # Provider-specific configuration
    providers = ai_config.get("providers", {})
    for provider_name, provider_config in providers.items():
        for key, value in provider_config.items():
            if key == "api_key" and value:
                # Mask API keys
                value = "*" * 8 + value[-4:] if len(value) > 4 else "*" * len(value)
            table.add_row("AI", f"{provider_name}.{key}", str(value))

    # Output configuration
    output_config = ai_config.get("output", {})
    for key, value in output_config.items():
        table.add_row("Output", key, str(value))

    console.print(table)


def set_config_impl(key: str, value: Any) -> None:
    """Implementation of set-config command."""
    config = get_config()

    try:
        # Handle special case for boolean values
        if value.lower() in ["true", "yes", "1"]:
            value = True
        elif value.lower() in ["false", "no", "0"]:
            value = False
        # Handle numbers
        elif value.isdigit():
            value = int(value)
        elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
            value = float(value)

        # Set the configuration value
        config.set(key, value)
        console.print(f"[green]Configuration updated:[/green] {key} = {value}")
    except Exception as e:
        console.print(f"[red]Error setting configuration:[/red] {str(e)}")


def unset_config_impl(key: str) -> None:
    """Implementation of unset-config command."""
    config = get_config()

    try:
        # Unset the configuration value
        config.unset(key)
        console.print(f"[green]Configuration value removed:[/green] {key}")
    except Exception as e:
        console.print(f"[red]Error removing configuration:[/red] {str(e)}")


def set_api_key_impl(provider: str, api_key: str) -> None:
    """Implementation of set-api-key command."""
    config = get_config()

    try:
        # Set the API key for the specified provider
        config_key = f"ai.providers.{provider}.api_key"
        config.set(config_key, api_key)

        # Mask API key in output
        masked_key = "*" * 8 + api_key[-4:] if len(api_key) > 4 else "*" * len(api_key)
        console.print(f"[green]API key set for {provider}:[/green] {masked_key}")
    except Exception as e:
        console.print(f"[red]Error setting API key:[/red] {str(e)}")


def set_default_provider_impl(provider: str) -> None:
    """Implementation of set-default-provider command."""
    config = get_config()

    try:
        # Set the default AI provider
        config.set("ai.default_provider", provider)
        console.print(f"[green]Default AI provider set to:[/green] {provider}")
    except Exception as e:
        console.print(f"[red]Error setting default provider:[/red] {str(e)}")


def export_config_impl(file_path: str) -> None:
    """Implementation of export-config command."""
    config = get_config()

    try:
        # Get the full configuration
        data = config.get()

        # Write to the specified file
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

        console.print(f"[green]Configuration exported to:[/green] {file_path}")
    except Exception as e:
        console.print(f"[red]Error exporting configuration:[/red] {str(e)}")


def import_config_impl(file_path: str) -> None:
    """Implementation of import-config command."""
    config = get_config()

    try:
        # Read from the specified file
        with open(file_path, "r") as f:
            data = json.load(f)

        # Set each configuration value
        for section, section_data in data.items():
            if isinstance(section_data, dict):
                for key, value in _flatten_dict(section_data, prefix=section):
                    config.set(key, value)
            else:
                config.set(section, section_data)

        console.print(f"[green]Configuration imported from:[/green] {file_path}")
    except Exception as e:
        console.print(f"[red]Error importing configuration:[/red] {str(e)}")


def _flatten_dict(d: dict, prefix: str = "") -> list:
    """
    Flatten a nested dictionary into a list of (key, value) tuples.

    Args:
        d: Dictionary to flatten
        prefix: Prefix for keys (for nested dictionaries)

    Returns:
        List of (key, value) tuples with dot-notation keys
    """
    items = []
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, key))
        else:
            items.append((key, v))
    return items
