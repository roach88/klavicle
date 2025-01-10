# User Flow Documentation

## CLI Command Flow

```mermaid
graph TD
    A[Start Tool] --> B{Choose Mode}
    B -->|Interactive| C[Interactive Menu]
    B -->|Direct Commands| D[Command Execution]

    C --> E{Select Operation}
    E -->|Query| F[Query Management]
    E -->|Profile| G[Profile Operations]
    E -->|List/Segment| H[List/Segment Operations]
    E -->|Tags| I[Tag Operations]

    F --> J[Execute Query]
    J --> K{Validation}
    K -->|Pass| L[Process Results]
    K -->|Fail| M[Show Error]

    G --> N[Profile Updates]
    N --> O{Batch Processing}
    O --> P[Rate Limit Check]
    P -->|OK| Q[Execute Updates]
    P -->|Limited| R[Wait/Retry]
```

## Core User Journey

### Query Management Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant DB
    participant Klaviyo

    User->>CLI: Select Query Operation
    alt New Query
        User->>CLI: Input Query
        CLI->>DB: Validate Query
        DB-->>CLI: Validation Result
        CLI->>User: Confirm Execution
    else Saved Query
        User->>CLI: Select Saved Query
        CLI->>DB: Load Query
        DB-->>CLI: Query Details
    end

    User->>CLI: Execute Query
    CLI->>DB: Run Query
    DB-->>CLI: Results
    CLI->>Klaviyo: Process Results
    Klaviyo-->>CLI: API Response
    CLI->>User: Operation Summary
```

### Error Handling

```mermaid
graph TD
    A[Error Occurs] --> B{Error Type}
    B -->|Database| C[DB Error Handler]
    B -->|API| D[API Error Handler]
    B -->|Validation| E[Validation Handler]

    C --> F{Can Retry?}
    F -->|Yes| G[Retry Operation]
    F -->|No| H[Log Error]

    D --> I{Rate Limited?}
    I -->|Yes| J[Wait and Retry]
    I -->|No| K[Process Error]

    E --> L[Show Validation Errors]

    G --> M[Continue Operation]
    H --> N[Show Error Message]
    J --> M
    K --> N
    L --> N
```

## Edge Cases

### Offline Mode

- Cache saved queries
- Queue failed operations
- Sync when connection restored

### Incomplete Data

- Validate before processing
- Skip invalid records
- Log validation failures

### Session Management

- Auto-retry on session expiry
- Maintain connection pools
- Handle timeout gracefully

## User Permissions

### Permission Levels

1. Admin

   - Full access to all operations
   - Can manage saved queries
   - Can modify batch settings

2. Operator
   - Can execute saved queries
   - Can perform profile updates
   - Cannot modify system settings

### Permission Flow

```mermaid
graph TD
    A[User Command] --> B{Check Permission}
    B -->|Admin| C[Full Access]
    B -->|Operator| D[Limited Access]
    B -->|Unauthorized| E[Access Denied]

    C --> F[Execute Command]
    D --> G{Verify Operation}
    G -->|Allowed| F
    G -->|Restricted| E
```

## CLI Interaction Examples

### Interactive Mode

```bash
$ tool interactive
> Select operation:
  1. Execute Query
  2. Manage Profiles
  3. Manage Lists/Segments
  4. Manage Tags
> Selected: 1
> Enter query name or 'new':
> new
> Enter query:
SELECT email FROM customers WHERE last_purchase > :date
> Enter parameters:
date (YYYY-MM-DD): 2024-01-01
> Executing query...
> Found 100 results
> Process results? [Y/n]
```

### Direct Command Mode

```bash
# Execute saved query
$ tool query run recent_customers --param date=2024-01-01

# Update profiles
$ tool profiles update --file profiles.csv --batch-size 50

# Create list
$ tool lists create "New Customers" --description "Customers from Jan 2024"
```
