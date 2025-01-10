# Klavicle

Klavicle is a command-line tool for increasing motility between your customer data and your Klaviyo campaigns.

## Features

- Execute and save SQL queries for later use
- Manage Klaviyo profiles (create, update, view)
- Handle Klaviyo lists (create, view, add/remove profiles)
- Work with Klaviyo segments (create, view)
- Manage tags (add, remove, view)
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

## Usage Guide

### Database Query Management

Klavicle allows you to save and execute SQL queries with parameter substitution. Queries are stored in the database for reuse.

#### Saving Queries

```bash
# Save a basic query
klavicle query save get_active_users "SELECT * FROM users WHERE status = 'active'"

# Save a query with parameters
klavicle query save users_by_status "SELECT * FROM users WHERE status = :status"
```

#### Running Queries

```bash
# Run a basic saved query
klavicle query run get_active_users

# Run a query with parameters
klavicle query run users_by_status status=active

# Run multiple parameters
klavicle query run find_users status=active created_after="2024-01-01"
```

#### Managing Queries

```bash
# List all saved queries
klavicle query list

# Delete a saved query
klavicle query delete query_name
```

### Profile Management

```bash
# Get a profile by ID
klavicle profile get profile_id

# Create a new profile
klavicle profile create '{"email": "user@example.com", "first_name": "John", "last_name": "Doe"}'

# Update an existing profile
klavicle profile update profile_id '{"first_name": "John", "last_name": "Smith"}'
```

### List Management

```bash
# View all lists (default: sorted by updated date, newest first)
klavicle list list

# View long list output with scrolling (prevents truncation)
klavicle list list | less -S

# View lists sorted by creation date
klavicle list list --sort-by created

# View lists sorted by updated date in ascending order (oldest first)
klavicle list list --sort-by updated --order asc

# View lists sorted by creation date in ascending order
klavicle list list --sort-by created --order asc

# Filter lists by time
klavicle list list --created-after 30  # Lists created in the last 30 days
klavicle list list --updated-after 90  # Lists updated in the last 90 days
klavicle list list --created-after 7 --updated-after 7  # Lists created AND updated in the last week

# Combine filtering and sorting
klavicle list list --created-after 30 --sort-by created --order asc  # Oldest to newest lists from last 30 days

# Create a new list
klavicle list create "My List" --description "Optional description"

# Add profiles to a list
klavicle list add-profiles list_id profile_id1 profile_id2

# Remove profiles from a list
klavicle list remove-profiles list_id profile_id1 profile_id2
```

When using `less -S`:

- Use arrow keys or j/k to scroll up/down
- Use left/right arrows to scroll horizontally
- Press 'q' to exit
- Press '/' to search

### Segment Management

```bash
# View all segments
klavicle segment list

# Create a new segment
klavicle segment create "High Value Customers" '{
  "and": [
    {"greater_than": [{"property": "total_spent"}, 1000]},
    {"equals": [{"property": "active"}, true]}
  ]
}'
```

### Tag Management

```bash
# List all tags
klavicle tag list

# Add tags to a list
klavicle tag add list list_id tag1 tag2

# Add tags to a segment
klavicle tag add segment segment_id tag1 tag2

# Remove tags from a list
klavicle tag remove list list_id tag1 tag2

# Remove tags from a segment
klavicle tag remove segment segment_id tag1 tag2
```

## Example Workflows

### 1. Creating a Targeted Customer List

```bash
# 1. Save a query to find high-value customers
klavicle query save high_value_customers "
  SELECT customer_id
  FROM orders
  GROUP BY customer_id
  HAVING SUM(order_total) > :min_spent
"

# 2. Create a new list in Klaviyo
klavicle list create "High Value Customers" --description "Customers who spent over $1000"

# 3. Run the query and add profiles to the list
klavicle query run high_value_customers min_spent=1000 | xargs -I {} klavicle list add-profiles list_id {}
```

### 2. Segmenting and Tagging Users

```bash
# 1. Create a segment for active subscribers
klavicle segment create "Active Subscribers" '{
  "and": [
    {"equals": [{"property": "subscribed"}, true]},
    {"greater_than": [{"property": "last_active"}, "2024-01-01"]}
  ]
}'

# 2. Tag the segment for campaign targeting
klavicle tag add segment segment_id active_subscriber campaign_target
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

## Troubleshooting

### Common Issues

1. **API Key Issues**

   - Ensure your Klaviyo API key is correctly set in the `.env` file
   - Verify the API key has the necessary permissions

2. **Database Connection**

   - Check if the database credentials in `.env` are correct
   - Ensure the database is accessible from your network

3. **Query Parameters**
   - Parameters in SQL queries must be prefixed with `:` (e.g., `:param_name`)
   - Parameter values must be provided when running queries

### Getting Help

If you encounter any issues:

1. Check the error message for specific details
2. Verify your configuration
3. Ensure you're using the correct command syntax
4. Check the logs for more detailed error information

## License

This project is licensed under the MIT License - see the LICENSE file for details.
