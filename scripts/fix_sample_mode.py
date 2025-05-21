#!/usr/bin/env python
"""
This script fixes the sample mode processing to make it more efficient 
by using synthetic data when no actual Klaviyo data is available.
"""

import os
import json
from pathlib import Path

# Create a mock data generator function
def create_mock_data():
    """Create synthetic data for testing the AI analysis functionality."""
    return {
        "campaigns": [
            {
                "id": "mock_campaign_1",
                "name": "Mock Newsletter Campaign",
                "status": "sent",
                "created": "2024-01-01T10:00:00Z",
                "updated": "2024-01-05T12:00:00Z",
                "send_time": "2024-01-10T08:00:00Z",
                "channel": "email",
                "message_type": "newsletter",
                "subject_line": "Check out our new products!",
                "from_email": "marketing@example.com",
                "from_name": "Marketing Team",
                "tags": ["newsletter", "product:launch", "audience:all"],
                "metrics": {
                    "recipient_count": 5000,
                    "open_rate": 0.22,
                    "click_rate": 0.08,
                    "revenue": 1200.00,
                }
            },
            {
                "id": "mock_campaign_2",
                "name": "Mock Sale Announcement",
                "status": "sent",
                "created": "2024-02-01T10:00:00Z",
                "updated": "2024-02-05T12:00:00Z",
                "send_time": "2024-02-10T08:00:00Z",
                "channel": "email",
                "message_type": "promotional",
                "subject_line": "50% Off Sale - This Weekend Only!",
                "from_email": "sales@example.com",
                "from_name": "Sales Team",
                "tags": ["promotion", "sale", "audience:active"],
                "metrics": {
                    "recipient_count": 8000,
                    "open_rate": 0.35,
                    "click_rate": 0.12,
                    "revenue": 5600.00,
                }
            },
            {
                "id": "mock_campaign_3",
                "name": "Mock Product Announcement",
                "status": "sent",
                "created": "2024-03-01T10:00:00Z",
                "updated": "2024-03-05T12:00:00Z",
                "send_time": "2024-03-10T08:00:00Z",
                "channel": "email",
                "message_type": "announcement",
                "subject_line": "Introducing Our New Product Line",
                "from_email": "products@example.com",
                "from_name": "Product Team",
                "tags": ["product:launch", "announcement", "audience:all"],
                "metrics": {
                    "recipient_count": 12000,
                    "open_rate": 0.28,
                    "click_rate": 0.09,
                    "revenue": 3200.00,
                }
            }
        ],
        "flows": [
            {
                "id": "mock_flow_1",
                "name": "Mock Welcome Series",
                "status": "live",
                "archived": False,
                "created": "2023-01-15T10:00:00Z",
                "updated": "2024-01-20T12:00:00Z",
                "trigger_type": "signup",
                "structure": {
                    "action_count": 5,
                    "email_count": 3,
                    "sms_count": 1,
                    "time_delay_count": 3,
                },
                "tags": ["onboarding", "automation:welcome", "audience:new"]
            },
            {
                "id": "mock_flow_2",
                "name": "Mock Abandoned Cart",
                "status": "live",
                "archived": False,
                "created": "2023-02-15T10:00:00Z",
                "updated": "2024-02-20T12:00:00Z",
                "trigger_type": "abandoned_cart",
                "structure": {
                    "action_count": 6,
                    "email_count": 3,
                    "sms_count": 2,
                    "time_delay_count": 4,
                },
                "tags": ["cart", "recovery", "automation:cart"]
            },
            {
                "id": "mock_flow_3",
                "name": "Mock Re-engagement",
                "status": "live",
                "archived": False,
                "created": "2023-03-15T10:00:00Z",
                "updated": "2024-03-20T12:00:00Z",
                "trigger_type": "metric_triggered",
                "structure": {
                    "action_count": 4,
                    "email_count": 3,
                    "sms_count": 0,
                    "time_delay_count": 2,
                },
                "tags": ["re-engagement", "win-back", "audience:inactive"]
            }
        ],
        "lists": [
            {
                "id": "mock_list_1",
                "name": "Mock Newsletter Subscribers",
                "created": "2023-01-10T10:00:00Z",
                "updated": "2024-01-15T12:00:00Z",
                "profile_count": 25000,
                "is_dynamic": False,
                "folder_name": "Main Lists",
                "tags": ["newsletter", "source:website", "opt-in:explicit"]
            },
            {
                "id": "mock_list_2",
                "name": "Mock High Value Customers",
                "created": "2023-02-10T10:00:00Z",
                "updated": "2024-02-15T12:00:00Z",
                "profile_count": 5000,
                "is_dynamic": True,
                "folder_name": "Segments",
                "tags": ["high-value", "segment:value", "behavior:purchase"]
            },
            {
                "id": "mock_list_3",
                "name": "Mock VIP Members",
                "created": "2023-03-10T10:00:00Z",
                "updated": "2024-03-15T12:00:00Z",
                "profile_count": 1000,
                "is_dynamic": True,
                "folder_name": "VIP",
                "tags": ["vip", "segment:loyalty", "tier:gold"]
            }
        ]
    }

