import click
from rich.console import Console
from rich.panel import Panel

from .klaviyo_commands import (
    analyze_campaigns_impl,
    analyze_flows_impl,
    analyze_lists_impl,
    run_async,
)

console = Console()


def show_error(message: str):
    """Display error message."""
    panel = Panel(message, title="[red]Error[/red]", border_style="red")
    console.print(panel)


def show_success(message: str):
    """Display success message."""
    panel = Panel(message, title="[green]Success[/green]", border_style="green")
    console.print(panel)


@click.group()
@click.option("--verbose", is_flag=True, help="Enable verbose output")
@click.option("--dry-run", is_flag=True, help="Run without making changes")
@click.option("--config", type=click.Path(exists=True), help="Specify config file")
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="INFO",
    help="Set logging level",
)
def cli(verbose: bool, dry_run: bool, config: str, log_level: str):
    """Klaviyo Data Integration Tool (KDIT) - CLI interface for managing Klaviyo data."""
    pass


# Query Management Commands
@cli.group()
def query():
    """Query management commands."""
    pass


@query.command("run")
@click.argument("name", required=False)
@click.option("--params", multiple=True, help="Query parameters (key=value)")
def run_query(name: str, params: tuple):
    """Execute a saved query or provide a new one."""
    # Implementation will go here
    pass


@query.command("save")
@click.argument("name")
@click.option("--query", required=True, help="SQL query to save")
@click.option("--description", help="Query description")
def save_query(name: str, query: str, description: str):
    """Save a query for later use."""
    # Implementation will go here
    pass


@query.command("list")
def list_queries():
    """List all saved queries."""
    # Implementation will go here
    pass


# Profile Operations Commands
@cli.group()
def profiles():
    """Profile management commands."""
    pass


@profiles.command("update")
@click.option(
    "--file", type=click.Path(exists=True), help="File containing profile data"
)
@click.option("--batch-size", type=int, default=50, help="Batch size for updates")
def update_profiles(file: str, batch_size: int):
    """Update profiles from a file."""
    # Implementation will go here
    pass


@profiles.command("get")
@click.argument("email")
def get_profile(email: str):
    """View profile details."""
    # Implementation will go here
    pass


# List/Segment Operations Commands
@cli.group()
def lists():
    """List management commands."""
    pass


@lists.command("create")
@click.argument("name")
@click.option("--description", help="List description")
def create_list(name: str, description: str):
    """Create a new list."""
    # Implementation will go here
    pass


@lists.command("analyze")
@click.option(
    "--export-format",
    type=click.Choice(["json", "csv"]),
    help="Export format for analysis results",
)
def analyze_lists(export_format: str):
    """Analyze all lists and provide insights and recommendations."""
    run_async(analyze_lists_impl(export_format=export_format))


@cli.group()
def segments():
    """Segment management commands."""
    pass


@segments.command("create")
@click.argument("name")
@click.option(
    "--conditions",
    type=click.Path(exists=True),
    help="JSON file with segment conditions",
)
def create_segment(name: str, conditions: str):
    """Create a new segment."""
    # Implementation will go here
    pass


# Tag Operations Commands
@cli.group()
def tags():
    """Tag management commands."""
    pass


@tags.command("add")
@click.option("--resource-type", type=click.Choice(["list", "segment"]), required=True)
@click.option("--resource-id", required=True)
@click.option("--tags", required=True, help="Comma-separated list of tags")
def add_tags(resource_type: str, resource_id: str, tags: str):
    """Add tags to a resource."""
    # Implementation will go here
    pass


@tags.command("remove")
@click.option("--resource-type", type=click.Choice(["list", "segment"]), required=True)
@click.option("--resource-id", required=True)
@click.option("--tags", required=True, help="Comma-separated list of tags")
def remove_tags(resource_type: str, resource_id: str, tags: str):
    """Remove tags from a resource."""
    # Implementation will go here
    pass


@cli.group()
def flows():
    """Flow management and analysis commands."""
    pass


@flows.command("analyze")
@click.option(
    "--days",
    type=int,
    default=30,
    help="Number of days to analyze for performance metrics",
)
@click.option(
    "--export-format",
    type=click.Choice(["json", "csv"]),
    help="Export format for analysis results",
)
def analyze_flows(days: int, export_format: str):
    """Analyze all flows and provide insights and recommendations."""
    run_async(analyze_flows_impl(days=days, export_format=export_format))


@cli.group()
def campaigns():
    """Campaign management and analysis commands."""
    pass


@campaigns.command("analyze")
@click.option(
    "--export-format",
    type=click.Choice(["json", "csv"]),
    help="Export format for analysis results",
)
def analyze_campaigns(export_format: str):
    """Analyze all campaigns and provide insights and recommendations."""
    run_async(analyze_campaigns_impl(export_format=export_format))


if __name__ == "__main__":
    cli()
