Before you begin
Check out our general API overview to make sure you’re ready to get started with specific endpoints.

A flow is a sequence of automated actions that is triggered when a person performs a specific action. These automated actions can include pre-configured email and SMS messages. For example, you can set up a welcome series flow to message profiles after they have joined a mailing list. You can also add time delays between actions in your flow. For example, in an abandoned cart flow, if a person fails to check out their cart in 4 hours, they will receive an email notification.

A flow action is an action that triggers when a flow’s condition has been met. For example, in an abandoned cart flow, Send Email is the flow action that sends out a message reminding a person to complete their purchase.

Our Flows API contains the following endpoint categories to support flows:

Flows endpoints for fetching flows or updating flow statuses.
Relationships endpoints for accessing a list of related objects for a specific flow.
📘
Flows are not the same as campaigns, which are one-time scheduled actions (see our Campaigns API overview).

Use cases
Here are some example use cases supported by the Flows API:

Get all flow actions for a specific flow (e.g., Send Email and Time Delay flow actions for an abandoned cart flow).
Fetch and update a flow’s status (i.e., live, manual, or draft).
Retrieve messages for email and SMS flow actions.
Get an email template associated with a flow message.
Data model
A flow has the following:

id

The flow id.

attributes

name

The name of the flow.

status

The status of the flow (i.e., “draft,” “manual,” “live,” or “archived”).

archived

A boolean indicating whether or not the flow has been archived.

created

The date the flow was created.

updated

The date the flow was last updated.

trigger_type

The type of trigger. This value is typically the name of a metric - for example, “Added to List” for a flow with an Added to List trigger, or “Unconfigured” if the flow is in Draft status.

relationships

This object contains related resources, i.e., flow actions and tags. Learn more about relationships.

flow-actions

Contains the flow action(s) associated with the flow (see Flow actions).

tags

Contains the tag(s) associated with the flow.

Here's an example of a Birthday flow with a date-based trigger type:

JSON

{
    "type": "flow",
    "id": "RLmyME",
    "attributes": {
        "name": "Happy Birthday - Standard (Email & SMS)",
        "status": "manual",
        "archived": false,
        "created": "2024-02-22T20:24:32+00:00",
        "updated": "2024-02-22T20:24:34+00:00",
        "trigger_type": "Date Based"
    },
    "relationships": {
        "flow-actions": {
            "links": {
                "self": "https://a.klaviyo.com/api/flows/RLmyME/relationships/flow-actions/",
                "related": "https://a.klaviyo.com/api/flows/RLmyME/flow-actions/"
            }
        },
        "tags": {
            "links": {
                "self": "https://a.klaviyo.com/api/flows/RLmyME/relationships/tags/",
                "related": "https://a.klaviyo.com/api/flows/RLmyME/tags/"
            }
        }
    },
    "links": {
        "self": "https://a.klaviyo.com/api/flows/RLmyME/"
    }
},
View your flow JSON in Klaviyo
We’ve added a way for you to view and copy the JSON for your flows in the Klaviyo app.

Navigate to Flows.
Click on a flow.
Delete /edit and append .json to the end of the URL.
The JSON should display for your flow as in the example below.


Get Flow(s)
You can utilize Get Flow or Get Flows endpoints to pull in particular flow data, for example, flows in draft status. When making a Get Flow(s) request, here’s an example of how a Welcome Series flow might look in the response:

Request
Response

curl --request GET \
     --url https://a.klaviyo.com/api/flows/ \
     --header 'Authorization: Klaviyo-API-Key your-private-api-key' \
     --header 'accept: application/json' \
     --header 'revision: 2024-02-15'
📘
It's important to keep your private API key a secret and never use it with our client endpoints. Not sure how to find your private API key? Locate your API credentials in Klaviyo.

Flow actions
A flow action’s data structure depends on the flow action type. For example, a Send Email flow action will contain options for tracking, sending, and rendering the email. A Time Delay flow action will contain settings including the delay’s length in seconds.

A flow action has the following:

id

The flow action id.

attributes

action_type

The type of flow action (e.g., "SEND_EMAIL").

status

The status of the flow action (i.e., "draft", "manual", or "live").

created

The date that the flow action was created.

updated

The date that the flow action was last updated.

settings

Options needed for setting the flow action (e.g., delay_seconds for setting a time delay).

A messaging flow action has the following:

tracking_options

An object containing tracking option(s) shared by email and SMS messages:

is_add_utm

Indicates if the email or SMS needs UTM parameters.

utm_params

An array of objects representing the UTM parameters. If is_add_utm is true and the list is empty, company defaults will be used.

Email campaigns have the following additional tracking options:

is_tracking_clicks

Whether the email is tracking click events (defaults to true).

is_tracking_opens

