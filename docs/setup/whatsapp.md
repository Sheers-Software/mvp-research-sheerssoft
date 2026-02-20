# WhatsApp Business API Setup

## 1. Create a Meta Business Account
1. Go to [business.facebook.com](https://business.facebook.com)
2. Create or select your business account

## 2. Create a WhatsApp Business App
1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create a new app → Select "Business" type
3. Add the "WhatsApp" product

## 3. Get Your Credentials
From the WhatsApp dashboard:

```env
WHATSAPP_API_TOKEN=<System User Token with whatsapp_business_messaging permission>
WHATSAPP_PHONE_NUMBER_ID=<From the WhatsApp > API Setup page>
WHATSAPP_APP_SECRET=<App Settings > Basic > App Secret>
WHATSAPP_VERIFY_TOKEN=<Any string you choose for webhook verification>
```

## 4. Configure Webhook
- URL: `https://your-domain.com/api/v1/webhooks/whatsapp`
- Verify Token: same as `WHATSAPP_VERIFY_TOKEN`
- Subscribe to: `messages`

## 5. Test
Send a message to your WhatsApp Business number. It should appear in the dashboard conversations.

## Mock Mode
If credentials are not set, WhatsApp messages are logged to console (dev) or stored in Redis (demo).
