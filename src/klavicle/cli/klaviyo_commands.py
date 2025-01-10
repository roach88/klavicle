import asyncio
import json
import os
from typing import Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from ..klaviyo.client import KlaviyoClient
from ..validation.handlers import (
    ValidationError,
    validate_list_data,
    validate_profile_data,
    validate_segment_data,
)

# Load environment variables from .env file
load_dotenv()

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


async def get_lists_impl(
    sort_by: str = "updated",
    order: str = "desc",
    created_after: Optional[int] = None,
    updated_after: Optional[int] = None,
) -> None:
    """Implementation of get lists command."""
    client = get_klaviyo_client()

    try:
        all_lists = []
        next_page = None

        # Calculate date filters if provided
        from datetime import datetime, timedelta

        filters = []

        if created_after:
            created_date = (datetime.utcnow() - timedelta(days=created_after)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            filters.append(f"greater-than(created,{created_date})")

        if updated_after:
            updated_date = (datetime.utcnow() - timedelta(days=updated_after)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            filters.append(f"greater-than(updated,{updated_date})")

        filter_string = None
        if filters:
            filter_string = (
                "and(" + ",".join(filters) + ")" if len(filters) > 1 else filters[0]
            )

        with console.status("[bold green]Fetching lists...") as status:
            while True:
                response = await client.get_lists(
                    page_cursor=next_page, filter_string=filter_string
                )

                if not response or "data" not in response:
                    break

                all_lists.extend(response["data"])

                # Check if there are more pages
                if (
                    "links" in response
                    and "next" in response["links"]
                    and response["links"]["next"]
                ):
                    next_page = response["links"]["next"]
                    status.update(
                        f"[bold green]Fetching more lists... ({len(all_lists)} found so far)"
                    )
                else:
                    break

        if not all_lists:
            console.print("[yellow]No lists found.[/yellow]")
            return

        # Sort lists by specified field and order
        reverse = order == "desc"
        all_lists.sort(
            key=lambda x: x.get("attributes", {}).get(sort_by, ""), reverse=reverse
        )

        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Created")
        table.add_column("Updated")

        # Add rows
        for list_item in all_lists:
            attributes = list_item.get("attributes", {})
            table.add_row(
                str(list_item.get("id", "")),
                str(attributes.get("name", "")),
                str(attributes.get("created", "")),
                str(attributes.get("updated", "")),
            )

        console.print(f"\nTotal lists: {len(all_lists)}")
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


async def get_segments_impl(
    sort_by: str = "updated",
    order: str = "desc",
    created_after: Optional[int] = None,
    updated_after: Optional[int] = None,
) -> None:
    """Implementation of get segments command."""
    client = get_klaviyo_client()

    try:
        all_segments = []
        next_page = None

        # Calculate date filters if provided
        from datetime import datetime, timedelta

        filters = []

        if created_after:
            created_date = (datetime.utcnow() - timedelta(days=created_after)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            filters.append(f"greater-than(created,{created_date})")

        if updated_after:
            updated_date = (datetime.utcnow() - timedelta(days=updated_after)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            filters.append(f"greater-than(updated,{updated_date})")

        filter_string = None
        if filters:
            filter_string = (
                "and(" + ",".join(filters) + ")" if len(filters) > 1 else filters[0]
            )

        with console.status("[bold green]Fetching segments...") as status:
            while True:
                response = await client.get_segments(
                    page_cursor=next_page, filter_string=filter_string
                )

                if not response or "data" not in response:
                    break

                all_segments.extend(response["data"])

                # Check if there are more pages
                if (
                    "links" in response
                    and "next" in response["links"]
                    and response["links"]["next"]
                ):
                    next_page = response["links"]["next"]
                    status.update(
                        f"[bold green]Fetching more segments... ({len(all_segments)} found so far)"
                    )
                else:
                    break

        if not all_segments:
            console.print("[yellow]No segments found.[/yellow]")
            return

        # Sort segments by specified field and order
        reverse = order == "desc"
        all_segments.sort(
            key=lambda x: x.get("attributes", {}).get(sort_by, ""), reverse=reverse
        )

        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Created")
        table.add_column("Updated")

        # Add rows
        for segment in all_segments:
            attributes = segment.get("attributes", {})
            table.add_row(
                str(segment.get("id", "")),
                str(attributes.get("name", "")),
                str(attributes.get("created", "")),
                str(attributes.get("updated", "")),
            )

        console.print(f"\nTotal segments: {len(all_segments)}")
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


async def get_tags_impl(
    sort_by: str = "updated",
    order: str = "desc",
    created_after: Optional[int] = None,
    updated_after: Optional[int] = None,
) -> None:
    """Implementation of get tags command."""
    client = get_klaviyo_client()

    try:
        all_tags = []
        next_page = None

        # Calculate date filters if provided
        from datetime import datetime, timedelta

        filters = []

        if created_after:
            created_date = (datetime.utcnow() - timedelta(days=created_after)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            filters.append(f"greater-than(created,{created_date})")

        if updated_after:
            updated_date = (datetime.utcnow() - timedelta(days=updated_after)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
            filters.append(f"greater-than(updated,{updated_date})")

        filter_string = None
        if filters:
            filter_string = (
                "and(" + ",".join(filters) + ")" if len(filters) > 1 else filters[0]
            )

        with console.status("[bold green]Fetching tags...") as status:
            while True:
                response = await client.get_tags(
                    page_cursor=next_page, filter_string=filter_string
                )

                if not response or "data" not in response:
                    break

                all_tags.extend(response["data"])

                # Check if there are more pages
                if (
                    "links" in response
                    and "next" in response["links"]
                    and response["links"]["next"]
                ):
                    next_page = response["links"]["next"]
                    status.update(
                        f"[bold green]Fetching more tags... ({len(all_tags)} found so far)"
                    )
                else:
                    break

        if not all_tags:
            console.print("[yellow]No tags found.[/yellow]")
            return

        # Sort tags by specified field and order
        reverse = order == "desc"
        all_tags.sort(
            key=lambda x: x.get("attributes", {}).get(sort_by, ""), reverse=reverse
        )

        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID")
        table.add_column("Name")
        table.add_column("Created")
        table.add_column("Updated")

        # Add rows
        for tag in all_tags:
            attributes = tag.get("attributes", {})
            table.add_row(
                str(tag.get("id", "")),
                str(attributes.get("name", "")),
                str(attributes.get("created", "")),
                str(attributes.get("updated", "")),
            )

        console.print(f"\nTotal tags: {len(all_tags)}")
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