Whether the email is tracking open events (defaults to true).

send_options

An object containing tracking option(s) shared by email and SMS messages:

use_smart_sending (default)

A boolean option to use smart sending for your email or SMS message (defaults to true). Smart sending skips recipients who have already received an email or SMS within a designated time frame.

render_options

An object containing additional options for rendering the message:

shorten_links

A boolean option that allows you to shorten links in the message.

add_org_prefix

A boolean option that allows you to add an organizational prefix to the beginning of the message to identify your company as the sender.

add_info_link

A boolean option that allows you to add a link to your custom company information page to the message.

add_opt_out_language

A boolean option that allows you to include a phrase at the end of the message with SMS opt-out information.

A flow action has the following related resources:

flow

The flow that contains the flow action.

flow-message

The flow message which contains message content for the flow action, if applicable. For example, email content for a Send Email flow action.

Get flow actions for a flow
You may want to retrieve specific data from flow actions for a given flow, for example, the time delay set for an abandoned cart flow. To retrieve flow actions for a given flow, call the Get Flow Flow Actions endpoint with a flow ID.

Here’s an example of a Send Email flow action retrieved from the Welcome Series flow example:

JSON

{
    "type": "flow-action",
    "id": "50516373",
    "attributes": {
        "action_type": "SEND_EMAIL",
        "status": "draft",
        "created": "2023-07-19T17:43:52+00:00",
        "updated": "2023-07-19T17:43:53+00:00",
        "settings": {},
        "tracking_options": {
            "add_utm": false,
            "utm_params": [],
            "is_tracking_opens": true,
            "is_tracking_clicks": true
        },
        "send_options": {
            "use_smart_sending": false,
            "is_transactional": false
        },
        "render_options": null
    },
    "relationships": {
        "flow": {
            "links": {
                "self": "https://a.klaviyo.com/api/flow-actions/50516373/relationships/flow/",
                "related": "https://a.klaviyo.com/api/flow-actions/50516373/flow/"
            }
        },
        "flow-messages": {
            "links": {
                "self": "https://a.klaviyo.com/api/flow-actions/50516373/relationships/flow-messages/",
                "related": "https://a.klaviyo.com/api/flow-actions/50516373/flow-messages/"
            }
        }
    },
    "links": {
        "self": "https://a.klaviyo.com/api/flow-actions/50516373/"
    }
},

Get messages for a flow action
You can retrieve flow action messages to access message data such as a message’s sending address, or when a flow message was last updated. In addition to fetching message content and activity, you can retrieve the flow action and/or email template associated with the message.

You can fetch a flow message given a flow action ID using the Get Flow Action Messages endpoint. Here’s an example of what a Send Email message from the Welcome Series flow would look like:

Request
Response

curl --request GET \
     --url 'https://a.klaviyo.com/api/flow-actions/50516373/flow-messages/
     --header 'Authorization: Klaviyo-API-Key your-private-api-key' \
     --header 'accept: application/json' \
     --header 'revision: 2024-02-15'
Get template for flow message
The Relationships endpoints that exist within the Flows API are useful for retrieving resources connected to flow-related objects (such as a flow message associated with a flow action).

Get Flow Message Template allows you to fetch an HTML template associated with a flow action’s message. For example, you might want to use the template ID from a Get Flow Message Template response to programmatically update the template used by the flow message (i.e., Update Template).

You can fetch a flow message’s template using the flow message ID related to a specific flow action, for example, Send Email. When making a Get Flow Message Template request, here’s an example of how the response could look for a Welcome Series flow:

Request
Response

curl --request GET \
     --url https://a.klaviyo.com/api/flow-messages/TphFtt/template/ \
     --header 'Authorization: Klaviyo-API-Key your-private-api-key' \
     --header 'accept: application/json' \
     --header 'revision: 2024-02-15'
Querying flows
Querying flows with the Get Flows endpoint can help you achieve things like retrieving a list of flows in draft status. Check out the supported query parameters below and test them out with our latest Postman collection. Note that support for given operators and fields is endpoint-specific. Review the API reference documentation for more information on allowed fields and query operators.

