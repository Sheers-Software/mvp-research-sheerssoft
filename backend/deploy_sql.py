import requests
import sys

token = "sbp_1d33ab05d6594734b1e2e4f8a5e8b79222e296d0"
project_ref = "ramenghkpvipxijhfptp"

url = f"https://api.supabase.com/v1/projects/{project_ref}/query"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

try:
    with open(r"C:\Users\abasy\.gemini\antigravity\brain\be279420-4932-449a-b81c-7466a5c5d062\manual_migration.sql", "r", encoding="utf-8") as f:
        sql = f.read()
except Exception as e:
    print(f"Missing sql file: {e}")
    sys.exit(1)

print("Shipping migrations to Supabase via Management API...")
payload = {"query": sql}
response = requests.post(url, headers=headers, json=payload)

print(f"Status: {response.status_code}")
if response.status_code >= 400:
    print(f"Failed to execute migrations. Error:\n{response.text}")
    sys.exit(1)
else:
    print("Migration successfully applied!")
    # Optionally also print the response for any confirmations
    print(response.text)
