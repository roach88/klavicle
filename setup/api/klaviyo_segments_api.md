Segments API overview
A segment is a dynamic list that contains profiles meeting a certain set of conditions. For example, a 30-day engagement segment for Boston customers will contain profiles who both have Boston as their location and have purchased one of your products within the last 30 days. This guide will walk you through our new Segments API, which has support for creating, retrieving, updating, and deleting segment definitions.

Before you begin
Check out our general API overview to make sure you’re ready to get started with specific endpoints.

Use cases
Here are some example use cases supported by the Segments API:

Create segments:
"Active" profile segments, e.g., profiles who can receive marketing.
Location-based segments, e.g., profiles with location['city'] set to Boston or San Francisco.
Segments for each loyalty program tier.
30-, 60-, and 90-day engagement segments.
Churned or at-risk segments.
Any other segment that you can create via the UI.
Retrieve a segment’s definition and description.
Update a segment’s definition.
Delete a segment.
Data model
A segment has the following:

id

The segment ID.

attributes

name

The name of the segment.

definition

The segment’s definition. Contains a list of condition_groups, which are combined with a logical AND. Each condition_group contains a list of condition objects combined with a logical OR (see Segment definition below).

is_starred

Whether the segment has been starred.

is_active

Whether the segment is active.

is_processing

Whether the segment is processing.

Segment definition
A segment definition has condition groups. These are the logical groups that are combined with a logical AND. Each condition group contains the following:

conditions

A list of conditions that define the condition group. These are combined with a logical OR. Each condition has the following:

type

The type of condition (e.g., profile_attribute) Each condition type has a different set of supported fields. See Condition types for more details.

Example segment definition
Profiles that are in the Mint Vinyl Subscriber List (list ID = "YzykDM") and live in Columbus or Boston will be a part of the segment below.

Here’s how the condition groups making up the segment definition appear in Klaviyo’s Segment builder:

Location segment for Columbus and Boston customers in Klaviyo's Segment builder
Here’s the same segment in JSON:

As shown above, the first group of conditions is a logical OR with both conditions sharing type “profile-attribute”, in this case, living in Columbus or Boston. The group of conditions contains a single profile-group-membership condition, i.e., the profile must belong to the provided list. The condition groups are joined with a logical AND.

View your segment JSON in Klaviyo
We’ve added a way for you to view and copy the JSON for your segments in the Klaviyo app.

Navigate to Lists & Segments.
Click the 3 dots next to a segment, then select Update definition.
Add .json to the end of the URL.
The JSON should display for your segment as in the example below:

Create Segment
The example request to Create Segment creates a segment with a profile predictive analytics condition that has profiles with a predicted gender of likely female:

Request

curl --request POST \
 --url https://a.klaviyo.com/api/segments/ \
 --header 'Authorization: Klaviyo-API-Key your-private-api-key' \
 --header 'accept: application/json' \
 --header 'content-type: application/json' \
 --header 'revision: 2024-06-15' \
 --data '
{
"data": {
"type": "segment",
"attributes": {
"name": "Likely female segment",
"definition": {
"condition_groups": [
{
"conditions": [
{
"type": "profile-predictive-analytics",
"dimension": "predicted_gender",
"filter": {
"type": "string",
"operator": "equals",
"value": "likely_female"
}
}
]
}
]
},
"is_starred": false
}
}
}
'
Get Segment(s)
We've added the ability to retrieve a segment's definition along with is_starred, is_processing, and is_active fields, as shown in the example segment below.

Request

