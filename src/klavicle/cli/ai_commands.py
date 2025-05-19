"""AI-related CLI commands."""

import json
import os
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from ..ai.analyzer import AIAnalyzer
from ..ai.export import (
    export_ai_analysis_results,
    export_data_for_ai_analysis,
    import_ai_analysis_results,
    import_data_for_ai_analysis,
)
from ..config import get_config

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
