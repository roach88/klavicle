import os

from dotenv import load_dotenv
from klaviyo_api import KlaviyoAPI


def test_sdk():
    """Test the SDK's available methods and types."""
    load_dotenv()
    api_key = os.getenv("KLAVIYO_API_KEY")
    if not api_key:
        print("Error: KLAVIYO_API_KEY environment variable not set")
        return

    client = KlaviyoAPI(api_key)

    # Print available methods for each API
    print("\nProfiles API methods:")
    print([method for method in dir(client.Profiles) if not method.startswith("_")])

    print("\nLists API methods:")
    print([method for method in dir(client.Lists) if not method.startswith("_")])

    print("\nSegments API methods:")
    print([method for method in dir(client.Segments) if not method.startswith("_")])

    print("\nTags API methods:")
    print([method for method in dir(client.Tags) if not method.startswith("_")])


if __name__ == "__main__":
    test_sdk()