{
"data": {
"type": "segment",
"id": "YaYUpQ",
"attributes": {
"name": "Boston Purchasers",
"created": "2023-04-28T12:11:42+00:00",
"updated": "2023-05-23T14:15:54+00:00",
"definition": { ... },
"is_starred": false,
"is_active": false,
"is_processing": true
}
}
The following example is a Get Segments request to get all active segments:

Request
Response

curl --request GET \
 --url https://a.klaviyo.com/api/segments/?filter=equals(is_active,true) \
 --header 'Authorization: Klaviyo-API-Key your-private-api-key' \
 --header 'accept: application/json' \
 --header 'revision: 2024-06-15'
Update Segment
You can update segment definitions with the Update Segment endpoint. In the example call to Update Segment below, the segment from the Get Segments example above ("id": "UUvyMc") is updated to include profiles who live within 20 miles of Columbus, Ohio ("postal_code": "43004"):

Request

curl --request PATCH \
 --url https://a.klaviyo.com/api/segments/id/ \
 --header 'Authorization: Klaviyo-API-Key your-private-api-key' \
 --header 'accept: application/json' \
 --header 'content-type: application/json' \
 --header 'revision: 2024-06-15' \
 --data '
{
"data": {
"type": "segment",
"id": "UUvyMc",
"attributes": {
"name": "Mint Vinyl Columbus Group",
"definition": {
"condition_groups": [
{
"conditions": [
{
"type": "profile-attribute",
"field": "location['city']",
"filter": {
"type": "string",
"operator": "equals",
"value": "Columbus"
}
},
{
"type": "profile-postal-code-distance",
"unit": "miles",
"filter": {
"type": "numeric",
"operator": "less-than",
"value": 20
},
"postal_code": "43004",
"country_code": "USA"
}
]
},
{
"conditions": [
{
"type": "profile-group-membership",
"is_member": true,
"group_ids": [
"YzykDM"
],
"timeframe_filter": null
}
]
}
]
}
}
}
}
'
Limitations
Maximum of 5 segments processed at a time.
Maximum of 100 segments created per day.
Condition types
You can create conditions by setting the type field to any of the condition types listed below (e.g., "type": "profile-attribute").

profile-group-membership
The following example is a segment condition that adds a profile to a segment if the profile has been added to the provided list in the last 10 days:

JSON

{
"type": "profile-group-membership",
"is_member": true,
"group_ids": [
"G2B2C2"
],
"timeframe_filter": {
"type": "date",
"operator": "in-the-last",
"quantity": 10,
"unit": "day"
}
}

is_member
Whether or not a profile belongs to a list (true or false).
group_ids
An array of list IDs (only lists are supported). Note that, at this time, group_ids can only contain 1 list ID.
timeframe_filter
The time when the profile was added to the list, if is_member is true.
profile-marketing-consent
To match the set of profiles that can receive email marketing because they subscribed and double opted-in:

JSON

{
"type": "profile-marketing-consent",
"consent": {
"channel": "email",
"can_receive_marketing": true,
"consent_status": {
"subscription": "subscribed",
"filters": [
{
"field": "is_double_optin",
"filter": {
"type": "boolean",
"operator": "equals",
"value": true
}
}
]
}
}
}

To match the set of profiles that can receive SMS marketing:

JSON

{
"type": "profile-marketing-consent",
"consent": {
"channel": "sms",
"can_receive_marketing": true,
"consent_status": {
"subscription": "any"
}
}
}
consent

A state for checking whether or not someone can receive email, sms, or push marketing. Contains the following:

channel

The channel, i.e., "email," "sms," or "push."

can_receive_marketing

Whether or not the profile can receive marketing.

consent_status

Contains the following:

subscription

The subscription status, e.g., any, subscribed, unsubscribed, never_subscribed.

filters

An object for setting filters (see API reference documentation).

profile-metric
The example below is a condition that adds profiles to the segment that have purchases adding up to more than 200 dollars total (using the Fulfilled Order metric) after April 1, 2017:

JSON

{
"type": "profile-metric",
"metric_id": "S4SFhi",
"measurement": "count",
"measurement_filter": {
"type": "numeric",
"operator": "greater-than",
"value": 200,
},
"timeframe_filter": {
"type": "date",
"operator": "after",
"value": "2017-04-01T00:00:00",
},
"metric_filters": [
{
"property": "country",
"filter": {
"type": "string",
"operator": "equals",
"value": "United States"
}
}
]
}
metric_id

The ID of the metric you will segment on, e.g., a metric ID with the name "Placed Order.”
measurement

One of the following:

count

The frequency of a metric for a profile, i.e., an event (e.g., the number of times a Clicked Email event occurred).

sum

The sum of event values. Should only be used for metrics where a value is being set. For example, the sum of a profile’s order values for the \_Placed Order \_metric.

measurement_filter

type: numeric

operator

Includes equals, greater-than,greater-than-or-equal,and so on.

value

The number of the value.

timeframe_filter

The filter for setting the timeframe in which a metric has been used to define a profile event (e.g., "in the last 1 month," "over all time," "greater than 6 days ago.")

type

Additional fields such as the operator and date depend on the timeframe type. See API reference documentation for more information.

profile-postal-code-distance
To match the set of profiles that live greater than 10 miles away from the 02141 zip code in the United States, you would use the following condition:

JSON

{
"type": "profile-postal-code-distance",
"country_code": "USA",
"postal_code": "02141",
"unit": "miles",
"filter": {
"type": "numeric",
"operator": "less-than",
"value": 10
}
}
country_code

The 3-digit ISO code for a country, e.g., USA.

postal_code

The 5-digit postal code, e.g., "12345".

unit

The unit for measuring distance, i.e., "kilometers" or "miles."

filter

type: "numeric"

operator

Includes "less-than" and "greater-than".

value

The number of the value, e.g., 5.

profile-predictive-analytics
📘
There is a certain set of requirements for your account to track predictive analytics properties beyond predicted gender.

To match the set of profiles with an average order value (AOV) greater than or equal to $100 you would use the following condition:

JSON

{
"type": "profile-predictive-analytics",
"dimension": "average_order_value",
"filter": {
"type": "numeric",
"operator": "greater-than-or-equal",
"value": 100
}
}
Predicted gender
dimension: "predicted_gender"
filter: "likely_male" | "likely_female" | "uncertain"
Other
dimension: e.g. "average_order_value", "predicted_clv", etc.
filter
type: "numeric"
operator: "equals", "greater-than" …
profile-property
The example below is a condition which will match all profiles with a hotmail email address:

JSON

{
"type": "profile-property",
"property": "email",
"filter": {
"type": "string",
"operator": "ends-with",
"value": "@hotmail.com"
}
}

property
The name of the profile property, e.g. created, location['city'] properties['preferences'].
filter
Available filters depend on the field type provided.
profile-region
To match the set of profiles that are in the European Union:

JSON

{
"type": "profile-region",
"in_region": true,
"region_id": "european_union"
}
in_region

Whether or not a profile lives in the specified region (true or false).

region

The profile region. Supported options include "european_union" or "united_states."
