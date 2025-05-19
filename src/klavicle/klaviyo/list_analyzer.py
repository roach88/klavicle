"""Analyzer for Klaviyo lists."""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiohttp
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import AIAnalyzer for enhanced analysis
from ..ai.analyzer import AIAnalyzer, ProviderType


@dataclass
class ListStats:
    """Statistics for a list."""

    id: str
    name: str
    created: datetime
    updated: datetime
    profile_count: int
    tags: List[str]
    is_dynamic: bool
    folder_name: Optional[str] = None


class ListAnalyzer:
    """Analyzes Klaviyo lists to provide insights and recommendations."""

    def __init__(self, klaviyo_client):
        """Initialize with a KlaviyoClient instance."""
        self.client = klaviyo_client
        self.console = Console()

    async def get_list_stats(self, list_id: str) -> ListStats:
        """Get comprehensive statistics for a single list."""
        # Get list details
        list_response = await self.client._make_request(f"lists/{list_id}")
        list_data = list_response["data"]

        # Get list tags
        tags = await self.client._make_request(f"lists/{list_id}/tags")
        tag_names = [tag["attributes"]["name"] for tag in tags.get("data", [])]

        # Get list profile count
        profiles = await self.client._make_request(f"lists/{list_id}/profiles")
        profile_count = profiles.get("meta", {}).get("total", 0)

        return ListStats(
            id=list_data["id"],
            name=list_data["attributes"]["name"],
            created=datetime.fromisoformat(
                list_data["attributes"]["created"].replace("Z", "+00:00")
            ),
            updated=datetime.fromisoformat(
                list_data["attributes"]["updated"].replace("Z", "+00:00")
            ),
            profile_count=profile_count,
            tags=tag_names,
            is_dynamic=list_data["attributes"].get("is_dynamic", False),
            folder_name=list_data["attributes"].get("folder_name"),
        )

    async def analyze_all_lists(self) -> List[ListStats]:
        """Get statistics for all lists."""
        list_stats = []
        next_page = None

        with self.console.status("[bold green]Fetching lists...") as status:
            while True:
                # If we have a next_page URL, use it directly
                if next_page and next_page.startswith("http"):
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            next_page, headers=self.client._headers
                        ) as response:
                            lists_response = await response.json()
                else:
                    lists_response = await self.client._make_request("lists")

                if not lists_response or "data" not in lists_response:
                    break

                current_lists = lists_response["data"]

                # Process each list in the current page
                for list_item in current_lists:
                    list_id = list_item["id"]
                    list_stats.append(await self.get_list_stats(list_id))
                    status.update(
                        f"[bold green]Processing lists... ({len(list_stats)} found)"
                    )

                # Check for next page
                links = lists_response.get("links", {})
                next_page = links.get("next")

                if not next_page:
                    break

                await asyncio.sleep(0.1)  # Small delay between requests

        return list_stats

    def print_list_analysis(self, list_stats: List[ListStats]) -> None:
        """Print a detailed analysis of lists to the console."""
        # Create summary table
        table = Table(title="List Analysis Summary")
        table.add_column("Name", style="cyan")
        table.add_column("Profiles", justify="right")
        table.add_column("Type", style="magenta")
        table.add_column("Folder", style="yellow")
        table.add_column("Last Updated", style="yellow")
        table.add_column("Tags")

        for stat in sorted(list_stats, key=lambda x: x.updated, reverse=True):
            table.add_row(
                stat.name,
                str(stat.profile_count),
                "Dynamic" if stat.is_dynamic else "Static",
                stat.folder_name or "-",
                stat.updated.strftime("%Y-%m-%d"),
                ", ".join(stat.tags) if stat.tags else "-",
            )

        self.console.print(table)

        # Print insights
        self.console.print("\n[bold]List Insights:[/bold]")

        # Get current time in UTC
        now = datetime.now(timezone.utc)

        # Identify empty lists
        empty_lists = [s for s in list_stats if s.profile_count == 0]
        if empty_lists:
            self.console.print(f"\n🔸 Found {len(empty_lists)} lists with no profiles:")
            for list_item in empty_lists:
                self.console.print(f"  - {list_item.name}")

        # Identify potentially stale lists
        stale_lists = [s for s in list_stats if (now - s.updated).days > 180]
        if stale_lists:
            self.console.print(
                f"\n🔸 Found {len(stale_lists)} lists not updated in over 6 months:"
            )
            for list_item in stale_lists:
                self.console.print(
                    f"  - {list_item.name} (Last updated: {list_item.updated.strftime('%Y-%m-%d')})"
                )

        # Identify lists without tags
        untagged_lists = [s for s in list_stats if not s.tags]
        if untagged_lists:
            self.console.print(f"\n🔸 Found {len(untagged_lists)} lists without tags:")
            for list_item in untagged_lists:
                self.console.print(f"  - {list_item.name}")

    def get_cleanup_recommendations(self, list_stats: List[ListStats]) -> List[str]:
        """Generate recommendations for lists that could potentially be cleaned up."""
        recommendations = []

        # Get current time in UTC
        now = datetime.now(timezone.utc)

        # Check for empty lists
        empty_lists = [s for s in list_stats if s.profile_count == 0]
        if empty_lists:
            recommendations.append(
                f"Consider deleting {len(empty_lists)} lists with no profiles:"
            )
            for list_item in empty_lists:
                recommendations.append(f"  - {list_item.name}")

        # Check for stale lists
        stale_lists = [s for s in list_stats if (now - s.updated).days > 180]
        if stale_lists:
            recommendations.append(
                f"\nReview {len(stale_lists)} lists that haven't been updated in over 6 months:"
            )
            for list_item in stale_lists:
                recommendations.append(
                    f"  - {list_item.name} (Last updated: {list_item.updated.strftime('%Y-%m-%d')})"
                )

        # Check for duplicate list names
        name_counts = {}
        for stat in list_stats:
            if stat.name not in name_counts:
                name_counts[stat.name] = []
            name_counts[stat.name].append(stat.id)

        duplicates = {name: ids for name, ids in name_counts.items() if len(ids) > 1}
        if duplicates:
            recommendations.append("\nFound lists with duplicate names:")
            for name, ids in duplicates.items():
                recommendations.append(f"  - {name} ({len(ids)} lists)")

        return recommendations

    def export_data_for_ai(self, list_stats: List[ListStats]) -> str:
        """
        Convert list stats to a JSON format suitable for AI analysis.

        Args:
            list_stats: List of ListStats objects

        Returns:
            JSON string representation of the data
        """
        # Convert ListStats objects to dictionaries
        list_data = []
        for stat in list_stats:
            # Convert to dict and handle datetime objects
            stat_dict = {
                "id": stat.id,
                "name": stat.name,
                "created": stat.created.isoformat() if stat.created else None,
                "updated": stat.updated.isoformat() if stat.updated else None,
                "profile_count": stat.profile_count,
                "is_dynamic": stat.is_dynamic,
                "folder_name": stat.folder_name,
                "tags": stat.tags,
                "days_since_update": (datetime.now(timezone.utc) - stat.updated).days,
            }
            list_data.append(stat_dict)

        return json.dumps(list_data)

    async def get_ai_analysis(
        self,
        list_stats: List[ListStats],
        ai_analyzer: Optional[AIAnalyzer] = None,
        provider: ProviderType = "mock",  # Use ProviderType, not str
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get AI-powered analysis of list data.

        Args:
            list_stats: List of ListStats objects
            ai_analyzer: Optional AIAnalyzer instance (creates one if not provided)
            provider: AI provider to use if creating a new analyzer
            context: Optional additional context or instructions for analysis

        Returns:
            Dictionary containing AI analysis results
        """
        if not ai_analyzer:
            ai_analyzer = AIAnalyzer(provider=provider)

        data = self.export_data_for_ai(list_stats)
        return await ai_analyzer.analyze_data("lists", data, context)

    def print_ai_analysis(self, ai_results: Dict[str, Any]) -> None:
        """
        Print AI analysis results to the console using rich formatting.

        Args:
            ai_results: The results dictionary from get_ai_analysis
        """
        if not ai_results:
            self.console.print("[yellow]No AI analysis results available.[/yellow]")
            return

        # Check for error
        if "error" in ai_results:
            self.console.print(
                f"[bold red]Error during AI analysis:[/bold red] {ai_results['error']}"
            )
            return

        # Print summary in a panel
        if "summary" in ai_results:
            summary_panel = Panel(
                ai_results["summary"],
                title="[bold blue]AI List Analysis Summary[/bold blue]",
                border_style="blue",
            )
            self.console.print(summary_panel)

        # Print key metrics if available
        if "key_metrics" in ai_results:
            self.console.print("\n[bold blue]Key Metrics[/bold blue]")
            metrics_table = Table(show_header=True, header_style="bold magenta")
            metrics_table.add_column("Metric")
            metrics_table.add_column("Value")

            for metric, value in ai_results["key_metrics"].items():
                # Format the value based on what kind of metric it is
                formatted_value = value
                if "percentage" in metric.lower() and isinstance(value, (int, float)):
                    formatted_value = f"{value:.1%}"
                elif isinstance(value, (int, float)) and value > 1000:
                    formatted_value = f"{value:,}"

                metrics_table.add_row(
                    metric.replace("_", " ").title(), str(formatted_value)
                )

            self.console.print(metrics_table)

        # Print size distribution if available
        if "size_distribution" in ai_results:
            self.console.print("\n[bold blue]List Size Distribution[/bold blue]")
            size_dist = ai_results["size_distribution"]
            size_table = Table(show_header=True, header_style="bold magenta")
            size_table.add_column("Size Category")
            size_table.add_column("Count", justify="right")

            # Show size categories
            for category in ["empty", "small", "medium", "large"]:
                if category in size_dist:
                    size_table.add_row(category.title(), str(size_dist[category]))

            self.console.print(size_table)

            # Show insights about size distribution
            if "insights" in size_dist:
                self.console.print(f"\n{size_dist['insights']}")

        # Print type analysis if available
        if "type_analysis" in ai_results:
            self.console.print("\n[bold blue]List Type Analysis[/bold blue]")
            type_analysis = ai_results["type_analysis"]
            type_table = Table(show_header=True, header_style="bold magenta")
            type_table.add_column("List Type")
            type_table.add_column("Count", justify="right")

            # Static vs Dynamic counts
            static_count = type_analysis.get("static_count", 0)
            dynamic_count = type_analysis.get("dynamic_count", 0)
            type_table.add_row("Static", str(static_count))
            type_table.add_row("Dynamic", str(dynamic_count))

            self.console.print(type_table)

            # Type recommendations
            if "recommendations" in type_analysis:
                self.console.print(f"\n{type_analysis['recommendations']}")

        # Print freshness analysis
        if "freshness_analysis" in ai_results and ai_results["freshness_analysis"]:
            self.console.print("\n[bold blue]List Freshness Analysis[/bold blue]")
            freshness_table = Table(show_header=True, header_style="bold magenta")
            freshness_table.add_column("List Name")
            freshness_table.add_column("Days Since Update", justify="right")
            freshness_table.add_column("Recommendation")

            for list_item in ai_results["freshness_analysis"]:
                freshness_table.add_row(
                    list_item.get("list_name", "Unknown"),
                    str(list_item.get("days_since_update", 0)),
                    list_item.get("recommendation", ""),
                )

            self.console.print(freshness_table)

        # Print organization recommendations
        if (
            "organization_recommendations" in ai_results
            and ai_results["organization_recommendations"]
        ):
            self.console.print("\n[bold blue]Organization Recommendations[/bold blue]")
            for i, rec in enumerate(ai_results["organization_recommendations"], 1):
                area = rec.get("area", "General")
                recommendation = rec.get("recommendation", "No details provided")
                impact = rec.get("expected_impact", "Unknown")

                self.console.print(
                    f"{i}. [bold cyan]{area}:[/bold cyan] {recommendation}"
                )
                self.console.print(f"   [italic](Expected impact: {impact})[/italic]")

        # Print segmentation strategy insights
        if (
            "segmentation_strategy" in ai_results
            and ai_results["segmentation_strategy"]
        ):
            self.console.print(
                "\n[bold blue]Segmentation Strategy Insights[/bold blue]"
            )
            for i, insight in enumerate(ai_results["segmentation_strategy"], 1):
                observation = insight.get("observation", "")
                recommendation = insight.get("recommendation", "")

                self.console.print(f"{i}. [bold]Observation:[/bold] {observation}")
                self.console.print(f"   [bold]Recommendation:[/bold] {recommendation}")
                self.console.print("")

        # Print tag recommendations if available
        if "tag_recommendations" in ai_results and ai_results["tag_recommendations"]:
            self.console.print("\n[bold blue]Tag Recommendations[/bold blue]")
            for i, rec in enumerate(ai_results["tag_recommendations"], 1):
                current = rec.get("current_state", "")
                recommendation = rec.get("recommendation", "")

                self.console.print(f"{i}. [bold]Current:[/bold] {current}")
                self.console.print(f"   [bold]Recommendation:[/bold] {recommendation}")
                self.console.print("")
