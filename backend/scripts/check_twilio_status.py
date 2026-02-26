import os
import sys
from twilio.rest import Client


def check_status(sid: str):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")

    if not account_sid or not auth_token:
        print("Error: TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set as environment variables.")
        sys.exit(1)

    client = Client(account_sid, auth_token)

    try:
        message = client.messages(sid).fetch()
        print(f"SID: {sid}")
        print(f"Status: {message.status}")
        print(f"To: {message.to}")
        print(f"Error Code: {message.error_code}")
        print(f"Error Message: {message.error_message}")
        print(f"Direction: {message.direction}")
    except Exception as e:
        print(f"Error fetching SID {sid}: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_twilio_status.py <MessageSid> [<MessageSid2> ...]")
        sys.exit(1)

    for sid_arg in sys.argv[1:]:
        check_status(sid_arg)
        print("-" * 20)
