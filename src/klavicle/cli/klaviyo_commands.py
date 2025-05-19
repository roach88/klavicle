import asyncio
import csv
import json
import os
from datetime import datetime, timezone
from typing import Optional, cast

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from ..ai.analyzer import ProviderType
from ..klaviyo.campaign_analyzer import CampaignAnalyzer
from ..klaviyo.client import KlaviyoClient
from ..klaviyo.flow_analyzer import FlowAnalyzer
from ..klaviyo.list_analyzer import ListAnalyzer
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


async def analyze_tags_impl(export_format: Optional[str] = None) -> None:
    """Implementation of analyze tags command."""
    client = get_klaviyo_client()

    try:
        with console.status("[bold green]Analyzing tags..."):
            analysis = await client.analyze_tag_usage()

        # Print summary
        console.print("\n[bold blue]Tag Analysis Summary[/bold blue]")
        console.print(f"Total tags: {analysis['summary']['total_tags']}")
        console.print(f"Active tags: {analysis['summary']['active_tags']}")
        console.print(f"Unused tags: {analysis['summary']['unused_tags']}")
        console.print(
            f"Total relationships: {analysis['summary']['total_relationships']}"
        )

        # Print age distribution
        console.print("\n[bold blue]Tag Age Distribution[/bold blue]")
        age_table = Table(show_header=True, header_style="bold magenta")
        age_table.add_column("Time Period")
        age_table.add_column("Count")
        age_table.add_column("Tags")

        for period, tags in analysis["age_groups"].items():
            age_table.add_row(
                period.replace("_", " ").title(),
                str(len(tags)),
                ", ".join(
                    sorted(tags)[:5] + ["..."] if len(tags) > 5 else sorted(tags)
                ),
            )
        console.print(age_table)

        # Print usage statistics
        console.print("\n[bold blue]Usage Statistics[/bold blue]")
        stats_table = Table(show_header=True, header_style="bold magenta")
        stats_table.add_column("Metric")
        stats_table.add_column("Count")

        detailed_stats = analysis["detailed_stats"]
        stats_table.add_row(
            "Total List Relationships", str(detailed_stats["total_list_relationships"])
        )
        stats_table.add_row(
            "Total Segment Relationships",
            str(detailed_stats["total_segment_relationships"]),
        )
        stats_table.add_row(
            "Total Flow Relationships", str(detailed_stats["total_flow_relationships"])
        )

        console.print(stats_table)

        # Print usage distribution
        console.print("\n[bold blue]Tag Usage Distribution[/bold blue]")
        usage_table = Table(show_header=True, header_style="bold magenta")
        usage_table.add_column("Usage Count")
        usage_table.add_column("Number of Tags")

        for usage_range, count in sorted(detailed_stats["tags_by_usage_count"].items()):
            usage_table.add_row(usage_range, str(count))
        console.print(usage_table)

        # Print most used tags
        if detailed_stats["most_used_tags"]:
            console.print("\n[bold blue]Top 10 Most Used Tags[/bold blue]")
            top_table = Table(show_header=True, header_style="bold magenta")
            top_table.add_column("Tag Name")
            top_table.add_column("Total Usage")
            top_table.add_column("Lists")
            top_table.add_column("Segments")
            top_table.add_column("Flows")

            for tag in detailed_stats["most_used_tags"]:
                top_table.add_row(
                    tag["name"],
                    str(tag["total_usage"]),
                    str(tag["list_count"]),
                    str(tag["segment_count"]),
                    str(tag["flow_count"]),
                )
            console.print(top_table)

        # Create table for unused tags
        if analysis["unused_tags"]:
            console.print(
                "\n[bold yellow]Unused Tags (Candidates for Cleanup)[/bold yellow]"
            )
            unused_table = Table(show_header=True, header_style="bold magenta")
            unused_table.add_column("Name")
            unused_table.add_column("Created At")
            unused_table.add_column("Last Updated")
            unused_table.add_column("Age (Days)")

            for tag in analysis["unused_tags"]:
                unused_table.add_row(
                    tag["name"],
                    tag["created_at"],
                    tag["updated_at"],
                    str(tag["age_days"]),
                )
            console.print(unused_table)

        # Create table for active tags
        if analysis["active_tags"]:
            console.print("\n[bold green]Active Tags Usage[/bold green]")
            active_table = Table(show_header=True, header_style="bold magenta")
            active_table.add_column("Name")
            active_table.add_column("Lists")
            active_table.add_column("Segments")
            active_table.add_column("Flows")
            active_table.add_column("Total Usage")
            active_table.add_column("Age (Days)")

            for tag in analysis["active_tags"]:
                active_table.add_row(
                    tag["name"],
                    str(tag["list_count"]),
                    str(tag["segment_count"]),
                    str(tag["flow_count"]),
                    str(tag["total_usage"]),
                    str(tag["age_days"]),
                )
            console.print(active_table)

        # Export data if requested
        if export_format:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if export_format == "csv":
                export_path = f"tag_analysis_{timestamp}.csv"
                with open(export_path, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [
                            "Tag Name",
                            "Status",
                            "Total Usage",
                            "Lists",
                            "Segments",
                            "Flows",
                            "Age (Days)",
                            "Created At",
                            "Updated At",
                        ]
                    )

                    for tag in analysis["active_tags"] + analysis["unused_tags"]:
                        writer.writerow(
                            [
                                tag["name"],
                                "Active" if tag["total_usage"] > 0 else "Unused",
                                tag["total_usage"],
                                tag["list_count"],
                                tag["segment_count"],
                                tag["flow_count"],
                                tag["age_days"],
                                tag["created_at"],
                                tag["updated_at"],
                            ]
                        )
                console.print(f"\n[green]Analysis exported to {export_path}[/green]")

            elif export_format == "json":
                export_path = f"tag_analysis_{timestamp}.json"
                with open(export_path, "w") as f:
                    json.dump(analysis, f, indent=2)
                console.print(f"\n[green]Analysis exported to {export_path}[/green]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


async def cleanup_tags_impl(dry_run: bool = True) -> None:
    """Implementation of cleanup tags command."""
    client = get_klaviyo_client()

    try:
        with console.status("[bold yellow]Analyzing tags for cleanup...") as status:
            results = await client.delete_unused_tags(dry_run=dry_run)

        if dry_run:
            console.print(
                "\n[bold yellow]DRY RUN - No tags will be deleted[/bold yellow]"
            )

        console.print(f"\nFound {results['count']} unused tags")

        if results["tags_to_delete"]:
            # Create table for tags to delete
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Tag Name")
            table.add_column("Status")

            for tag in results["tags_to_delete"]:
                status = (
                    "[green]Would be deleted[/green]"
                    if dry_run
                    else (
                        "[green]Deleted[/green]"
                        if tag in results.get("deleted", [])
                        else "[red]Failed[/red]"
                    )
                )
                table.add_row(tag, status)

            console.print(table)

        if not dry_run and results.get("errors"):
            console.print("\n[bold red]Errors occurred during deletion:[/bold red]")
            for error in results["errors"]:
                console.print(f"[red]• {error['tag']}: {error['error']}[/red]")

        if not dry_run and results.get("deleted"):
            console.print(
                f"\n[green]Successfully deleted {len(results['deleted'])} tags[/green]"
            )

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


async def analyze_flows_impl(
    days: Optional[int] = 30,
    export_format: Optional[str] = None,
    use_ai: bool = False,
    ai_provider: str = "mock",
) -> None:
    """
    Analyze all flows in the Klaviyo account and provide insights.

    Args:
        days: Number of days to analyze for performance metrics
        export_format: Optional format to export results ("json" or "csv")
        use_ai: Whether to use AI-powered analysis
        ai_provider: AI provider to use ("openai", "anthropic", or "mock")
    """
    client = get_klaviyo_client()
    analyzer = FlowAnalyzer(client)

    try:
        with console.status("[bold green]Analyzing flows..."):
            # Get flow statistics
            flow_stats = await analyzer.analyze_all_flows()

            # Print standard analysis to console
            analyzer.print_flow_analysis(flow_stats)

            # Get cleanup recommendations
            recommendations = analyzer.get_cleanup_recommendations(flow_stats)

            if recommendations:
                console.print("\n[bold]Cleanup Recommendations:[/bold]")
                for rec in recommendations:
                    console.print(rec)

            # Run AI analysis if requested
            if use_ai and flow_stats:
                console.print("\n[bold blue]Running AI Flow Analysis...[/bold blue]")
                with console.status("[bold green]Generating AI insights for flows..."):
                    try:
                        ai_results = await analyzer.get_ai_analysis(
                            flow_stats=flow_stats,
                            provider=cast(ProviderType, ai_provider),
                        )
                        analyzer.print_ai_analysis(ai_results)
                    except Exception as e:
                        console.print(
                            f"[bold red]AI flow analysis failed:[/bold red] {str(e)}"
                        )
                        console.print(
                            "[yellow]Falling back to standard analysis only.[/yellow]"
                        )

            # Export if requested
            if export_format:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"flow_analysis_{timestamp}.{export_format}"

                if export_format == "json":
                    data = [
                        {
                            "id": stat.id,
                            "name": stat.name,
                            "status": stat.status,
                            "archived": stat.archived,
                            "created": stat.created.isoformat(),
                            "updated": stat.updated.isoformat(),
                            "trigger_type": stat.trigger_type,
                            "action_count": stat.action_count,
                            "email_count": stat.email_count,
                            "sms_count": stat.sms_count,
                            "time_delay_count": stat.time_delay_count,
                            "tags": stat.tags,
                        }
                        for stat in flow_stats
                    ]
                    with open(filename, "w") as f:
                        json.dump(data, f, indent=2)

                elif export_format == "csv":
                    with open(filename, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(
                            [
                                "ID",
                                "Name",
                                "Status",
                                "Archived",
                                "Created",
                                "Updated",
                                "Trigger Type",
                                "Actions",
                                "Emails",
                                "SMS",
                                "Delays",
                                "Tags",
                            ]
                        )
                        for stat in flow_stats:
                            writer.writerow(
                                [
                                    stat.id,
                                    stat.name,
                                    stat.status,
                                    stat.archived,
                                    stat.created.isoformat(),
                                    stat.updated.isoformat(),
                                    stat.trigger_type,
                                    stat.action_count,
                                    stat.email_count,
                                    stat.sms_count,
                                    stat.time_delay_count,
                                    ", ".join(stat.tags),
                                ]
                            )

                console.print(f"\n[green]Analysis exported to {filename}[/green]")

    except Exception as e:
        console.print(f"[red]Error analyzing flows: {str(e)}[/red]")
        raise


async def analyze_lists_impl(
    export_format: Optional[str] = None, use_ai: bool = False, ai_provider: str = "mock"
) -> None:
    """
    Analyze all lists in the Klaviyo account and provide insights.

    Args:
        export_format: Optional format to export results ("json" or "csv")
        use_ai: Whether to use AI-powered analysis
        ai_provider: AI provider to use ("openai", "anthropic", or "mock")
    """
    client = get_klaviyo_client()
    analyzer = ListAnalyzer(client)

    try:
        with console.status("[bold green]Analyzing lists..."):
            # Get list statistics
            list_stats = await analyzer.analyze_all_lists()

            # Print standard analysis to console
            analyzer.print_list_analysis(list_stats)

            # Get cleanup recommendations
            recommendations = analyzer.get_cleanup_recommendations(list_stats)

            if recommendations:
                console.print("\n[bold]Cleanup Recommendations:[/bold]")
                for rec in recommendations:
                    console.print(rec)

            # Run AI analysis if requested
            if use_ai and list_stats:
                console.print("\n[bold blue]Running AI List Analysis...[/bold blue]")
                with console.status("[bold green]Generating AI insights for lists..."):
                    try:
                        ai_results = await analyzer.get_ai_analysis(
                            list_stats=list_stats,
                            provider=cast(ProviderType, ai_provider),
                        )
                        analyzer.print_ai_analysis(ai_results)
                    except Exception as e:
                        console.print(
                            f"[bold red]AI list analysis failed:[/bold red] {str(e)}"
                        )
                        console.print(
                            "[yellow]Falling back to standard analysis only.[/yellow]"
                        )

            # Export if requested
            if export_format:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"list_analysis_{timestamp}.{export_format}"

                if export_format == "json":
                    data = [
                        {
                            "id": stat.id,
                            "name": stat.name,
                            "created": stat.created.isoformat(),
                            "updated": stat.updated.isoformat(),
                            "profile_count": stat.profile_count,
                            "is_dynamic": stat.is_dynamic,
                            "folder_name": stat.folder_name,
                            "tags": stat.tags,
                            "analysis": {
                                "is_empty": stat.profile_count == 0,
                                "days_since_update": (
                                    datetime.now(timezone.utc) - stat.updated
                                ).days,
                                "has_tags": bool(stat.tags),
                            },
                        }
                        for stat in list_stats
                    ]
                    with open(filename, "w") as f:
                        json.dump(data, f, indent=2)

                elif export_format == "csv":
                    with open(filename, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(
                            [
                                "ID",
                                "Name",
                                "Type",
                                "Folder",
                                "Profiles",
                                "Created",
                                "Updated",
                                "Days Since Update",
                                "Tags",
                                "Is Empty",
                                "Has Tags",
                            ]
                        )
                        for stat in list_stats:
                            days_since_update = (
                                datetime.now(timezone.utc) - stat.updated
                            ).days
                            writer.writerow(
                                [
                                    stat.id,
                                    stat.name,
                                    "Dynamic" if stat.is_dynamic else "Static",
                                    stat.folder_name or "",
                                    stat.profile_count,
                                    stat.created.isoformat(),
                                    stat.updated.isoformat(),
                                    days_since_update,
                                    ", ".join(stat.tags),
                                    "Yes" if stat.profile_count == 0 else "No",
                                    "Yes" if stat.tags else "No",
                                ]
                            )

                console.print(f"\n[green]Analysis exported to {filename}[/green]")

    except Exception as e:
        console.print(f"[red]Error analyzing lists: {str(e)}[/red]")
        raise


async def analyze_campaigns_impl(
    export_format: Optional[str] = None, use_ai: bool = False, ai_provider: str = "mock"
) -> None:
    """
    Analyze all campaigns in the Klaviyo account and provide insights.

    Args:
        export_format: Optional format to export results ("json" or "csv")
        use_ai: Whether to use AI-powered analysis
        ai_provider: AI provider to use ("openai", "anthropic", or "mock")
    """
    client = get_klaviyo_client()
    analyzer = CampaignAnalyzer(client)

    try:
        with console.status("[bold green]Analyzing campaigns..."):
            # Get campaign statistics
            campaign_stats = await analyzer.analyze_all_campaigns()

            # Print standard analysis to console
            analyzer.print_campaign_analysis(campaign_stats)

            # Get cleanup recommendations
            recommendations = analyzer.get_cleanup_recommendations(campaign_stats)

            if recommendations:
                console.print("\n[bold]Cleanup Recommendations:[/bold]")
                for rec in recommendations:
                    console.print(rec)

            # Run AI analysis if requested
            if use_ai and campaign_stats:
                console.print("\n[bold blue]Running AI Analysis...[/bold blue]")
                with console.status("[bold green]Generating AI insights..."):
                    try:
                        ai_results = await analyzer.get_ai_analysis(
                            campaign_stats=campaign_stats,
                            provider=cast(ProviderType, ai_provider),
                        )
                        analyzer.print_ai_analysis(ai_results)
                    except Exception as e:
                        console.print(
                            f"[bold red]AI analysis failed:[/bold red] {str(e)}"
                        )
                        console.print(
                            "[yellow]Falling back to standard analysis only.[/yellow]"
                        )

            # Export if requested
            if export_format:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"campaign_analysis_{timestamp}.{export_format}"

                if export_format == "json":
                    data = [
                        {
                            "id": stat.id,
                            "name": stat.name,
                            "status": stat.status,
                            "created": stat.created.isoformat(),
                            "updated": stat.updated.isoformat(),
                            "send_time": stat.send_time.isoformat()
                            if stat.send_time
                            else None,
                            "channel": stat.channel,
                            "message_type": stat.message_type,
                            "subject_line": stat.subject_line,
                            "from_email": stat.from_email,
                            "from_name": stat.from_name,
                            "tags": stat.tags,
                            "metrics": {
                                "recipient_count": stat.recipient_count,
                                "open_rate": stat.open_rate,
                                "click_rate": stat.click_rate,
                                "revenue": stat.revenue,
                            },
                            "analysis": {
                                "is_draft": stat.status == "draft",
                                "days_since_update": (
                                    datetime.now(timezone.utc) - stat.updated
                                ).days,
                                "has_tags": bool(stat.tags),
                            },
                        }
                        for stat in campaign_stats
                    ]
                    with open(filename, "w") as f:
                        json.dump(data, f, indent=2)

                elif export_format == "csv":
                    with open(filename, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(
                            [
                                "ID",
                                "Name",
                                "Status",
                                "Channel",
                                "Type",
                                "Subject Line",
                                "From Name",
                                "From Email",
                                "Recipients",
                                "Open Rate",
                                "Click Rate",
                                "Revenue",
                                "Send Time",
                                "Created",
                                "Updated",
                                "Days Since Update",
                                "Tags",
                                "Is Draft",
                                "Has Tags",
                            ]
                        )
                        for stat in campaign_stats:
                            days_since_update = (
                                datetime.now(timezone.utc) - stat.updated
                            ).days
                            writer.writerow(
                                [
                                    stat.id,
                                    stat.name,
                                    stat.status,
                                    stat.channel,
                                    stat.message_type,
                                    stat.subject_line or "",
                                    stat.from_name or "",
                                    stat.from_email or "",
                                    stat.recipient_count,
                                    f"{stat.open_rate:.1%}" if stat.open_rate else "",
                                    f"{stat.click_rate:.1%}" if stat.click_rate else "",
                                    f"${stat.revenue:.2f}" if stat.revenue else "",
                                    stat.send_time.isoformat()
                                    if stat.send_time
                                    else "",
                                    stat.created.isoformat(),
                                    stat.updated.isoformat(),
                                    days_since_update,
                                    ", ".join(stat.tags),
                                    "Yes" if stat.status == "draft" else "No",
                                    "Yes" if stat.tags else "No",
                                ]
                            )

                console.print(f"\n[green]Analysis exported to {filename}[/green]")

    except Exception as e:
        console.print(f"[red]Error analyzing campaigns: {str(e)}[/red]")
        raise


async def export_data_for_ai_impl(
    data_type: str, file_path: Optional[str] = None, export_dir: Optional[str] = None
) -> None:
    """
    Implementation of export data for AI analysis command.

    Args:
        data_type: Type of data to export ("campaigns", "flows", "lists")
        file_path: Optional custom file path
        export_dir: Optional directory to export to
    """
    client = get_klaviyo_client()

    try:
        from ..ai.export import export_data_for_ai_analysis

        # Based on data type, get the appropriate data
        if data_type == "campaigns":
            analyzer = CampaignAnalyzer(client)
            with console.status("[bold green]Fetching campaign data for export..."):
                data = await analyzer.analyze_all_campaigns()
                export_data = [
                    {
                        "id": stat.id,
                        "name": stat.name,
                        "status": stat.status,
                        "created": stat.created.isoformat(),
                        "updated": stat.updated.isoformat(),
                        "send_time": stat.send_time.isoformat()
                        if stat.send_time
                        else None,
                        "channel": stat.channel,
                        "message_type": stat.message_type,
                        "subject_line": stat.subject_line,
                        "from_email": stat.from_email,
                        "from_name": stat.from_name,
                        "tags": stat.tags,
                        "metrics": {
                            "recipient_count": stat.recipient_count,
                            "open_rate": stat.open_rate,
                            "click_rate": stat.click_rate,
                            "revenue": stat.revenue,
                        },
                    }
                    for stat in data
                ]

        elif data_type == "flows":
            analyzer = FlowAnalyzer(client)
            with console.status("[bold green]Fetching flow data for export..."):
                data = await analyzer.analyze_all_flows()
                export_data = [
                    {
                        "id": stat.id,
                        "name": stat.name,
                        "status": stat.status,
                        "archived": stat.archived,
                        "created": stat.created.isoformat(),
                        "updated": stat.updated.isoformat(),
                        "trigger_type": stat.trigger_type,
                        "structure": {
                            "action_count": stat.action_count,
                            "email_count": stat.email_count,
                            "sms_count": stat.sms_count,
                            "time_delay_count": stat.time_delay_count,
                        },
                        "tags": stat.tags,
                    }
                    for stat in data
                ]

        elif data_type == "lists":
            analyzer = ListAnalyzer(client)
            with console.status("[bold green]Fetching list data for export..."):
                data = await analyzer.analyze_all_lists()
                export_data = [
                    {
                        "id": stat.id,
                        "name": stat.name,
                        "created": stat.created.isoformat(),
                        "updated": stat.updated.isoformat(),
                        "profile_count": stat.profile_count,
                        "is_dynamic": stat.is_dynamic,
                        "folder_name": stat.folder_name,
                        "tags": stat.tags,
                    }
                    for stat in data
                ]

        else:
            console.print(f"[yellow]Unsupported data type: {data_type}[/yellow]")
            console.print("[yellow]Supported types: campaigns, flows, lists[/yellow]")
            return

        # Export the data
        export_path = export_data_for_ai_analysis(
            data_type=data_type,
            data=export_data,
            export_dir=export_dir,
            file_name=file_path,
        )

        console.print(f"[green]Data exported successfully to: {export_path}[/green]")
        console.print(
            "\nYou can use this exported data for offline AI analysis or import it with:\n"
            f"[bold]klavicle ai import {export_path}[/bold]"
        )

    except Exception as e:
        console.print(f"[red]Error exporting data: {str(e)}[/red]")


async def unified_ai_analysis_impl(provider: Optional[str] = None) -> None:
    """
    Implementation of unified AI analysis command.

    Args:
        provider: AI provider to use ("openai", "anthropic", or "mock")
    """
    client = get_klaviyo_client()

    try:
        from ..ai.analyzer import AIAnalyzer
        from ..ai.export import export_ai_analysis_results

        # If provider is not specified, use default from config
        if not provider:
            from ..config import get_config

            provider = get_config().get_default_ai_provider()

        # Create analyzers
        campaign_analyzer = CampaignAnalyzer(client)
        flow_analyzer = FlowAnalyzer(client)
        list_analyzer = ListAnalyzer(client)

        # Fetch all data
        with console.status("[bold green]Fetching campaigns data..."):
            campaign_stats = await campaign_analyzer.analyze_all_campaigns()
            campaign_data = [
                {
                    "id": stat.id,
                    "name": stat.name,
                    "status": stat.status,
                    "created": stat.created.isoformat(),
                    "updated": stat.updated.isoformat(),
                    "send_time": stat.send_time.isoformat() if stat.send_time else None,
                    "channel": stat.channel,
                    "message_type": stat.message_type,
                    "subject_line": stat.subject_line,
                    "from_email": stat.from_email,
                    "from_name": stat.from_name,
                    "tags": stat.tags,
                    "metrics": {
                        "recipient_count": stat.recipient_count,
                        "open_rate": stat.open_rate,
                        "click_rate": stat.click_rate,
                        "revenue": stat.revenue,
                    },
                }
                for stat in campaign_stats
            ]

        with console.status("[bold green]Fetching flows data..."):
            flow_stats = await flow_analyzer.analyze_all_flows()
            flow_data = [
                {
                    "id": stat.id,
                    "name": stat.name,
                    "status": stat.status,
                    "archived": stat.archived,
                    "created": stat.created.isoformat(),
                    "updated": stat.updated.isoformat(),
                    "trigger_type": stat.trigger_type,
                    "structure": {
                        "action_count": stat.action_count,
                        "email_count": stat.email_count,
                        "sms_count": stat.sms_count,
                        "time_delay_count": stat.time_delay_count,
                    },
                    "tags": stat.tags,
                }
                for stat in flow_stats
            ]

        with console.status("[bold green]Fetching lists data..."):
            list_stats = await list_analyzer.analyze_all_lists()
            list_data = [
                {
                    "id": stat.id,
                    "name": stat.name,
                    "created": stat.created.isoformat(),
                    "updated": stat.updated.isoformat(),
                    "profile_count": stat.profile_count,
                    "is_dynamic": stat.is_dynamic,
                    "folder_name": stat.folder_name,
                    "tags": stat.tags,
                }
                for stat in list_stats
            ]

        # Combine all data into a unified structure
        unified_data = {
            "campaigns": campaign_data,
            "flows": flow_data,
            "lists": list_data,
        }

        # Create AI analyzer and analyze the unified data
        analyzer = AIAnalyzer(provider=cast(ProviderType, provider))
        with console.status(
            f"[bold green]Performing unified AI analysis using {provider}..."
        ):
            # Convert data to JSON string
            data_json = json.dumps(unified_data)

            # Analyze the unified data
            analysis_results = await analyzer.analyze_data("unified", data_json)

        # Print the analysis results
        console.print("\n[bold blue]Unified AI Analysis Results[/bold blue]")
        analyzer.format_insights_for_display(analysis_results)

        # Export the analysis results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_path = export_ai_analysis_results(
            results=analysis_results,
            data_type="unified",
            file_name=f"unified_analysis_{timestamp}.json",
        )

        console.print(f"\n[green]Analysis results exported to: {results_path}[/green]")

    except Exception as e:
        console.print(f"[red]Error during unified AI analysis: {str(e)}[/red]")


async def import_data_for_ai_impl(
    file_path: str, provider: Optional[str] = None
) -> None:
    """
    Implementation of import and analyze data for AI command.

    Args:
        file_path: Path to the exported data file
        provider: AI provider to use ("openai", "anthropic", or "mock")
    """
    try:
        from ..ai.analyzer import AIAnalyzer
        from ..ai.export import export_ai_analysis_results, import_data_for_ai_analysis

        # Import the data
        with console.status("[bold green]Importing data..."):
            imported_data = import_data_for_ai_analysis(file_path)
            data_type = imported_data["data_type"]
            data = imported_data["data"]

        # If provider is not specified, use default from config
        if not provider:
            from ..config import get_config

            provider = get_config().get_default_ai_provider()

        # Create AI analyzer and analyze the data
        analyzer = AIAnalyzer(provider=cast(ProviderType, provider))
        with console.status(
            f"[bold green]Analyzing {data_type} data using {provider}..."
        ):
            # Convert data to JSON string
            data_json = json.dumps(data)

            # Analyze the data
            analysis_results = await analyzer.analyze_data(data_type, data_json)

        # Print the analysis results
        console.print(f"\n[bold blue]AI Analysis Results for {data_type}[/bold blue]")
        analyzer.format_insights_for_display(analysis_results)

        # Export the analysis results if requested
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_path = export_ai_analysis_results(
            results=analysis_results,
            data_type=data_type,
            file_name=f"{data_type}_analysis_{timestamp}.json",
        )

        console.print(f"\n[green]Analysis results exported to: {results_path}[/green]")

    except Exception as e:
        console.print(f"[red]Error during AI analysis: {str(e)}[/red]")


def run_async(coro):
    """Helper function to run async functions."""
    return asyncio.run(coro)
