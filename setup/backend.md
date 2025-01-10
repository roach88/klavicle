# Backend Documentation

## Backend Architecture

### Framework and Language

- Primary Language: Python 3.9+
- Key Libraries:
  - SQLAlchemy for database operations
  - aiohttp for async HTTP requests
  - Pydantic for data validation
  - Click for CLI interface

### Component Structure

```
src/
├── database/
│   ├── connection.py      # Database connection management
│   └── query_manager.py   # SQL query execution and storage
├── klaviyo/
│   ├── client.py         # Klaviyo API client
│   ├── profile.py        # Profile operations
│   └── list_segment.py   # List and segment operations
├── validation/
│   ├── schemas.py        # Data validation schemas
│   └── handlers.py       # Validation logic
└── cli/
    └── commands.py       # CLI command definitions
```

## Database Schema

### Query Storage

```sql
CREATE TABLE saved_queries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    query_text TEXT NOT NULL,
    parameters JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### Internal API Structure

#### Database Operations

- `QueryManager`
  - `execute_query(query: str, params: Dict[str, Any]) -> List[Dict]`
  - `save_query(name: str, query: str, params: Dict[str, Any]) -> None`
  - `load_query(name: str) -> Tuple[str, Dict[str, Any]]`

#### Klaviyo Operations

- `KlaviyoClient`
  - Profile Management:
    - `update_profile(profile_id: str, data: Dict) -> Dict`
    - `create_profile(data: Dict) -> Dict`
    - `get_profile(profile_id: str) -> Dict`
  - List Management:
    - `create_list(name: str, data: Dict) -> Dict`
    - `update_list(list_id: str, data: Dict) -> Dict`
  - Segment Management:
    - `create_segment(name: str, conditions: Dict) -> Dict`
    - `update_segment(segment_id: str, data: Dict) -> Dict`
  - Tag Management:
    - `add_tags(resource_type: str, resource_id: str, tags: List[str]) -> Dict`
    - `remove_tags(resource_type: str, resource_id: str, tags: List[str]) -> Dict`

## Authentication and Authorization

### Database Authentication

- Environment variables for database credentials
- Connection pooling with maximum retries
- SSL support for secure connections

### Klaviyo Authentication

- API key management through environment variables
- Rate limit monitoring and adherence
- Request signing and validation

## Error Handling

### Database Errors

- Connection error recovery
- Query timeout handling
- Transaction rollback support

### API Errors

- Rate limit handling with backoff
- Request retry logic
- Error categorization and logging

## Third-Party Integrations

### Klaviyo API Integration

- Rate Limits:
  - Burst: 10/second
  - Steady: 150/minute
- Endpoints:
  - Profiles API
  - Lists API
  - Segments API
- Error Handling:
  - 429 Rate Limit Response
  - Validation Errors
  - Server Errors

### Logging and Monitoring

- Error logging with rotation
- Operation auditing
- Performance metrics tracking
