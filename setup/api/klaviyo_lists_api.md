Get Lists
get
https://a.klaviyo.com/api/lists
Get all lists in an account.

Filter to request a subset of all lists. Lists can be filtered by id, name, created, and updated fields.

Returns a maximum of 10 results per page.

Rate limits:
Burst: 75/s
Steady: 700/m

Scopes:
lists:read

Query Params
fields[flow]
array of strings
For more information please visit https://developers.klaviyo.com/en/v2024-10-15/reference/api-overview#sparse-fieldsets

ADD string
fields[list]
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
name: any, equals
id: any, equals
created: greater-than
updated: greater-than

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
