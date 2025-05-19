# Vinyl Me, Please Klaviyo Account Overview

## Tag Organization System

```mermaid
graph TD
    %% Main Tag Categories
    CategoryAnthology[Anthology Tags]
    CategoryShipping[Shipping Update Tags]
    CategoryBAU[Business As Usual Tags]
    CategoryProductReview[Product Review Tags]
    CategoryOther[Other Tags]

    %% Specific Tags
    Anthology[anthology]
    StaxAnthology[stax]
    WomenOfMotown[women of motown]
    GratefulDead[grateful dead]

    ShippingUpdate[shipping update]

    BAUBrowse[BAU Browse]
    BAUCheckout[BAU Checkout]

    ProductReview[product-review]

    SMS[sms]
    BCSubscribe[BC Subscribe]
    Renewals[renewals]
    Retention[retention]

    %% Connections
    CategoryAnthology --> Anthology
    CategoryAnthology --> StaxAnthology
    CategoryAnthology --> WomenOfMotown
    CategoryAnthology --> GratefulDead

    CategoryShipping --> ShippingUpdate

    CategoryBAU --> BAUBrowse
    CategoryBAU --> BAUCheckout

    CategoryProductReview --> ProductReview

    CategoryOther --> SMS
    CategoryOther --> BCSubscribe
    CategoryOther --> Renewals
    CategoryOther --> Retention
```

## Flow Analysis

```mermaid
graph TD
    %% Flow Types
    MetricTriggers[Metric Triggered Flows]
    ListTriggers[List Triggered Flows]
    Unconfigured[Unconfigured Flows]

    %% Main Flow Categories
    Abandoned[Abandoned Browsing & Cart Flows]
    WelcomeSeries[Welcome Series Flows]
    PostPurchase[Post Purchase Flows]
    ShippingUpdates[Shipping Update Flows]
    ThankYou[Thank You Flows]
    ProductReviews[Product Review Flows]
    Membership[Membership Flows]

    %% Stats for each category
    AbandonedStats["
      Abandoned Flows:
      • 8 active flows
      • Key tags: BAU Browse, BAU Checkout
      • Primarily Metric triggers
    "]

    WelcomeStats["
      Welcome Series:
      • 11 active flows
      • Both Member and new customer series
      • Primarily List triggers
    "]

    PostPurchaseStats["
      Post Purchase Flows:
      • 12 anthology-specific flows
      • All have anthology tag
      • Primarily Metric triggers
    "]

    ShippingStats["
      Shipping Update Flows:
      • 15 product-specific flows
      • All tagged with shipping update
      • All List triggers
    "]

    ThankYouStats["
      Thank You Flows:
      • 3 different flows (new/returning)
      • No tags used
      • All Metric triggers
    "]

    ProductReviewStats["
      Product Review Flows:
      • 2 flows for requesting reviews
      • Tagged with product-review
      • Metric triggers
    "]

    MembershipStats["
      Membership Flows:
      • 4 flows for member management
      • Includes winback and renewals
      • Mixed trigger types
    "]

    %% Connections
    MetricTriggers --> Abandoned
    MetricTriggers --> PostPurchase
    MetricTriggers --> ThankYou
    MetricTriggers --> ProductReviews

    ListTriggers --> WelcomeSeries
    ListTriggers --> ShippingUpdates
    ListTriggers --> Membership

    Unconfigured --> Membership

    Abandoned --> AbandonedStats
    WelcomeSeries --> WelcomeStats
    PostPurchase --> PostPurchaseStats
    ShippingUpdates --> ShippingStats
    ThankYou --> ThankYouStats
    ProductReviews --> ProductReviewStats
    Membership --> MembershipStats
```

## Flow Structure Analysis

```mermaid
flowchart TD
    %% Flow structure analysis
    FlowStructure["Flow Structure Analysis
    (Based on 91 flows)"]

    %% Trigger Types
    TriggerTypes["Trigger Distribution:
    - Metric Trigger: 46 flows (51%)
    - List Trigger: 42 flows (46%)
    - Unconfigured: 3 flows (3%)"]

    %% Email Statistics
    EmailStats["Email Usage:
    - Total emails in flows: 176
    - Average emails per flow: 1.93
    - Single email flows: 43 (47%)
    - Multiple email flows: 48 (53%)"]

    %% Delay Statistics
    DelayStats["Time Delay Usage:
    - Total delays in flows: 139
    - Average delays per flow: 1.53
    - No delay flows: 13 (14%)
    - Multiple delay flows: 58 (64%)"]

    %% SMS Statistics
    SMSStats["SMS Usage:
    - Total SMS in flows: 17
    - Only 6 flows use SMS (7%)
    - All SMS flows are draft templates"]

    %% Tag Statistics
    TagStats["Tag Usage:
    - Flows with tags: 47 (52%)
    - Flows without tags: 44 (48%)
    - Most common tag: anthology (12 flows)
    - Second most common: shipping update (15 flows)"]

    %% Status Distribution
    StatusStats["Flow Status:
    - Live flows: 23 (25%)
    - Manual flows: 41 (45%)
    - Draft flows: 27 (30%)"]

    %% Connections
    FlowStructure --> TriggerTypes
    FlowStructure --> EmailStats
    FlowStructure --> DelayStats
    FlowStructure --> SMSStats
    FlowStructure --> TagStats
    FlowStructure --> StatusStats
```

## Flow Trigger Relationships

