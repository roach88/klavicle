import json
from typing import Optional, Tuple

import click
from rich.console import Console
from rich.table import Table

from ..database.connection import create_db_connection
from ..database.query_manager import QueryManager
from ..validation.handlers import (
    ValidationError,
    validate_saved_query,
    validate_sql_query,
)

console = Console()


def parse_params(params: Tuple[str, ...]) -> dict:
    """Parse key=value parameters into a dictionary."""
    result = {}
    for param in params:
        try:
            key, value = param.split("=", 1)
            # Try to parse as JSON for complex types
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass  # Keep as string if not valid JSON
            result[key.strip()] = value
        except ValueError:
            raise click.BadParameter(
                f"Invalid parameter format: {param}. Use key=value format."
            )
    return result


def get_query_manager() -> QueryManager:
    """Create and return a QueryManager instance."""
    engine = create_db_connection()
    return QueryManager(engine)


def run_query_impl(name: Optional[str], params: Tuple[str, ...]) -> None:
    """Implementation of query run command."""
    query_manager = get_query_manager()

    try:
        # Parse parameters
        param_dict = parse_params(params) if params else {}

        # Get query text
        if name:
            query_text, stored_params = query_manager.load_query(name)
            # Merge stored params with provided params
            if stored_params:
                param_dict = {**stored_params, **param_dict}
        else:
            # If no name provided, expect query from stdin
            query_text = click.get_text_stream("stdin").read().strip()
            if not query_text:
                raise click.UsageError(
                    "No query provided. Either specify a saved query name or pipe a query."
                )

        # Validate query
        query_text = validate_sql_query(query_text)

        # Execute query
        with console.status("[bold green]Executing query..."):
            results = query_manager.execute_query(query_text, param_dict)

        # Display results
        if not results:
            console.print("[yellow]No results found.[/yellow]")
            return

        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        columns = results[0].keys()
        for column in columns:
            table.add_column(str(column))

        # Add rows
        for row in results:
            table.add_row(*[str(value) for value in row.values()])

        console.print(table)

    except ValidationError as e:
        console.print(f"[red]Validation error:[/red] {str(e)}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


def save_query_impl(name: str, query: str, description: Optional[str] = None) -> None:
    """Implementation of query save command."""
    query_manager = get_query_manager()

    try:
        # Validate query data
        validate_saved_query(name=name, query_text=query, description=description)
        validate_sql_query(query)

        # Save query
        with console.status("[bold green]Saving query..."):
            query_manager.save_query(name, query, description)

        console.print(f"[green]Query '{name}' saved successfully.[/green]")

    except ValidationError as e:
        console.print(f"[red]Validation error:[/red] {str(e)}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


def list_queries_impl() -> None:
    """Implementation of query list command."""
    query_manager = get_query_manager()

    try:
        # Get all queries
        with console.status("[bold green]Fetching queries..."):
            queries = query_manager.list_queries()

        if not queries:
            console.print("[yellow]No saved queries found.[/yellow]")
            return

        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name")
        table.add_column("Description")
        table.add_column("Parameters")
        table.add_column("Created")
        table.add_column("Updated")

        # Add rows
        for query in queries:
            table.add_row(
                query["name"],
                query.get("description", ""),
                str(query.get("parameters", {})),
                str(query.get("created_at", "")),
                str(query.get("updated_at", "")),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
