# Klavicle

Klavicle is a powerful command-line tool that bridges your customer data with Klaviyo's marketing platform. It helps marketers and developers efficiently manage Klaviyo components while providing AI-powered insights to optimize marketing performance.

## What Does It Do?

Klavicle streamlines your Klaviyo workflow in three key areas:

1. **Data Management**: Execute SQL queries to extract customer data and sync it with your Klaviyo account
2. **Klaviyo Management**: Create and modify lists, segments, and tags with simple commands
3. **AI-Powered Analysis**: Gain insights on your campaigns, flows, and lists using advanced AI models

## Features

### Data Operations
- Execute and save SQL queries for later use
- Parameterized queries with variable substitution
- Database connection management

### Klaviyo Operations
- **Profiles**: Create, update, and view customer profiles
- **Lists**: Create, manage, and analyze subscriber lists
- **Segments**: Build and view dynamic customer segments
- **Tags**: Organize entities with tagging system
- **Campaign Analysis**: Analyze campaign performance metrics
- **Flow Analysis**: Evaluate automation flow structure and effectiveness

### AI Capabilities
- Intelligent analysis of campaign performance metrics
- Flow structure recommendations and optimization tips
- List management insights and segmentation suggestions
- Export analytics to JSON or Markdown for easy sharing
- Multiple AI provider options (OpenAI, Anthropic, or mock for testing)
- Unified cross-entity analysis for holistic marketing insights

### User Experience
- Rich terminal output with formatted tables
- Asynchronous operations for better performance
- Detailed error handling and troubleshooting guidance

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

### Basic Configuration

Create a `.env` file in the project root with the following variables:

```env
# Klaviyo API credentials (required)
KLAVIYO_API_KEY=your_api_key

# Database connection settings (required for query features)
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

### AI Provider Configuration

To use AI features, set up API keys for your preferred providers:

```bash
# Configure Anthropic API key
klavicle config set-api-key anthropic your-anthropic-api-key

# Configure OpenAI API key
klavicle config set-api-key openai your-openai-api-key

# Set default provider
klavicle config set-default-provider anthropic
```

You can also set API keys as environment variables:

```env
ANTHROPIC_API_KEY=your-anthropic-api-key
OPENAI_API_KEY=your-openai-api-key
```

To view your current configuration:

```bash
klavicle config get
```

Additional configuration commands:

```bash
# Export configuration to a file
klavicle config export config_backup.json

# Import configuration from a file
klavicle config import config_backup.json

# Set a specific configuration value
klavicle config set key value

# Unset a configuration value
klavicle config unset key
```

## Usage Guide

### Command Structure

All Klavicle commands follow this general structure:

```
klavicle <module> <command> [options] [arguments]
```

Where:
- `<module>` is the feature area (e.g., query, list, segment, ai)
- `<command>` is the specific action to perform
- `[options]` are flags that modify command behavior
- `[arguments]` are the required inputs for the command

### Database Query Management

Klavicle allows you to save and execute SQL queries with parameter substitution. Queries are stored in the database for reuse.

#### Saving Queries

```bash
# Save a basic query
klavicle query save get_active_users "SELECT * FROM users WHERE status = 'active'"

# Save a query with parameters
klavicle query save users_by_status "SELECT * FROM users WHERE status = :status"

# Save with description
klavicle query save recent_purchases "SELECT * FROM orders WHERE date > :date" --description "Finds orders after specified date"
```

#### Running Queries

```bash
# Run a basic saved query
klavicle query run get_active_users

# Run a query with parameters
klavicle query run users_by_status status=active

# Run with multiple parameters
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

Work with Klaviyo customer profiles:

```bash
# Get a profile by ID or email
klavicle profile get profile_id
klavicle profile get user@example.com

# Create a new profile
klavicle profile create '{"email": "user@example.com", "first_name": "John", "last_name": "Doe"}'

# Update an existing profile
klavicle profile update profile_id '{"first_name": "John", "last_name": "Smith"}'

# Bulk update profiles from a file
klavicle profile update-batch profiles.json --batch-size 50
```

### List Management

Manage Klaviyo subscriber lists:

```bash
# View all lists (default: sorted by updated date, newest first)
klavicle list list

# View lists with formatting options
klavicle list list | less -S  # Prevents truncation with scrolling

# Sort lists
klavicle list list --sort-by created
klavicle list list --sort-by updated --order asc  # Oldest first

# Filter lists by time
klavicle list list --created-after 30  # Lists created in the last 30 days
klavicle list list --updated-after 90  # Lists updated in the last 90 days
klavicle list list --created-after 7 --updated-after 7  # AND condition

# Create a new list
klavicle list create "My List" --description "Optional description"

# Manage list members
klavicle list add-profiles list_id profile_id1 profile_id2
klavicle list remove-profiles list_id profile_id1 profile_id2
```

When using `less -S`:
- Use arrow keys or j/k to scroll up/down
- Use left/right arrows to scroll horizontally
- Press 'q' to exit
- Press '/' to search

### Segment Management

Create and manage dynamic customer segments:

```bash
# View all segments
klavicle segment list

# Create a new segment with conditions
klavicle segment create "High Value Customers" '{
  "and": [
    {"greater_than": [{"property": "total_spent"}, 1000]},
    {"equals": [{"property": "active"}, true]}
  ]
}'
```

### Tag Management

Organize your Klaviyo entities with tags:

```bash
# List all tags
klavicle tag list

# Add tags to a list
klavicle tag add list list_id tag1 tag2

# Add tags to a segment
klavicle tag add segment segment_id tag1 tag2

# Remove tags from entities
klavicle tag remove list list_id tag1 tag2
klavicle tag remove segment segment_id tag1 tag2
```

