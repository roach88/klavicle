import click
from rich.console import Console
from rich.panel import Panel

from .ai_commands import analyze_impl
from .config_commands import (
    export_config_impl,
    get_config_impl,
    import_config_impl,
    set_api_key_impl,
    set_config_impl,
    set_default_provider_impl,
    unset_config_impl,
)
from .klaviyo_commands import (
    analyze_campaigns_impl,
    analyze_flows_impl,
    analyze_lists_impl,
    export_data_for_ai_impl,
    import_data_for_ai_impl,
    unified_ai_analysis_impl,
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
def config():
    """Configuration management commands."""
    pass


@config.command("get")
def get_config():
    """Display current configuration."""
    get_config_impl()


@config.command("set")
@click.argument("key")
@click.argument("value")
def set_config(key: str, value: str):
    """Set a configuration value."""
    set_config_impl(key, value)


@config.command("unset")
@click.argument("key")
def unset_config(key: str):
    """Remove a configuration value."""
    unset_config_impl(key)


@config.command("set-api-key")
@click.argument("provider", type=click.Choice(["openai", "anthropic"]))
@click.argument("api_key")
def set_api_key(provider: str, api_key: str):
    """Set API key for an AI provider."""
    set_api_key_impl(provider, api_key)


@config.command("set-default-provider")
@click.argument("provider", type=click.Choice(["openai", "anthropic", "mock"]))
def set_default_provider(provider: str):
    """Set default AI provider."""
    set_default_provider_impl(provider)


@config.command("export")
@click.argument("file_path")
def export_config(file_path: str):
    """Export configuration to a file."""
    export_config_impl(file_path)


@config.command("import")
@click.argument("file_path", type=click.Path(exists=True))
def import_config(file_path: str):
    """Import configuration from a file."""
    import_config_impl(file_path)


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
@click.option(
    "--ai",
    is_flag=True,
    help="Use AI-powered analysis to provide enhanced insights",
)
@click.option(
    "--ai-provider",
    type=click.Choice(["openai", "anthropic", "mock"]),
    help="AI provider to use for analysis (requires API key)",
)
def analyze_lists(export_format: str, ai: bool, ai_provider: str):
    """Analyze all lists and provide insights and recommendations."""
    # If ai_provider is not specified, use default from config
    if ai and not ai_provider:
        from ..config import get_config
        ai_provider = get_config().get_default_ai_provider()
    
    run_async(analyze_lists_impl(
        export_format=export_format,
        use_ai=ai,
        ai_provider=ai_provider
    ))


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
@click.option(
    "--ai",
    is_flag=True,
    help="Use AI-powered analysis to provide enhanced insights",
)
@click.option(
    "--ai-provider",
    type=click.Choice(["openai", "anthropic", "mock"]),
    help="AI provider to use for analysis (requires API key)",
)
def analyze_flows(days: int, export_format: str, ai: bool, ai_provider: str):
    """Analyze all flows and provide insights and recommendations."""
    # If ai_provider is not specified, use default from config
    if ai and not ai_provider:
        from ..config import get_config
        ai_provider = get_config().get_default_ai_provider()
    
    run_async(analyze_flows_impl(
        days=days,
        export_format=export_format,
        use_ai=ai,
        ai_provider=ai_provider
    ))


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
@click.option(
    "--ai",
    is_flag=True,
    help="Use AI-powered analysis to provide enhanced insights",
)
@click.option(
    "--ai-provider",
    type=click.Choice(["openai", "anthropic", "mock"]),
    help="AI provider to use for analysis (requires API key)",
)
def analyze_campaigns(export_format: str, ai: bool, ai_provider: str):
    """Analyze all campaigns and provide insights and recommendations."""
    # If ai_provider is not specified, use default from config
    if ai and not ai_provider:
        from ..config import get_config
        ai_provider = get_config().get_default_ai_provider()
    
    run_async(analyze_campaigns_impl(
        export_format=export_format,
        use_ai=ai,
        ai_provider=ai_provider
    ))


@cli.group()
def ai():
    """AI-powered analysis commands."""
    pass


@ai.command("export")
@click.argument("data_type", type=click.Choice(["campaigns", "flows", "lists"]))
@click.option(
    "--file", 
    help="Custom file name for the export",
)
@click.option(
    "--dir", 
    help="Directory to export to (defaults to ./exports)",
)
def export_for_ai(data_type: str, file: str, dir: str):
    """Export data for offline AI analysis."""
    run_async(export_data_for_ai_impl(
        data_type=data_type,
        file_path=file,
        export_dir=dir
    ))


@ai.command("import")
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--provider",
    type=click.Choice(["openai", "anthropic", "mock"]),
    help="AI provider to use for analysis (requires API key)",
)
def import_for_ai(file_path: str, provider: str):
    """Import and analyze data using AI."""
    run_async(import_data_for_ai_impl(
        file_path=file_path,
        provider=provider
    ))


@ai.command("unified")
@click.option(
    "--provider",
    type=click.Choice(["openai", "anthropic", "mock"]),
    help="AI provider to use for analysis (requires API key)",
)
@click.option(
    "--sample", 
    is_flag=True,
    help="Use a smaller dataset sample for faster testing",
)
def unified_analysis(provider: str, sample: bool):
    """Run unified AI analysis across all entities (campaigns, flows, lists)."""
    run_async(unified_ai_analysis_impl(
        provider=provider,
        use_sample=sample
    ))


@ai.command("analyze")
@click.option(
    "--entity-type",
    type=click.Choice(["campaigns", "flows", "lists", "all"]), 
    default="all",
    help="Type of entities to analyze",
)
@click.option(
    "--provider",
    type=click.Choice(["openai", "anthropic", "mock"]),
    default="mock",
    help="AI provider to use for analysis (requires API key)",
)
@click.option(
    "--export",
    type=click.Choice(["json", "csv"]),
    help="Export format for analysis results",
)
@click.option(
    "--sample", 
    is_flag=True,
    help="Use a smaller dataset sample for faster testing",
)
def analyze(entity_type: str, provider: str, export: str, sample: bool):
    """
    Run AI analysis on specified entities with a simplified approach.
    
    This command provides a more streamlined way to analyze your Klaviyo data using AI.
    It can analyze campaigns, flows, lists, or all entities at once.
    
    Examples:
        klavicle ai analyze --entity-type=campaigns
        klavicle ai analyze --provider=anthropic
        klavicle ai analyze --entity-type=flows --export=json --sample
    """
    run_async(analyze_impl(
        entity_type=entity_type,
        provider=provider,
        export_format=export,
        sample=sample
    ))


if __name__ == "__main__":
    cli()
