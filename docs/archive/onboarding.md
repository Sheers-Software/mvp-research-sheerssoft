# 🏨 Property Onboarding Guide

## 1. Prepare Property Configuration
Create a JSON file (e.g., `new_property.json`) with the property details:

```json
{
  "name": "Grand Hotel KL",
  "whatsapp_number": "60123456789",
  "notification_email": "reservations@grandhotel.com",
  "website_url": "https://grandhotel.com",
  "operating_hours": {
    "start": "09:00",
    "end": "18:00",
    "timezone": "Asia/Kuala_Lumpur"
  },
  "adr": 300.00,
  "ota_commission_pct": 18.00,
  "kb_documents": [
    {
      "doc_type": "rooms",
      "title": "Room Types",
      "content": "Description of rooms..."
    },
    {
      "doc_type": "faqs",
      "title": "Check-in Policy",
      "content": "Check-in at 3pm, check-out at 12pm."
    }
  ]
}
```

## 2. Run Onboarding Script
Run the script inside the backend container:

```bash
docker compose exec backend python -m scripts.onboard_property --file new_property.json
```

If successful, it will output:
`SUCCESS: Property 'Grand Hotel KL' onboarded with ID: <UUID>`

## 3. WhatsApp Integration
1.  Go to [Meta for Developers](https://developers.facebook.com/).
2.  Select the App and go to **WhatsApp > Configuration**.
3.  Edit **Callback URL**: `https://<your-api-domain>/api/v1/webhook/whatsapp`
4.  Verify Token: `nocturn_verify_token` (as set in `.env`).
5.  Subscribe to `messages` webhook field.

## 4. Updates & Management
To update property details or add more KB documents, edit the JSON file and run the script again. It will update the existing property record.