### AI-Powered Analytics

Klavicle offers AI-powered analytics to derive insights from your Klaviyo data.

#### Basic Analysis Commands

```bash
# Run a comprehensive analysis of all entity types
klavicle ai analyze

# Analyze specific entity types
klavicle ai analyze --entity-type=campaigns
klavicle ai analyze --entity-type=flows
klavicle ai analyze --entity-type=lists

# Use different AI providers
klavicle ai analyze --provider=mock       # Fast, local analysis without API costs
klavicle ai analyze --provider=anthropic  # Analysis using Anthropic's Claude
klavicle ai analyze --provider=openai     # Analysis using OpenAI's models
```

#### Exporting Analysis Results

```bash
# Export results to JSON for programmatic use
klavicle ai analyze --entity-type=campaigns --export-format=json

# Export results to Markdown for documentation
klavicle ai analyze --entity-type=flows --export-format=md
klavicle ai analyze --entity-type=lists --export-format=markdown  # Alternative syntax
```

#### Sample Data for Faster Analysis

For testing or quick insights, use the `--sample` flag to analyze a smaller subset of data:

```bash
# Analyze a sample of campaigns data
klavicle ai analyze --entity-type=campaigns --sample

# Combine options
klavicle ai analyze --entity-type=flows --provider=anthropic --export-format=md --sample
```

#### AI Data Export and Import

For offline analysis or to share data sets:

```bash
# Export data for AI analysis
klavicle ai export campaigns --file campaigns_data.json

# Import and analyze previously exported data
klavicle ai import campaigns_data.json --provider anthropic

# Initialize an exports directory
klavicle ai init-exports-dir ./exports
```

#### Exported Files

Exported files will be saved in the current directory with a timestamp:
- JSON files: `entity_type_analysis_YYYYMMDD_HHMMSS.json`
- Markdown files: `entity_type_analysis_YYYYMMDD_HHMMSS.md`

The markdown exports contain:
- Summary of findings
- Key metrics and statistics
- Recommendations with expected impact
- Entity-specific insights (campaigns, flows, or lists)
- Visual formatting for easier reading

#### Unified Analysis

Perform cross-entity analysis to gain holistic insights across your entire Klaviyo account:

```bash
# Run unified analysis across all entity types
klavicle ai analyze --entity-type=all --provider=anthropic

# Export unified analysis to markdown
klavicle ai analyze --entity-type=all --export-format=md
```

The unified analysis provides:
- Account health score and assessment
- Cross-entity tag consistency analysis
- Customer journey mapping
- Strategic recommendations with priority levels
- Resource allocation guidance
- Correlation analysis between different marketing entities

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

### 3. AI Analysis and Optimization Workflow

```bash
# 1. Analyze current campaign performance
klavicle ai analyze --entity-type=campaigns --provider=anthropic --export-format=md

# 2. Review the markdown report for insights
cat campaigns_analysis_*.md

# 3. Analyze flow structure and performance
klavicle ai analyze --entity-type=flows --provider=anthropic --export-format=md

# 4. Create new tags based on AI recommendations
klavicle tag add list list_id recommended_tag

# 5. Run a unified analysis after making changes
klavicle ai analyze --entity-type=all --provider=anthropic --export-format=md
```

### 4. Analyzing Campaign Performance

```bash
# Run AI-powered campaign analysis for deeper insights
klavicle ai analyze --entity-type=campaigns --provider=anthropic

# Export campaign analysis as structured markdown for reporting
klavicle ai analyze --entity-type=campaigns --export-format=md
```

### 5. Evaluating Automation Flows

```bash
# Get AI-powered flow analysis
klavicle ai analyze --entity-type=flows --provider=anthropic

# Review complex flows for optimization opportunities
klavicle ai analyze --entity-type=flows --sample --export-format=md
```

## Project Structure

Klavicle is organized into modular components:

- `klavicle/`: Main package root
  - `ai/`: AI analysis capabilities and providers
    - `analyzer.py`: Core AI analysis functionality
    - `prompts.py`: Specialized prompts for different entity types
    - `mock_analyzer.py`: Testing without API calls
    - `export.py`: Data import/export utilities
  - `cli/`: Command-line interface and commands
  - `config/`: Configuration management
  - `database/`: Database connection and query handling
  - `klaviyo/`: Klaviyo API integration and analyzers
    - `campaign_analyzer.py`: Campaign performance analysis
    - `flow_analyzer.py`: Flow structure analysis
    - `list_analyzer.py`: List management analysis
  - `validation/`: Data validation and schema handling

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

   - Ensure your Klaviyo API key is correctly set in the `.env` file or `config`
   - Verify the API key has the necessary permissions in Klaviyo
   - Check AI provider API keys are correctly set with `klavicle config get`

2. **Database Connection**

   - Check if the database credentials in `.env` are correct
   - Ensure the database is accessible from your network
   - Test connection with a simple query

3. **Query Parameters**
   - Parameters in SQL queries must be prefixed with `:` (e.g., `:param_name`)
   - Parameter values must be provided when running queries
   - Verify parameter types match expected values

4. **AI Analysis Issues**
   - Authentication errors: Check your API keys
   - Long analysis times: Use the `--sample` flag for faster results
   - Rate limits: Switch to `--provider=mock` option for testing
   - JSON parsing errors: Check for valid Klaviyo data structure
   - Empty responses: Ensure your account has the relevant entity data

### Getting Help

If you encounter any issues:

1. Check the error message for specific details
2. Verify your configuration
3. Ensure you're using the correct command syntax
4. Check the logs for more detailed error information
5. Use the mock provider (`--provider=mock`) to test functionality without API costs

## License

This project is licensed under the MIT License - see the LICENSE file for details.