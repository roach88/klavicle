import asyncio
import json
import os
from typing import Optional

from rich.console import Console
from rich.table import Table

from ..klaviyo.client import KlaviyoClient
from ..validation.handlers import (
    ValidationError,
    validate_list_data,
    validate_profile_data,
    validate_segment_data,
)

console = Console()


def get_klaviyo_client() -> KlaviyoClient:
    """Create and return a KlaviyoClient instance."""
    api_key = os.getenv("KLAVIYO_API_KEY")
    if not api_key:
        raise ValueError("KLAVIYO_API_KEY environment variable is not set")
    return KlaviyoClient(api_key=api_key)


async def get_profile_impl(profile_id: str) -> None:
    """Implementation of get profile command."""
    client = get_klaviyo_client()

    try:
        with console.status("[bold green]Fetching profile..."):
            profile = await client.get_profile(profile_id)

        if not profile:
            console.print("[yellow]Profile not found.[/yellow]")
            return

        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Field")
        table.add_column("Value")

        # Add rows
        for key, value in profile.items():
            table.add_row(str(key), str(value))

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


async def create_profile_impl(data: str) -> None:
    """Implementation of create profile command."""
    client = get_klaviyo_client()

    try:
        # Parse and validate profile data
        profile_data = json.loads(data)
        validate_profile_data(profile_data)

        # Create profile
        with console.status("[bold green]Creating profile..."):
            profile = await client.create_profile(profile_data)

        console.print(
            f"[green]Profile created successfully. ID: {profile.get('id')}[/green]"
        )

    except json.JSONDecodeError:
        console.print("[red]Error:[/red] Invalid JSON data")
    except ValidationError as e:
        console.print(f"[red]Validation error:[/red] {str(e)}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


async def update_profile_impl(profile_id: str, data: str) -> None:
    """Implementation of update profile command."""
    client = get_klaviyo_client()

    try:
        # Parse and validate profile data
        profile_data = json.loads(data)
        validate_profile_data(profile_data)

        # Update profile
        with console.status("[bold green]Updating profile..."):
            await client.update_profile(profile_id, profile_data)

        console.print(f"[green]Profile {profile_id} updated successfully.[/green]")

    except json.JSONDecodeError:
        console.print("[red]Error:[/red] Invalid JSON data")
    except ValidationError as e:
        console.print(f"[red]Validation error:[/red] {str(e)}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


async def get_lists_impl() -> None:
    """Implementation of get lists command."""
    client = get_klaviyo_client()

    try:
        with console.status("[bold green]Fetching lists..."):
            lists = await client.get_lists()

        if not lists:
            console.print("[yellow]No lists found.[/yellow]")
            return

        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Created")
        table.add_column("Updated")

        # Add rows
        for list_item in lists:
            table.add_row(
                str(list_item.get("id", "")),
                str(list_item.get("name", "")),
                str(list_item.get("created", "")),
                str(list_item.get("updated", "")),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


async def create_list_impl(name: str, description: Optional[str] = None) -> None:
    """Implementation of create list command."""
    client = get_klaviyo_client()

    try:
        # Validate list data
        list_data = {"name": name}
        if description:
            list_data["description"] = description
        validate_list_data(list_data)

        # Create list
        with console.status("[bold green]Creating list..."):
            list_item = await client.create_list(name, description)

        console.print(
            f"[green]List created successfully. ID: {list_item.get('id')}[/green]"
        )

    except ValidationError as e:
        console.print(f"[red]Validation error:[/red] {str(e)}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


async def get_segments_impl() -> None:
    """Implementation of get segments command."""
    client = get_klaviyo_client()

    try:
        with console.status("[bold green]Fetching segments..."):
            segments = await client.get_segments()

        if not segments:
            console.print("[yellow]No segments found.[/yellow]")
            return

        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Created")
        table.add_column("Updated")

        # Add rows
        for segment in segments:
            table.add_row(
                str(segment.get("id", "")),
                str(segment.get("name", "")),
                str(segment.get("created", "")),
                str(segment.get("updated", "")),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


async def create_segment_impl(name: str, conditions: str) -> None:
    """Implementation of create segment command."""
    client = get_klaviyo_client()

    try:
        # Parse and validate segment data
        segment_data = {"name": name, "conditions": json.loads(conditions)}
        validate_segment_data(segment_data)

        # Create segment
        with console.status("[bold green]Creating segment..."):
            segment = await client.create_segment(
                name, definition=json.loads(conditions)
            )

        console.print(
            f"[green]Segment created successfully. ID: {segment.get('id')}[/green]"
        )

    except json.JSONDecodeError:
        console.print("[red]Error:[/red] Invalid JSON conditions")
    except ValidationError as e:
        console.print(f"[red]Validation error:[/red] {str(e)}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


async def get_tags_impl() -> None:
    """Implementation of get tags command."""
    client = get_klaviyo_client()

    try:
        with console.status("[bold green]Fetching tags..."):
            tags = await client.get_tags()

        if not tags:
            console.print("[yellow]No tags found.[/yellow]")
            return

        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Created")
        table.add_column("Updated")

        # Add rows
        for tag in tags:
            table.add_row(
                str(tag.get("id", "")),
                str(tag.get("name", "")),
                str(tag.get("created", "")),
                str(tag.get("updated", "")),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


async def add_tags_impl(resource_type: str, resource_id: str, tags: list) -> None:
    """Implementation of add tags command."""
    client = get_klaviyo_client()

    try:
        # Add tags
        with console.status("[bold green]Adding tags..."):
            await client.add_tags(resource_type, resource_id, tags)

        console.print(
            f"[green]Tags added successfully to {resource_type} {resource_id}.[/green]"
        )

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


async def remove_tags_impl(resource_type: str, resource_id: str, tags: list) -> None:
    """Implementation of remove tags command."""
    client = get_klaviyo_client()

    try:
        # Remove tags
        with console.status("[bold green]Removing tags..."):
            await client.remove_tags(resource_type, resource_id, tags)

        console.print(
            f"[green]Tags removed successfully from {resource_type} {resource_id}.[/green]"
        )

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


def run_async(coro):
    """Helper function to run async functions."""
    return asyncio.run(coro)