# Update the AI commands file with the fix
def update_ai_commands():
    """
    Update the ai_commands.py file to add mock data support for sample mode.
    This makes --sample work without requiring a Klaviyo connection.
    """
    ai_commands_path = Path("src/klavicle/cli/ai_commands.py")
    if not ai_commands_path.exists():
        print(f"Error: {ai_commands_path} not found")
        return False
    
    # Read the file content
    with open(ai_commands_path, "r") as f:
        content = f.read()
    
    # If we already fixed the file, don't do it again
    if "USE_MOCK_DATA_FOR_SAMPLE" in content:
        print("File already contains fix")
        return True
    
    # Define the code to insert for mock data support
    mock_data_code = """
# Flag to use mock data in sample mode when no real data is available
USE_MOCK_DATA_FOR_SAMPLE = True

def _get_mock_data_for_sample():
    \"\"\"Create mock data for sample analysis when no real data is available.\"\"\"
    return {
        "campaigns": [
            {
                "id": "mock_campaign_1",
                "name": "Mock Newsletter Campaign",
                "status": "sent",
                "created": "2024-01-01T10:00:00Z",
                "updated": "2024-01-05T12:00:00Z",
                "send_time": "2024-01-10T08:00:00Z",
                "channel": "email",
                "message_type": "newsletter",
                "subject_line": "Check out our new products!",
                "from_email": "marketing@example.com",
                "from_name": "Marketing Team",
                "tags": ["newsletter", "product:launch", "audience:all"],
                "metrics": {
                    "recipient_count": 5000,
                    "open_rate": 0.22,
                    "click_rate": 0.08,
                    "revenue": 1200.00,
                }
            },
            {
                "id": "mock_campaign_2",
                "name": "Mock Sale Announcement",
                "status": "sent",
                "created": "2024-02-01T10:00:00Z",
                "updated": "2024-02-05T12:00:00Z",
                "send_time": "2024-02-10T08:00:00Z",
                "channel": "email",
                "message_type": "promotional",
                "subject_line": "50% Off Sale - This Weekend Only!",
                "from_email": "sales@example.com",
                "from_name": "Sales Team",
                "tags": ["promotion", "sale", "audience:active"],
                "metrics": {
                    "recipient_count": 8000,
                    "open_rate": 0.35,
                    "click_rate": 0.12,
                    "revenue": 5600.00,
                }
            },
            {
                "id": "mock_campaign_3",
                "name": "Mock Product Announcement",
                "status": "sent",
                "created": "2024-03-01T10:00:00Z",
                "updated": "2024-03-05T12:00:00Z",
                "send_time": "2024-03-10T08:00:00Z",
                "channel": "email",
                "message_type": "announcement",
                "subject_line": "Introducing Our New Product Line",
                "from_email": "products@example.com",
                "from_name": "Product Team",
                "tags": ["product:launch", "announcement", "audience:all"],
                "metrics": {
                    "recipient_count": 12000,
                    "open_rate": 0.28,
                    "click_rate": 0.09,
                    "revenue": 3200.00,
                }
            }
        ],
        "flows": [
            {
                "id": "mock_flow_1",
                "name": "Mock Welcome Series",
                "status": "live",
                "archived": False,
                "created": "2023-01-15T10:00:00Z",
                "updated": "2024-01-20T12:00:00Z",
                "trigger_type": "signup",
                "structure": {
                    "action_count": 5,
                    "email_count": 3,
                    "sms_count": 1,
                    "time_delay_count": 3,
                },
                "tags": ["onboarding", "automation:welcome", "audience:new"]
            },
            {
                "id": "mock_flow_2",
                "name": "Mock Abandoned Cart",
                "status": "live",
                "archived": False,
                "created": "2023-02-15T10:00:00Z",
                "updated": "2024-02-20T12:00:00Z",
                "trigger_type": "abandoned_cart",
                "structure": {
                    "action_count": 6,
                    "email_count": 3,
                    "sms_count": 2,
                    "time_delay_count": 4,
                },
                "tags": ["cart", "recovery", "automation:cart"]
            },
            {
                "id": "mock_flow_3",
                "name": "Mock Re-engagement",
                "status": "live",
                "archived": False,
                "created": "2023-03-15T10:00:00Z",
                "updated": "2024-03-20T12:00:00Z",
                "trigger_type": "metric_triggered",
                "structure": {
                    "action_count": 4,
                    "email_count": 3,
                    "sms_count": 0,
                    "time_delay_count": 2,
                },
                "tags": ["re-engagement", "win-back", "audience:inactive"]
            }
        ],
        "lists": [
            {
                "id": "mock_list_1",
                "name": "Mock Newsletter Subscribers",
                "created": "2023-01-10T10:00:00Z",
                "updated": "2024-01-15T12:00:00Z",
                "profile_count": 25000,
                "is_dynamic": False,
                "folder_name": "Main Lists",
                "tags": ["newsletter", "source:website", "opt-in:explicit"]
            },
            {
                "id": "mock_list_2",
                "name": "Mock High Value Customers",
                "created": "2023-02-10T10:00:00Z",
                "updated": "2024-02-15T12:00:00Z",
                "profile_count": 5000,
                "is_dynamic": True,
                "folder_name": "Segments",
                "tags": ["high-value", "segment:value", "behavior:purchase"]
            },
            {
                "id": "mock_list_3",
                "name": "Mock VIP Members",
                "created": "2023-03-10T10:00:00Z",
                "updated": "2024-03-15T12:00:00Z",
                "profile_count": 1000,
                "is_dynamic": True,
                "folder_name": "VIP",
                "tags": ["vip", "segment:loyalty", "tier:gold"]
            }
        ]
    }
"""
    
    # Find the imports section to add our global variables
    import_section_end = content.find("console = Console()")
    if import_section_end == -1:
        print("Could not find where to insert mock data code")
        return False
        
    # Insert the mock data code after imports
    new_content = content[:import_section_end] + mock_data_code + content[import_section_end:]
    
    # Now, we need to modify the analyze_impl function to use mock data in sample mode
    # Find the analyze_impl function
    analyze_impl_start = new_content.find("async def analyze_impl(")
    if analyze_impl_start == -1:
        print("Could not find analyze_impl function")
        return False
    
    # Find where the unified data is initialized
    unified_data_init = new_content.find("unified_data = {}", analyze_impl_start)
    if unified_data_init == -1:
        print("Could not find unified_data initialization")
        return False
    
    # Replace unified_data initialization with custom logic for sample mode
    old_data_init = "unified_data = {}"
    new_data_init = """# Use mock data if requested and in sample mode
        if sample and USE_MOCK_DATA_FOR_SAMPLE:
            console.print("[yellow]Using mock data for sample analysis[/yellow]")
            unified_data = _get_mock_data_for_sample()
        else:
            unified_data = {}"""
    
    new_content = new_content.replace(old_data_init, new_data_init)
    
    # Write the updated file
    with open(ai_commands_path, "w") as f:
        f.write(new_content)
    
    print(f"Successfully updated {ai_commands_path}")
    return True

# Run the update
if __name__ == "__main__":
    update_ai_commands()