Parameter	Description	Query example
filter	Retrieve a subset of flows, e.g., flows that trigger when a profile is added to a list. Learn about the filter query parameter.	GET /api/flows?filter=and(equals(trigger_type,"Added to List")
sort	Sort flows, e.g., by updated datetime in ascending order (oldest to newest). Learn about the sort query parameter.	GET /api/flows?sort=-updated
fields	Request for only specified flow data (e.g., only return the status field for each flow action in the response). You can also request for only specified related resource data. Learn more about sparse fieldsets.	GET /api/flows?include=flow-action&fields[flow-action]=status
include	Include related resources in the response, e.g., flow actions. Learn about the include query parameter.	GET /api/flows?include=flow-actions
View your flow JSON in Klaviyo
We’ve added a way for you to view and copy the JSON for your flows in the Klaviyo app.

Navigate to Flows.
Click on a flow to edit it.
Change the URL in your browser from /flow/abc123/edit to /flow/abc123.json.
The JSON should display for your flow as in the example below:

JSON

{
  "data": {
    "type": "flow",
    "id": "Sdq3ii",
    "attributes": {
      "name": "Abandoned Cart",
      "status": "live",
      "archived": false,
      "created": "2024-04-30T18:29:06+00:00",
      "updated": "2024-04-30T18:29:07+00:00",
      "triggerType": "Metric",
      "definition": {
        "triggers": [
          {
            "type": "metric",
            "id": "TzAeur",
            "triggerFilter": null
          }
        ],
        "profileFilter": {
          "conditionGroups": [
            {
              "conditions": [
                {
                  "type": "profile-metric",
                  "metricId": "T3csdc",
                  "measurement": "count",
                  "measurementFilter": {
                    "type": "numeric",
                    "operator": "equals",
                    "value": 0
                  },
                  "timeframeFilter": {
                    "type": "date",
                    "operator": "flow-start"
                  },
                  "metricFilters": null
                }
              ]
            }
          ]
        },
        "actions": [
          {
            "id": "12777480",
            "type": "conditional-split",
            "links": {
              "nextIfTrue": "12777476",
              "nextIfFalse": null
            },
            "data": {
              "profileFilter": {
                "conditionGroups": [
                  {
                    "conditions": [
                      {
                        "type": "profile-group-membership",
                        "isMember": true,
                        "groupIds": [
                          "QWwLBF"
                        ],
                        "timeframeFilter": null
                      }
                    ]
                  }
                ]
              }
            }
          },
          {
            "id": "12777476",
            "type": "time-delay",
            "links": {
              "next": "12777506"
            },
            "data": {
              "unit": "hours",
              "value": 4,
              "secondaryValue": 0,
              "timezone": "profile",
              "delayUntilTime": null,
              "delayUntilWeekdays": [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday"
              ]
            }
          },
          {
            "id": "12777506",
            "type": "conditional-split",
            "links": {
              "nextIfTrue": "12777474",
              "nextIfFalse": "12777519"
            },
            "data": {
              "profileFilter": {
                "conditionGroups": [
                  {
                    "conditions": [
                      {
                        "type": "profile-sample",
                        "percentage": 50
                      }
                    ]
                  }
                ]
              }
            }
          },
          {
            "id": "12777474",
            "type": "send-email",
            "links": {
              "next": null
            },
            "data": {
              "message": {
                "fromEmail": "example@test.com",
                "fromLabel": "Klaviyo",
                "replyToEmail": null,
                "ccEmail": null,
                "bccEmail": null,
                "subjectLine": "It looks like you left something behind...",
                "previewText": "",
                "templateId": "Xw4rum",
                "smartSendingEnabled": false,
                "transactional": false,
                "addTrackingParams": false,
                "customTrackingParams": null,
                "additionalFilters": null,
                "name": "Abandoned Cart: Email 1",
                "id": "TVcEtp"
              },
              "status": "live"
            }
          },
          {
            "id": "12777519",
            "type": "send-sms",
            "links": {
              "next": null
            },
            "data": {
              "message": {
                "body": "Forget something?",
                "imageId": null,
                "dynamicImage": null,
                "shortenLinks": true,
                "includeContactCard": false,
                "addOrgPrefix": true,
                "addInfoLink": true,
                "addOptOutLanguage": false,
                "smartSendingEnabled": true,
                "smsQuietHoursEnabled": true,
                "transactional": false,
                "addTrackingParams": false,
                "customTrackingParams": null,
                "additionalFilters": null,
                "name": "SMS #1",
                "id": "SBXhJW"
              },
              "status": "live"
            }
          }
        ],
        "entryActionId": "12777480"
      }
    },
    "relationships": {
      "flowActions": {
        "links": {
          "self": "https://www.klaviyo.com/ux-api/flows/Sdq3ii/relationships/flow-actions/",
          "related": "https://www.klaviyo.com/ux-api/flows/Sdq3ii/flow-actions/"
        }
      },
      "tags": {
        "links": {
          "self": "https://www.klaviyo.com/ux-api/flows/Sdq3ii/relationships/tags/",
          "related": "https://www.klaviyo.com/ux-api/flows/Sdq3ii/tags/"
        }
      }
    },
    "links": {
      "self": "https://www.klaviyo.com/ux-api/flows/Sdq3ii/"
    }
  },
  "links": {
    "self": "https://www.klaviyo.com/ux-api/flows/Sdq3ii?additional-fields[flow]=definition"
  }
}
