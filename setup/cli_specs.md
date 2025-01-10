# CLI Interface Specification

## Command Structure

### Base Commands

```bash
tool [command] [subcommand] [options]
```

### Global Options

```bash
--verbose        # Enable verbose output
--dry-run       # Run without making changes
--config FILE   # Specify config file
--log-level     # Set logging level
```

## Command Groups

### Query Management

```bash
# Execute query
tool query run [name] [--params key=value]

# Save query
tool query save [name] [--query "SQL"] [--description "text"]

# List saved queries
tool query list

# Test query
tool query test [name] [--params key=value]
```

### Profile Operations

```bash
# Update profiles
tool profiles update [--file FILE] [--batch-size N]

# View profile
tool profiles get [email]

# Create profile
tool profiles create [--file FILE]
```

### List/Segment Operations

```bash
# Create list
tool lists create [name] [--description "text"]

# Update list
tool lists update [id] [--name "text"] [--description "text"]

# Create segment
tool segments create [name] [--conditions FILE]

# Update segment
tool segments update [id] [--conditions FILE]
```

### Tag Operations

```bash
# Add tags
tool tags add [--resource-type TYPE] [--resource-id ID] [--tags tag1,tag2]

# Remove tags
tool tags remove [--resource-type TYPE] [--resource-id ID] [--tags tag1,tag2]
```

## Interactive Mode

### Menu Structure

```python
MAIN_MENU = [
    "Execute Query",
    "Manage Profiles",
    "Manage Lists/Segments",
    "Manage Tags",
    "Exit"
]

QUERY_MENU = [
    "Run Saved Query",
    "Create New Query",
    "List Saved Queries",
    "Test Query",
    "Back"
]

PROFILE_MENU = [
    "Update Profiles",
    "View Profile",
    "Create Profile",
    "Back"
]
```

### User Interface Components

#### Progress Bars

```python
class ProgressDisplay:
    """Progress bar for long-running operations"""
    def __init__(self):
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn()
        )
```

#### Status Updates

```python
class StatusDisplay:
    """Status messages with color coding"""
    def show_status(self, message: str, status: str):
        colors = {
            "success": "green",
            "error": "red",
            "warning": "yellow",
            "info": "blue"
        }
        color = colors.get(status, "white")
        self.console.print(f"[{color}]{message}[/{color}]")
```

## Error Display

### Error Message Format

```python
{
    "error": {
        "type": "ValidationError",
        "message": "Invalid email format",
        "details": {
            "field": "email",
            "value": "invalid-email"
        }
    }
}
```

### Visual Feedback

```python
class ErrorDisplay:
    """Error message formatting"""
    def show_error(self, error: Dict):
        panel = Panel(
            self._format_error(error),
            title="[red]Error[/red]",
            border_style="red"
        )
        self.console.print(panel)
```

## Configuration

### Config File Structure

```yaml
database:
  host: localhost
  port: 5432
  name: customer_db

klaviyo:
  api_key: ${KLAVIYO_API_KEY}

batch_size: 50
retry_limit: 3
log_level: INFO
```

### Environment Variables

```bash
KLAVIYO_API_KEY=your-api-key
DB_PASSWORD=your-password
LOG_LEVEL=INFO
```
