API overview
📘
We've updated our API versioning and deprecation policy

Review our updated API versioning and deprecation policy to learn about our date-versioned APIs, non-breaking and breaking changes, our API lifecycle, and more to effectively manage your API usage.

Quickstart
New Klaviyo developers: Check out our Get started with Klaviyo series to set up an account, obtain API credentials, and authenticate.
Current Klaviyo developers:
Install one of our new SDKs.
Make test calls with the new API collection in our Postman workspace.
To learn more, see below for an overview of the newly launched API features:
Go into detail on the JSON API features supported by our new API surface.
Explore what's different between the legacy v1/v2 endpoints and the new endpoints with the API comparison chart.
What's new?
Read more about our date-versioned APIs and how they differ from our v1/v2 legacy APIs.

👍
API comparison chart

For developers looking to move from our retired v1/v2 endpoints to our new API endpoints, we highly recommend viewing the API comparison chart to help with the transition.

This chart compares older endpoints to newer equivalents, showcases key feature improvements, and highlights net new endpoints.

OpenAPI and Postman
View the latest OpenAPI spec here.
Import the spec into your favorite API tool, such as Postman, to start interacting with our new APIs right away!

You can also navigate to our Postman Workspace, where you will find our latest collection of requests, along with the API definitions.

Authentication
Klaviyo provides three methods of authentication:

Private key authentication
All /api endpoints use API private keys to authenticate requests. If you do not use an API key for your requests, or if you use a key from the wrong account, your call will return an error. A 400 error indicates an invalid or missing API key. Please refer to this guide for more details on how to generate private keys and use API key scopes.
Public key authentication
All /client endpoints use a public API key: your 6-character company ID, also known as a site ID.
OAuth
If you are a tech partner integrating with Klaviyo, we recommend using OAuth to authenticate your app. OAuth offers multiple benefits over a private key integration, including security, usability, and improved rate limits. Check out our guide on setting up OAuth.
API key scopes
Klaviyo's APIs support the use of API scopes, which allow you to restrict access for third parties using a private API key. Adding a scope helps you protect your and your customers’ data by limiting what third parties can access.

You can add any of the following scopes to any new private API key in Klaviyo:

Read-only
Only allows third parties to view all data associated with the endpoint
Full
Allows third parties to create, delete, or make changes to anything associated with that endpoint
Custom
Allows you to decide how much access to give the third party
Note that you cannot add a scope to an existing private key, which have full access by default. You also cannot edit a private API key after it’s been created. If you need to remove access to a key based on its current scope, delete it and then create a new key with the correct scope.

For more information about the supported scopes for each endpoint and how to add a scope to an API key, please refer to the how to create a scope for a private API key guide.

Private key authentication
Private key authentication for /api endpoints is performed by setting the following request header:

Authorization: Klaviyo-API-Key your-private-api-key
Company ID
Because our /client endpoints are designed to only be called from publicly-browsable client-side environments, these endpoints do not accept private keys, but instead only use public API keys to authorize and route requests. These endpoints are specifically designed to limit functionality to object creation of specific types of objects and do not respond with any potentially sensitive response data. For security reasons, this data must be accessed using private key endpoints only (i.e., /api).

Public API keys are passed to /client endpoints using a query parameter:

curl --request POST \
 --url 'https://a.klaviyo.com/client/events/?company_id=COMPANY_ID'
--header 'Content-Type: application/json'
--data '{DATA}'

Versioning and deprecation
Check out our API versioning and deprecation policy to learn more about how Klaviyo handles API versioning and support.

Status codes and errors
Every response will include an HTTP status code with more details on whether the request succeeded. Check out our guide on status codes and errors to learn more about status codes used by Klaviyo’s API and how to troubleshoot error responses.

Rate limiting
All new API endpoints are rate limited on a per-account basis, and used a fixed-window rate limiting algorithm with two distinct windows: burst (short) and steady (long). All API traffic will be subject to rate limits, and will receive HTTP 429 errors in event either a burst or steady rate limit is reached.

Each endpoint lists its burst and steady rate limits in our API reference documentation.

Learn more about rate limiting in this guide.

JSON:API feature guides
Relationships
Klaviyo’s modern APIs offer powerful new functionality via the relationships object, a thorough set of syntax offered by JSON:API for modeling relationships between resources. This syntax allows developers to efficiently query specific groups of related resources, eliminating the need to perform redundant queries.

Check out our guide to JSON:API Relationships feature for more information on how use, create, modify, and delete resource relationships.

Filtering
JSON:API’s general filtering syntax and its supported operations can be used across all new APIs. Please note that support for specific operators and fields is highly specific to each endpoint. You can refer to the filter query parameter in the API reference documentation for specific operator and field support.

View our JSON:API filtering guide for a list of the filter operations and comparison literals.

The filtering syntax for Klaviyo’s new APIs uses the ?filter query parameter for all endpoints that support filter operations.

Sorting
Where supported, sorting is handled using the ?sort query parameter followed by a field name. Reverse sorting is specified using a - prefix.

Example
GET /api/events/?sort=datetime sorts events by datetime ascending; GET /api/events/?sort=-datetime sorts by datetime descending.

For more examples, view our JSON:API sorting guide.

Sparse fieldsets
Several endpoints support sparse fieldsets to allow developers to select only requested fields of resources, rather than having to retrieve entire resources (which may be very large).

Sparse fieldsets are specified using the ?fields[TYPE]=field1,field2 query parameter, where TYPE is the resource type from which to select only field1 and field2. This also works for included resource types, e.g. ?fields[INCLUDED-TYPE]=field1,field2; however you also need to include that resource in your request, using the include query parameter for this to work.

Examples:

GET /api/events?fields[event]=metric_id,profile_id will retrieve only the metric_id and profile_id attributes for all events returned in the response.
GET /api/events?fields[profile]=first_name,email&include=profile will retrieve all event fields and only the first_name and email attributes for included profile resource data.
To learn more about sparse fieldsets, see our JSON:API sparse fieldsets guide.

Pagination
Our APIs support cursor-based pagination with the query parameter ?page[cursor].

Paginated resource responses will contain a specific set of pagination cursor helper links in their top-level links object, like the following:

JSON

{
"data": [
...
],
"links" : {
"next" : "https://a.klaviyo.com/api/profiles/?page%5Bcursor%5D=bmV4dDo6aWQ6Ok43dW1iVw",
"prev" : null,
"self" : "https://a.klaviyo.com/api/profiles"
}
}
Use these links to navigate to next and previous pages.

Datetimes
Datetime formatting
All datetimes across all new APIs in URLs, request, and response bodies must be formatted as ISO 8601 RFC 3339 datetime strings.
Example:
2023-01-16T23:20:50.52Z
