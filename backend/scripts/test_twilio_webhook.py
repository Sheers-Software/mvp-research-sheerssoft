import os
import requests
from twilio.request_validator import RequestValidator

# Need to match the token set in demo config or `.env.demo`
# docker-compose is running with the root env unless overridden. Let's assume it has no token or "dev"
AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")

# The exact URL the validator expects. 
URL = "http://localhost:8000/api/v1/webhook/twilio/whatsapp"

payload = {
    "From": "whatsapp:+1234567890",
    "To": "whatsapp:+0987654321",
    "Body": "Hello from manual test script",
    "ProfileName": "TestGuest"
}

# If auth token exists (it might not be in demo if not set), we sign it
headers = {
    "Content-Type": "application/x-www-form-urlencoded"
}

if AUTH_TOKEN:
    validator = RequestValidator(AUTH_TOKEN)
    signature = validator.compute_signature(URL, payload)
    headers["X-Twilio-Signature"] = signature

print(f"Sending POST to {URL}")
response = requests.post(URL, data=payload, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.text}")
