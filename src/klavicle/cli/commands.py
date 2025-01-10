import click

from .klaviyo_commands import (
    add_tags_impl,
    create_list_impl,
    create_profile_impl,
    create_segment_impl,
    get_lists_impl,
    get_profile_impl,
    get_segments_impl,
    get_tags_impl,
    remove_tags_impl,
    run_async,
    update_profile_impl,
)
from .query_commands import list_queries_impl, run_query_impl, save_query_impl


@click.group()
def cli():
    """Klavicle - Klaviyo Data Integration Tool"""
    pass


@cli.group()
def query():
    """Query management commands"""
    pass


@query.command(name="run")
@click.argument("name", required=False)
@click.argument("params", nargs=-1)
def run_query(name: str, params: tuple):
    """Run a saved query or execute a query from stdin.

    If NAME is provided, runs the saved query with that name.
    Otherwise, reads query from stdin.

    PARAMS are optional key=value pairs used in query parameters.
    """
    run_query_impl(name, params)


@query.command(name="save")
@click.argument("name")
@click.argument("query")
@click.option("--description", "-d", help="Query description")
def save_query(name: str, query: str, description: str):
    """Save a query for later use.

    NAME is the unique identifier for the query.
    QUERY is the SQL query text to save.
    """
    save_query_impl(name, query, description)


@query.command(name="list")
def list_queries():
    """List all saved queries."""
    list_queries_impl()


@cli.group()
def profile():
    """Profile management commands"""
    pass


@profile.command(name="get")
@click.argument("profile_id")
def get_profile(profile_id: str):
    """Get a profile by ID."""
    run_async(get_profile_impl(profile_id))


@profile.command(name="create")
@click.argument("data")
def create_profile(data: str):
    """Create a new profile.

    DATA is a JSON string containing profile data.
    """
    run_async(create_profile_impl(data))


@profile.command(name="update")
@click.argument("profile_id")
@click.argument("data")
def update_profile(profile_id: str, data: str):
    """Update an existing profile.

    PROFILE_ID is the ID of the profile to update.
    DATA is a JSON string containing profile data.
    """
    run_async(update_profile_impl(profile_id, data))


@cli.group()
def list():
    """List management commands"""
    pass


@list.command(name="list")
@click.option(
    "--sort-by",
    type=click.Choice(["created", "updated"]),
    default="updated",
    help="Sort lists by created or updated date",
)
@click.option(
    "--order",
    type=click.Choice(["asc", "desc"]),
    default="desc",
    help="Sort order (ascending or descending)",
)
@click.option(
    "--created-after",
    type=int,
    help="Show lists created within the last N days",
)
@click.option(
    "--updated-after",
    type=int,
    help="Show lists updated within the last N days",
)
def get_lists(
    sort_by: str, order: str, created_after: int | None, updated_after: int | None
):
    """List all lists."""
    run_async(
        get_lists_impl(
            sort_by=sort_by,
            order=order,
            created_after=created_after,
            updated_after=updated_after,
        )
    )


@list.command(name="create")
@click.argument("name")
@click.option("--description", "-d", help="List description")
def create_list(name: str, description: str):
    """Create a new list.

    NAME is the name of the list.
    """
    run_async(create_list_impl(name, description))


@cli.group()
def segment():
    """Segment management commands"""
    pass


@segment.command(name="list")
@click.option(
    "--sort-by",
    type=click.Choice(["created", "updated"]),
    default="updated",
    help="Sort segments by created or updated date",
)
@click.option(
    "--order",
    type=click.Choice(["asc", "desc"]),
    default="desc",
    help="Sort order (ascending or descending)",
)
@click.option(
    "--created-after",
    type=int,
    help="Show segments created within the last N days",
)
@click.option(
    "--updated-after",
    type=int,
    help="Show segments updated within the last N days",
)
def get_segments(
    sort_by: str, order: str, created_after: int | None, updated_after: int | None
):
    """List all segments."""
    run_async(
        get_segments_impl(
            sort_by=sort_by,
            order=order,
            created_after=created_after,
            updated_after=updated_after,
        )
    )


@segment.command(name="create")
@click.argument("name")
@click.argument("conditions")
def create_segment(name: str, conditions: str):
    """Create a new segment.

    NAME is the name of the segment.
    CONDITIONS is a JSON string containing segment conditions.
    """
    run_async(create_segment_impl(name, conditions))


@cli.group()
def tag():
    """Tag management commands"""
    pass


@tag.command(name="list")
@click.option(
    "--sort-by",
    type=click.Choice(["created", "updated"]),
    default="updated",
    help="Sort tags by created or updated date",
)
@click.option(
    "--order",
    type=click.Choice(["asc", "desc"]),
    default="desc",
    help="Sort order (ascending or descending)",
)
@click.option(
    "--created-after",
    type=int,
    help="Show tags created within the last N days",
)
@click.option(
    "--updated-after",
    type=int,
    help="Show tags updated within the last N days",
)
def get_tags(
    sort_by: str, order: str, created_after: int | None, updated_after: int | None
):
    """List all tags."""
    run_async(
        get_tags_impl(
            sort_by=sort_by,
            order=order,
            created_after=created_after,
            updated_after=updated_after,
        )
    )


@tag.command(name="add")
@click.argument("resource_type")
@click.argument("resource_id")
@click.argument("tags", nargs=-1)
def add_tags(resource_type: str, resource_id: str, tags: tuple):
    """Add tags to a resource.

    RESOURCE_TYPE is the type of resource (profile, list, segment).
    RESOURCE_ID is the ID of the resource.
    TAGS are the tags to add.
    """
    run_async(add_tags_impl(resource_type, resource_id, list(tags)))


@tag.command(name="remove")
@click.argument("resource_type")
@click.argument("resource_id")
@click.argument("tags", nargs=-1)
def remove_tags(resource_type: str, resource_id: str, tags: tuple):
    """Remove tags from a resource.

    RESOURCE_TYPE is the type of resource (profile, list, segment).
    RESOURCE_ID is the ID of the resource.
    TAGS are the tags to remove.
    """
    run_async(remove_tags_impl(resource_type, resource_id, list(tags)))


if __name__ == "__main__":
    cli()
