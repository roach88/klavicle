Get Tags
get
https://a.klaviyo.com/api/tags
List all tags in an account.

Tags can be filtered by name, and sorted by name or id in ascending or descending order.

Returns a maximum of 50 tags per request, which can be paginated with
cursor-based pagination.

Rate limits:
Burst: 3/s
Steady: 60/m

Scopes:
tags:read

Query Params
fields[tag-group]
array of strings
For more information please visit https://developers.klaviyo.com/en/v2024-10-15/reference/api-overview#sparse-fieldsets

ADD string
fields[tag]
array of strings
For more information please visit https://developers.klaviyo.com/en/v2024-10-15/reference/api-overview#sparse-fieldsets

ADD string
filter
string
For more information please visit https://developers.klaviyo.com/en/v2024-10-15/reference/api-overview#filtering
Allowed field(s)/operator(s):
name: contains, ends-with, equals, starts-with

include
array of strings
For more information please visit https://developers.klaviyo.com/en/v2024-10-15/reference/api-overview#relationships

ADD string
page[cursor]
string
For more information please visit https://developers.klaviyo.com/en/v2024-10-15/reference/api-overview#pagination

sort
string
For more information please visit https://developers.klaviyo.com/en/v2024-10-15/reference/api-overview#sorting

Headers
revision
string
required
Defaults to 2024-10-15
API endpoint revision (format: YYYY-MM-DD[.suffix])

2024-10-15
Responses

200
Success

4XX
Client Error

5XX
Server Error
