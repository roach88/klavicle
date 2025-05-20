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
class FlowStats:
    """Statistics for a flow."""

    id: str
    name: str
    status: str
    archived: bool
    created: datetime
    updated: datetime
    trigger_type: str
    action_count: int
    email_count: int
    sms_count: int
    time_delay_count: int
    tags: List[str]
    last_activity: Optional[datetime] = None


class FlowAnalyzer:
    """Analyzes Klaviyo flows to provide insights and recommendations."""

    def __init__(self, klaviyo_client):
        """Initialize with a KlaviyoClient instance."""
        self.client = klaviyo_client
        self.console = Console()

    async def get_flow_stats(self, flow_id: str) -> FlowStats:
        """Get comprehensive statistics for a single flow."""
        # Get flow details
        flow = await self.client._make_request(f"flows/{flow_id}")
        flow_data = flow["data"]

        # Get flow actions
        actions = await self.client._make_request(f"flows/{flow_id}/flow-actions")
        action_data = actions.get("data", [])

        # Get flow tags
        tags = await self.client._make_request(f"flows/{flow_id}/tags")
        tag_names = [tag["attributes"]["name"] for tag in tags.get("data", [])]

        # Count different action types
        email_count = sum(
            1
            for action in action_data
            if action["attributes"]["action_type"] == "SEND_EMAIL"
        )
        sms_count = sum(
            1
            for action in action_data
            if action["attributes"]["action_type"] == "SEND_SMS"
        )
        time_delay_count = sum(
            1
            for action in action_data
            if action["attributes"]["action_type"] == "TIME_DELAY"
        )

        # Safely handle datetime parsing with fallbacks
        try:
            created = datetime.fromisoformat(
                flow_data["attributes"]["created"].replace("Z", "+00:00")
            ) if flow_data["attributes"].get("created") else datetime.now(timezone.utc)
        except (ValueError, AttributeError, KeyError):
            created = datetime.now(timezone.utc)
            
        try:
            updated = datetime.fromisoformat(
                flow_data["attributes"]["updated"].replace("Z", "+00:00")
            ) if flow_data["attributes"].get("updated") else datetime.now(timezone.utc)
        except (ValueError, AttributeError, KeyError):
            updated = datetime.now(timezone.utc)
            
        return FlowStats(
            id=flow_data["id"],
            name=flow_data["attributes"]["name"],
            status=flow_data["attributes"]["status"],
            archived=flow_data["attributes"]["archived"],
            created=created,
            updated=updated,
            trigger_type=flow_data["attributes"]["trigger_type"],
            action_count=len(action_data),
            email_count=email_count,
            sms_count=sms_count,
            time_delay_count=time_delay_count,
            tags=tag_names,
        )

    async def analyze_all_flows(self) -> List[FlowStats]:
        """Get statistics for all flows."""
        flow_stats = []
        next_page = None

        with self.console.status("[bold green]Fetching flows...") as status:
            while True:
                # If we have a next_page URL, use it directly
                if next_page and next_page.startswith("http"):
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            next_page, headers=self.client._headers
                        ) as response:
                            flows_response = await response.json()
                else:
                    flows_response = await self.client._make_request("flows")

                if not flows_response or "data" not in flows_response:
                    break

                current_flows = flows_response["data"]

                # Process each flow in the current page
                for flow in current_flows:
                    flow_id = flow["id"]
                    flow_stats.append(await self.get_flow_stats(flow_id))
                    status.update(
                        f"[bold green]Processing flows... ({len(flow_stats)} found)"
                    )

                # Check for next page
                links = flows_response.get("links", {})
                next_page = links.get("next")

                if not next_page:
                    break

                await asyncio.sleep(0.1)  # Small delay between requests

        return flow_stats

    def print_flow_analysis(self, flow_stats: List[FlowStats]) -> None:
        """Print a detailed analysis of flows to the console."""
        # Create summary table
        table = Table(title="Flow Analysis Summary")
        table.add_column("Name", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Trigger Type", style="magenta")
        table.add_column("Actions", justify="right")
        table.add_column("Emails", justify="right")
        table.add_column("SMS", justify="right")
        table.add_column("Delays", justify="right")
        table.add_column("Last Updated", style="yellow")
        table.add_column("Tags")

        for stat in sorted(flow_stats, key=lambda x: x.updated, reverse=True):
            table.add_row(
                stat.name,
                stat.status,
                stat.trigger_type,
                str(stat.action_count),
                str(stat.email_count),
                str(stat.sms_count),
                str(stat.time_delay_count),
                stat.updated.strftime("%Y-%m-%d"),
                ", ".join(stat.tags) if stat.tags else "-",
            )

        self.console.print(table)

        # Print insights
        self.console.print("\n[bold]Flow Insights:[/bold]")

        # Get current time in UTC
        now = datetime.now(timezone.utc)

        # Identify inactive flows
        inactive_flows = [s for s in flow_stats if s.status != "live"]
        if inactive_flows:
            self.console.print(
                f"\n🔸 Found {len(inactive_flows)} inactive flows that could be reviewed:"
            )
            for flow in inactive_flows:
                self.console.print(f"  - {flow.name} (Status: {flow.status})")

        # Identify potentially abandoned flows
        old_flows = [s for s in flow_stats if (now - s.updated).days > 180]
        if old_flows:
            self.console.print(
                f"\n🔸 Found {len(old_flows)} flows not updated in over 6 months:"
            )
            for flow in old_flows:
                self.console.print(
                    f"  - {flow.name} (Last updated: {flow.updated.strftime('%Y-%m-%d')})"
                )

        # Identify flows without tags
        untagged_flows = [s for s in flow_stats if not s.tags]
        if untagged_flows:
            self.console.print(f"\n🔸 Found {len(untagged_flows)} flows without tags:")
            for flow in untagged_flows:
                self.console.print(f"  - {flow.name}")

    async def get_flow_performance(
        self, flow_id: str, days: int = 30
    ) -> Dict[str, Any]:
        """Get performance metrics for a specific flow."""
        try:
            response = await self.client._make_request(
                "flow-values-reports",
                method="POST",
                data={
                    "data": {
                        "type": "flow-values-report",
                        "attributes": {
                            "statistics": ["opens", "clicks", "conversions", "revenue"],
                            "timeframe": f"last_{days}_days",
                        },
                    }
                },
            )
            return response
        except Exception as e:
            self.console.print(
                f"[red]Error getting performance data for flow {flow_id}: {str(e)}[/red]"
            )
            return {}

    def get_cleanup_recommendations(self, flow_stats: List[FlowStats]) -> List[str]:
        """Generate recommendations for flows that could potentially be cleaned up."""
        recommendations = []

        # Get current time in UTC
        now = datetime.now(timezone.utc)

        # Check for draft flows older than 30 days
        old_drafts = [
            s for s in flow_stats if s.status == "draft" and (now - s.created).days > 30
        ]
        if old_drafts:
            recommendations.append(
                f"Consider deleting {len(old_drafts)} draft flows that are over 30 days old:"
            )
            for flow in old_drafts:
                recommendations.append(
                    f"  - {flow.name} (Created: {flow.created.strftime('%Y-%m-%d')})"
                )

        # Check for archived flows
        archived = [s for s in flow_stats if s.archived]
        if archived:
            recommendations.append(
                f"\nFound {len(archived)} archived flows that could be deleted if no longer needed:"
            )
            for flow in archived:
                recommendations.append(f"  - {flow.name}")

        # Check for duplicate trigger types
        trigger_counts = {}
        for stat in flow_stats:
            if stat.trigger_type not in trigger_counts:
                trigger_counts[stat.trigger_type] = []
            trigger_counts[stat.trigger_type].append(stat.name)

        for trigger_type, flows in trigger_counts.items():
            if len(flows) > 1:
                recommendations.append(
                    f"\nFound {len(flows)} flows with '{trigger_type}' trigger - consider consolidating:"
                )
                for flow in flows:
                    recommendations.append(f"  - {flow}")

        return recommendations

    def export_data_for_ai(self, flow_stats: List[FlowStats]) -> str:
        """
        Convert flow stats to a JSON format suitable for AI analysis.

        Args:
            flow_stats: List of FlowStats objects

        Returns:
            JSON string representation of the data
        """
        # Convert FlowStats objects to dictionaries
        flow_data = []
        for stat in flow_stats:
            # Convert to dict and handle datetime objects
            stat_dict = {
                "id": stat.id,
                "name": stat.name,
                "status": stat.status,
                "archived": stat.archived,
                "created": stat.created.isoformat() if stat.created else None,
                "updated": stat.updated.isoformat() if stat.updated else None,
                "trigger_type": stat.trigger_type,
                "structure": {
                    "action_count": stat.action_count,
                    "email_count": stat.email_count,
                    "sms_count": stat.sms_count,
                    "time_delay_count": stat.time_delay_count,
                },
                "tags": stat.tags,
                "last_activity": stat.last_activity.isoformat()
                if stat.last_activity
                else None,
            }
            flow_data.append(stat_dict)

        return json.dumps(flow_data)

    async def get_ai_analysis(
        self,
        flow_stats: List[FlowStats],
        ai_analyzer: Optional[AIAnalyzer] = None,
        provider: ProviderType = "mock",  # Use ProviderType, not str
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get AI-powered analysis of flow data.

        Args:
            flow_stats: List of FlowStats objects
            ai_analyzer: Optional AIAnalyzer instance (creates one if not provided)
            provider: AI provider to use if creating a new analyzer
            context: Optional additional context or instructions for analysis

        Returns:
            Dictionary containing AI analysis results
        """
        if not ai_analyzer:
            ai_analyzer = AIAnalyzer(provider=provider)

        data = self.export_data_for_ai(flow_stats)
        return await ai_analyzer.analyze_data("flows", data, context)

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
                title="[bold blue]AI Flow Analysis Summary[/bold blue]",
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
                if isinstance(value, (int, float)) and value > 1000:
                    formatted_value = f"{value:,}"

                metrics_table.add_row(
                    metric.replace("_", " ").title(), str(formatted_value)
                )

            self.console.print(metrics_table)

        # Print trigger analysis
        if "trigger_analysis" in ai_results and ai_results["trigger_analysis"]:
            self.console.print("\n[bold blue]Trigger Analysis[/bold blue]")
            trigger_table = Table(show_header=True, header_style="bold magenta")
            trigger_table.add_column("Trigger Type")
            trigger_table.add_column("Count", justify="right")
            trigger_table.add_column("Percentage", justify="right")
            trigger_table.add_column("Effectiveness")

            for trigger in ai_results["trigger_analysis"]:
                # Format percentage
                percentage = trigger.get("percentage", 0)
                if isinstance(percentage, (int, float)):
                    formatted_percentage = f"{percentage:.1%}"
                else:
                    formatted_percentage = str(percentage)

                trigger_table.add_row(
                    trigger.get("trigger_type", "Unknown"),
                    str(trigger.get("count", 0)),
                    formatted_percentage,
                    trigger.get("effectiveness", ""),
                )

            self.console.print(trigger_table)

        # Print channel usage
        if "channel_usage" in ai_results:
            self.console.print("\n[bold blue]Channel Usage Analysis[/bold blue]")
            channel_usage = ai_results["channel_usage"]
            channel_table = Table(show_header=True, header_style="bold magenta")
            channel_table.add_column("Channel")
            channel_table.add_column("Count", justify="right")
            channel_table.add_column("Percentage", justify="right")

            # Email
            email_count = channel_usage.get("email_count", 0)
            email_percentage = channel_usage.get("email_percentage", 0)
            if isinstance(email_percentage, (int, float)):
                email_percentage = f"{email_percentage:.1%}"
            channel_table.add_row("Email", str(email_count), str(email_percentage))

            # SMS
            sms_count = channel_usage.get("sms_count", 0)
            sms_percentage = channel_usage.get("sms_percentage", 0)
            if isinstance(sms_percentage, (int, float)):
                sms_percentage = f"{sms_percentage:.1%}"
            channel_table.add_row("SMS", str(sms_count), str(sms_percentage))

            self.console.print(channel_table)

            # Channel insights
            if "insights" in channel_usage:
                self.console.print(f"\n{channel_usage['insights']}")

        # Print complexity analysis
        if "complexity_analysis" in ai_results and ai_results["complexity_analysis"]:
            self.console.print("\n[bold blue]Flow Complexity Analysis[/bold blue]")
            complexity_table = Table(show_header=True, header_style="bold magenta")
            complexity_table.add_column("Flow Name")
            complexity_table.add_column("Steps", justify="right")
            complexity_table.add_column("Complexity")
            complexity_table.add_column("Simplification Suggestion")

            for flow in ai_results["complexity_analysis"]:
                complexity_table.add_row(
                    flow.get("flow_name", "Unknown"),
                    str(flow.get("steps", 0)),
                    flow.get("complexity", "Unknown"),
                    flow.get("simplification", ""),
                )

            self.console.print(complexity_table)

        # Print recommendations
        if (
            "organization_recommendations" in ai_results
            and ai_results["organization_recommendations"]
        ):
            self.console.print("\n[bold blue]AI Flow Recommendations[/bold blue]")
            for i, rec in enumerate(ai_results["organization_recommendations"], 1):
                area = rec.get("area", "General")
                recommendation = rec.get("recommendation", "No details provided")
                impact = rec.get("expected_impact", "Unknown")

                self.console.print(
                    f"{i}. [bold cyan]{area}:[/bold cyan] {recommendation}"
                )
                self.console.print(f"   [italic](Expected impact: {impact})[/italic]")

        # Print tag recommendations if available
        if "tag_recommendations" in ai_results and ai_results["tag_recommendations"]:
            self.console.print("\n[bold blue]Tag Recommendations[/bold blue]")
            for i, rec in enumerate(ai_results["tag_recommendations"], 1):
                current = rec.get("current_state", "")
                recommendation = rec.get("recommendation", "")

                self.console.print(f"{i}. [bold]Current:[/bold] {current}")
                self.console.print(f"   [bold]Recommendation:[/bold] {recommendation}")
                self.console.print("")
