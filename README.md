# Klavicle

Klavicle is a powerful command-line tool for integrating data between PostgreSQL and Klaviyo. It provides a seamless interface for managing Klaviyo profiles, lists, segments, and tags while allowing you to save and execute SQL queries against your database.

## Features

- Execute and save SQL queries for later use
- Manage Klaviyo profiles (create, update, view)
- Handle Klaviyo lists (create, list)
- Work with Klaviyo segments (create, list)
- Manage tags (add, remove, list)
- Rich terminal output with formatted tables
- Asynchronous operations for better performance

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/klavicle.git
cd klavicle
```

2. Install using Poetry:

```bash
poetry install
```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
KLAVIYO_API_KEY=your_api_key
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

## Usage

### Query Management

```bash
# Run a saved query
klavicle query run query_name param1=value1 param2=value2

# Save a query
klavicle query save query_name "SELECT * FROM table"

# List saved queries
klavicle query list
```

### Profile Management

```bash
# Get a profile
klavicle profile get profile_id

# Create a profile
klavicle profile create '{"email": "user@example.com", "first_name": "John"}'

# Update a profile
klavicle profile update profile_id '{"first_name": "John", "last_name": "Doe"}'
```

### List Management

```bash
# List all lists
klavicle list list

# Create a list
klavicle list create "My List" --description "A description"
```

### Segment Management

```bash
# List all segments
klavicle segment list

# Create a segment
klavicle segment create "My Segment" '{"conditions": {...}}'
```

### Tag Management

```bash
# List all tags
klavicle tag list

# Add tags
klavicle tag add profile profile_id tag1 tag2

# Remove tags
klavicle tag remove profile profile_id tag1 tag2
```

## Development

1. Install development dependencies:

```bash
poetry install --with dev
```

2. Run tests:

```bash
poetry run pytest
```

3. Format code:

```bash
poetry run black .
poetry run isort .
```

4. Type checking:

```bash
poetry run mypy .
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