```mermaid
graph TD
    %% Define trigger types
    MetricTrigger[Metric Triggers]
    ListTrigger[List Triggers]
    Unconfigured[Unconfigured Triggers]

    %% Define specific metric trigger types
    Browse["Browse Abandonment
    7 flows"]

    Cart["Cart/Checkout Abandonment
    4 flows"]

    Purchase["Post Purchase
    22 flows"]

    Review["Product Review
    2 flows"]

    ThankYou["Thank You
    3 flows"]

    %% Define specific list trigger types
    WelcomeSeries["Welcome Series
    10 flows"]

    ShippingUpdate["Shipping Updates
    15 flows"]

    MemberManagement["Member Management
    7 flows"]

    %% Define unconfigured triggers
    Renewal["Renewal Reminder
    1 flow"]

    UpdateAddress["Update Address
    1 flow"]

    Welcome["Welcome
    1 flow"]

    %% Connections
    MetricTrigger --> Browse
    MetricTrigger --> Cart
    MetricTrigger --> Purchase
    MetricTrigger --> Review
    MetricTrigger --> ThankYou

    ListTrigger --> WelcomeSeries
    ListTrigger --> ShippingUpdate
    ListTrigger --> MemberManagement

    Unconfigured --> Renewal
    Unconfigured --> UpdateAddress
    Unconfigured --> Welcome
```

## Data Flow Diagram

```mermaid
flowchart LR
    %% Major Data Sources
    Database[(Customer Database)]
    Website[Website Activity]
    ThirdParty[Third Party Sources]

    %% Klaviyo Lists
    NewSignups[New Signups List]
    Members[Members List]
    PastPurchasers[Past Purchasers List]
    ProductSpecific[Product-Specific Lists]

    %% Flow Triggers
    BrowseAbandon[Browse Abandonment]
    CartAbandon[Cart Abandonment]
    PurchaseEvent[Purchase Event]

    %% Email Types
    WelcomeEmails[Welcome Emails]
    ThankYouEmails[Thank You Emails]
    ShippingEmails[Shipping Update Emails]
    AbandonEmails[Abandonment Emails]
    AnthologyEmails[Anthology Welcome Emails]

    %% Data Flow
    Database --> NewSignups
    Database --> Members
    Database --> PastPurchasers
    Database --> ProductSpecific

    Website --> BrowseAbandon
    Website --> CartAbandon
    Website --> PurchaseEvent

    ThirdParty --> ProductSpecific

    NewSignups --> WelcomeEmails

    Members --> WelcomeEmails

    PastPurchasers --> ThankYouEmails

    ProductSpecific --> ShippingEmails
    ProductSpecific --> AnthologyEmails

    BrowseAbandon --> AbandonEmails
    CartAbandon --> AbandonEmails
    PurchaseEvent --> ThankYouEmails
    PurchaseEvent --> AnthologyEmails
```

## Key Metrics & Performance Analysis

```mermaid
graph TD
    %% Flow Performance Categories
    FlowTypes[Flow Types]

    %% Flow Categories
    Abandoned[Abandoned Cart & Browse]
    Welcome[Welcome Series]
    PostPurchase[Post Purchase]
    ShippingUpdates[Shipping Updates]

    %% Performance Metrics
    AbandonedMetrics["
      Abandoned Flow Metrics:
      • 7 Browse Abandonment flows
      • 4 Cart Abandonment flows
      • Avg. emails: 3.2 per flow
      • Used for: Recovery, engagement
    "]

    WelcomeMetrics["
      Welcome Series Metrics:
      • 10 active welcome flows
      • Avg. emails: 3.4 per flow
      • Used for: Onboarding new members
      • Segment-specific welcomes
    "]

    PurchaseMetrics["
      Post Purchase Metrics:
      • 22 purchase-specific flows
      • 12 anthology-specific
      • Avg. emails: 1.5 per flow
      • Used for: Cross-sell, reviews
    "]

    ShippingMetrics["
      Shipping Update Metrics:
      • 15 product-specific flows
      • Single email per flow
      • Used for: Order status updates
      • All manually triggered
    "]

    %% Connections
    FlowTypes --> Abandoned
    FlowTypes --> Welcome
    FlowTypes --> PostPurchase
    FlowTypes --> ShippingUpdates

    Abandoned --> AbandonedMetrics
    Welcome --> WelcomeMetrics
    PostPurchase --> PurchaseMetrics
    ShippingUpdates --> ShippingMetrics
```

## Recommended Improvements

```mermaid
graph TD
    %% Areas for Improvement
    Improvements[Klaviyo Improvement Areas]

    %% Specific Improvement Categories
    TagSystem[Tag System Improvements]
    FlowConsolidation[Flow Consolidation]
    DraftCleanup[Draft Flow Cleanup]
    FlowUpgrade[Flow Upgrade]

    %% Detailed Recommendations
    TagRecs["
      Tag System:
      • Add tags to 44 untagged flows
      • Create consistent tag naming
      • Develop tag hierarchy
      • Document tag purpose
    "]

    ConsolidationRecs["
      Flow Consolidation:
      • Combine 15 shipping update flows
      • Merge similar welcome series
      • Standardize abandoned browse flows
      • Template-based approach
    "]

    CleanupRecs["
      Draft Cleanup:
      • Review 27 draft flows
      • Delete or activate 17 old drafts
      • Remove clone templates
      • Document remaining drafts
    "]

    UpgradeRecs["
      Flow Upgrading:
      • Add SMS to key flows
      • Update aging content
      • Refresh visuals
      • A/B test critical flows
    "]

    %% Connections
    Improvements --> TagSystem
    Improvements --> FlowConsolidation
    Improvements --> DraftCleanup
    Improvements --> FlowUpgrade

    TagSystem --> TagRecs
    FlowConsolidation --> ConsolidationRecs
    DraftCleanup --> CleanupRecs
    FlowUpgrade --> UpgradeRecs
```
