"""AI-related CLI commands."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, cast

from rich.console import Console
from rich.panel import Panel

from ..ai.analyzer import AIAnalyzer, ProviderType
from ..ai.export import (
    export_ai_analysis_results,
    export_data_for_ai_analysis,
    import_ai_analysis_results,
    import_data_for_ai_analysis,
)
from ..ai.tag_analyzer import TagAnalyzer
from ..config import get_config
from ..klaviyo.campaign_analyzer import CampaignAnalyzer
from ..klaviyo.client import KlaviyoClient
from ..klaviyo.flow_analyzer import FlowAnalyzer
from ..klaviyo.list_analyzer import ListAnalyzer

console = Console()


async def export_data_impl(
    data_type: str,
    data_source: str,
    output_file: Optional[str] = None,
    export_dir: Optional[str] = None,
) -> None:
    """
    Implementation of export-data command.

    Args:
        data_type: Type of data to export
        data_source: Source of the data (file path)
        output_file: Optional output file name
        export_dir: Optional export directory
    """
    try:
        # Load data from source
        with open(data_source, "r") as f:
            data = json.load(f)

        # Export data
        file_path = export_data_for_ai_analysis(
            data_type=data_type, data=data, export_dir=export_dir, file_name=output_file
        )

        console.print(f"[green]Data exported to:[/green] {file_path}")
    except Exception as e:
        console.print(f"[red]Error exporting data:[/red] {str(e)}")


async def analyze_exported_impl(
    data_file: str,
    output_file: Optional[str] = None,
    export_dir: Optional[str] = None,
    provider: Optional[str] = None,
) -> None:
    """
    Implementation of analyze-exported command.

    Args:
        data_file: Exported data file
        output_file: Optional output file name
        export_dir: Optional export directory
        provider: AI provider to use
    """
    try:
        # Load data from file
        data = import_data_for_ai_analysis(data_file)
        data_type = data["data_type"]

        # Get AI provider
        if not provider:
            provider = get_config().get_default_ai_provider()

        console.print(
            f"[green]Analyzing {data_type} data using {provider} provider...[/green]"
        )

        # Create AI analyzer
        analyzer = AIAnalyzer(provider=provider if provider is not None else "mock")  # type: ignore

        # Analyze data
        with console.status("[bold green]Generating AI insights..."):
            results = await analyzer.analyze_data(
                data_type=data_type, data=data["data"]
            )

        # Print analysis summary
        if "summary" in results:
            summary_panel = Panel(
                results["summary"],
                title=f"[bold blue]AI {data_type.title()} Analysis Summary[/bold blue]",
                border_style="blue",
            )
            console.print(summary_panel)

        # Export results
        if results:
            file_path = export_ai_analysis_results(
                results=results,
                data_type=data_type,
                export_dir=export_dir,
                file_name=output_file,
            )

            console.print(f"[green]Analysis results exported to:[/green] {file_path}")
    except Exception as e:
        console.print(f"[red]Error analyzing data:[/red] {str(e)}")


async def import_analysis_impl(analysis_file: str) -> None:
    """
    Implementation of import-analysis command.

    Args:
        analysis_file: Analysis results file
    """
    try:
        # Load analysis from file
        data = import_ai_analysis_results(analysis_file)
        data_type = data["data_type"]
        results = data["analysis"]

        # Print analysis summary
        if "summary" in results:
            summary_panel = Panel(
                results["summary"],
                title=f"[bold blue]AI {data_type.title()} Analysis Summary[/bold blue]",
                border_style="blue",
            )
            console.print(summary_panel)

        # Create the appropriate analyzer
        if data_type == "campaigns":
            from ..klaviyo.campaign_analyzer import CampaignAnalyzer

            analyzer = CampaignAnalyzer(None)  # No client needed for printing
            analyzer.print_ai_analysis(results)
        elif data_type == "flows":
            from ..klaviyo.flow_analyzer import FlowAnalyzer

            analyzer = FlowAnalyzer(None)  # No client needed for printing
            analyzer.print_ai_analysis(results)
        elif data_type == "lists":
            from ..klaviyo.list_analyzer import ListAnalyzer

            analyzer = ListAnalyzer(None)  # No client needed for printing
            analyzer.print_ai_analysis(results)
        else:
            # Generic printing
            for key, value in results.items():
                if key != "summary" and key != "error":
                    console.print(
                        f"\n[bold blue]{key.replace('_', ' ').title()}[/bold blue]"
                    )
                    if isinstance(value, list):
                        for i, item in enumerate(value, 1):
                            console.print(f"{i}. {item}")
                    elif isinstance(value, dict):
                        for k, v in value.items():
                            console.print(f"{k}: {v}")
                    else:
                        console.print(value)
    except Exception as e:
        console.print(f"[red]Error importing analysis:[/red] {str(e)}")


def initialize_exports_dir_impl(dir_path: Optional[str] = None) -> None:
    """
    Implementation of init-exports-dir command.

    Args:
        dir_path: Path to initialize
    """
    try:
        # Use default if not provided
        if not dir_path:
            from ..ai.export import DEFAULT_EXPORT_DIR

            dir_path = DEFAULT_EXPORT_DIR

        # Create directory
        os.makedirs(dir_path, exist_ok=True)

        # Create .gitignore if needed
        gitignore_path = Path(dir_path) / ".gitignore"
        if not gitignore_path.exists():
            with open(gitignore_path, "w") as f:
                f.write("# Ignore all files in this directory\n*\n!.gitignore\n")

        console.print(f"[green]Exports directory initialized at:[/green] {dir_path}")
    except Exception as e:
        console.print(f"[red]Error initializing exports directory:[/red] {str(e)}")


def get_klaviyo_client() -> KlaviyoClient:
    """Create and return a KlaviyoClient instance."""
    from .klaviyo_commands import get_klaviyo_client

    return get_klaviyo_client()


async def analyze_impl(
    entity_type: str = "all",
    provider: str = "mock",
    export_format: Optional[str] = None,
    sample: bool = False,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    batch_size: Optional[int] = None,
    max_tokens: Optional[int] = None,
) -> None:
    """
    Implementation of analyze command.

    Args:
        entity_type: Type of entity to analyze ("campaigns", "flows", "lists", "tags", or "all")
        provider: AI provider to use ("openai", "anthropic", or "mock")
        export_format: Optional format to export results in
        sample: Whether to use a sample of the data
        start_date: Optional start date for filtering (YYYY-MM-DD)
        end_date: Optional end date for filtering (YYYY-MM-DD)
        batch_size: Optional batch size for processing large datasets
        max_tokens: Optional maximum tokens per request
    """
    try:
        # Parse dates if provided
        parsed_start_date = None
        parsed_end_date = None
        if start_date:
            try:
                parsed_start_date = datetime.fromisoformat(start_date)
            except ValueError:
                console.print("[red]Invalid start date format. Use YYYY-MM-DD.[/red]")
                return
        if end_date:
            try:
                parsed_end_date = datetime.fromisoformat(end_date)
            except ValueError:
                console.print("[red]Invalid end date format. Use YYYY-MM-DD.[/red]")
                return

        # Initialize Klaviyo client
        client = get_klaviyo_client()

        # Determine which entity types to analyze
        analyze_campaigns = entity_type in ["campaigns", "all", "tags"]
        analyze_flows = entity_type in ["flows", "all", "tags"]
        analyze_lists = entity_type in ["lists", "all", "tags"]

        # Initialize unified data structure
        unified_data = {}

        # Fetch data for each entity type
        if analyze_campaigns:
            campaign_analyzer = CampaignAnalyzer(client)
            with console.status("[bold green]Fetching campaigns data..."):
                campaign_stats = await campaign_analyzer.analyze_all_campaigns()
                campaign_data = [
                    {
                        "id": stat.id,
                        "name": stat.name,
                        "status": stat.status,
                        "created": stat.created.isoformat() if stat.created else None,
                        "updated": stat.updated.isoformat() if stat.updated else None,
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
                    for stat in campaign_stats
                ]
                unified_data["campaigns"] = campaign_data
                if sample:
                    sample_size = 3
                    unified_data["campaigns"] = unified_data["campaigns"][:sample_size]
                    console.print(
                        f"[yellow]Using sample of {sample_size} campaigns for analysis[/yellow]"
                    )

        if analyze_flows:
            flow_analyzer = FlowAnalyzer(client)
            with console.status("[bold green]Fetching flows data..."):
                flow_stats = await flow_analyzer.analyze_all_flows()
                flow_data = [
                    {
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
                    }
                    for stat in flow_stats
                ]
                unified_data["flows"] = flow_data
                if sample:
                    sample_size = 3
                    unified_data["flows"] = unified_data["flows"][:sample_size]
                    console.print(
                        f"[yellow]Using sample of {sample_size} flows for analysis[/yellow]"
                    )

        if analyze_lists:
            list_analyzer = ListAnalyzer(client)
            with console.status("[bold green]Fetching lists data..."):
                list_stats = await list_analyzer.analyze_all_lists()
                list_data = [
                    {
                        "id": stat.id,
                        "name": stat.name,
                        "created": stat.created.isoformat() if stat.created else None,
                        "updated": stat.updated.isoformat() if stat.updated else None,
                        "profile_count": stat.profile_count,
                        "is_dynamic": stat.is_dynamic,
                        "folder_name": stat.folder_name,
                        "tags": stat.tags,
                    }
                    for stat in list_stats
                ]
                unified_data["lists"] = list_data
                if sample:
                    sample_size = 3
                    unified_data["lists"] = unified_data["lists"][:sample_size]
                    console.print(
                        f"[yellow]Using sample of {sample_size} lists for analysis[/yellow]"
                    )

        # Tag analysis as a standalone entity
        if entity_type == "tags":
            tag_analyzer = TagAnalyzer()
            tag_map = tag_analyzer.aggregate_tags(
                campaigns=unified_data.get("campaigns"),
                flows=unified_data.get("flows"),
                lists_=unified_data.get("lists"),
            )
            report = tag_analyzer.summary_report(tag_map)
            tag_analyzer.print_tag_analysis(report)
            # Optionally export results
            if export_format == "json":
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_path = f"tags_analysis_{timestamp}.json"
                with open(export_path, "w") as f:
                    json.dump(report, f, indent=2)
                console.print(
                    f"\n[green]Tag analysis exported to {export_path}[/green]"
                )
            return

        # Create AI analyzer with custom batch size and max tokens if provided
        provider_type: ProviderType = cast(ProviderType, provider)
        ai_analyzer = AIAnalyzer(  # type: ignore
            provider=provider_type,
            batch_size=batch_size if batch_size is not None else 1000,
            max_tokens=max_tokens if max_tokens is not None else 100000,
        )

        # Analyze the data
        if entity_type == "all":
            # Unified analysis of all entity types
            with console.status(
                f"[bold green]Performing unified AI analysis using {provider}..."
            ):
                # Use our enhanced mock functionality if using the mock provider
                if provider == "mock":
                    data_json = json.dumps(unified_data)
                    analysis_results = await ai_analyzer.analyze_data(
                        "unified",
                        data_json,
                        start_date=parsed_start_date,
                        end_date=parsed_end_date,
                    )
                else:
                    # Use regular API providers
                    data_json = json.dumps(unified_data)
                    analysis_results = await ai_analyzer.analyze_data(
                        "unified",
                        data_json,
                        start_date=parsed_start_date,
                        end_date=parsed_end_date,
                    )

            # Print the unified analysis results
            console.print("\n[bold blue]Unified AI Analysis Results[/bold blue]")

            # Print summary in a panel if available
            if "summary" in analysis_results:
                summary_panel = Panel(
                    analysis_results["summary"],
                    title="[bold blue]AI Analysis Summary[/bold blue]",
                    border_style="blue",
                )
                console.print(summary_panel)

            # Display the insights
            ai_analyzer.format_insights_for_display(analysis_results)

        else:
            # Individual entity analysis
            with console.status(
                f"[bold green]Analyzing {entity_type} using {provider}..."
            ):
                # Use our enhanced mock functionality if using the mock provider
                if provider == "mock":
                    data_json = json.dumps(unified_data.get(entity_type, []))
                    analysis_results = await ai_analyzer.analyze_data(
                        entity_type,
                        data_json,
                        start_date=parsed_start_date,
                        end_date=parsed_end_date,
                    )
                else:
                    # Use regular API providers
                    data_json = json.dumps(unified_data.get(entity_type, []))
                    analysis_results = await ai_analyzer.analyze_data(
                        entity_type,
                        data_json,
                        start_date=parsed_start_date,
                        end_date=parsed_end_date,
                    )

            # Print the analysis results
            console.print(
                f"\n[bold blue]AI Analysis Results for {entity_type}[/bold blue]"
            )

            # Print specific entity analysis
            if entity_type == "campaigns" and campaign_analyzer:
                campaign_analyzer.print_ai_analysis(analysis_results)
            elif entity_type == "flows" and flow_analyzer:
                flow_analyzer.print_ai_analysis(analysis_results)
            elif entity_type == "lists" and list_analyzer:
                list_analyzer.print_ai_analysis(analysis_results)
            else:
                # Generic display for any entity type
                ai_analyzer.format_insights_for_display(analysis_results)

        # Export results if requested
        if export_format:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if export_format == "json":
                export_path = f"{entity_type}_analysis_{timestamp}.json"
                with open(export_path, "w") as f:
                    json.dump(analysis_results, f, indent=2)
                console.print(f"\n[green]Analysis exported to {export_path}[/green]")
            else:
                console.print(
                    f"[yellow]Unsupported export format: {export_format}[/yellow]"
                )

    except Exception as e:
        console.print(f"[red]Error during analysis:[/red] {str(e)}")
