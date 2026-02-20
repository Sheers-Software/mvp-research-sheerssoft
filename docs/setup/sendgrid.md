# SendGrid Email Setup

## 1. Create a SendGrid Account
1. Go to [sendgrid.com](https://sendgrid.com) and sign up
2. Complete domain verification (Settings > Sender Authentication)

## 2. Create an API Key
1. Settings > API Keys > Create API Key
2. Select "Full Access" or restrict to "Mail Send" only

```env
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=concierge@yourdomain.com
```

## 3. Configure Inbound Parse (for receiving emails)
1. Settings > Inbound Parse > Add Host & URL
2. URL: `https://your-domain.com/api/v1/webhooks/email`
3. Check "POST the raw, full MIME message"

## 4. Event Webhook (for delivery tracking)
1. Settings > Mail Settings > Event Webhook
2. URL: `https://your-domain.com/api/v1/webhooks/email/events`
3. Enable: Delivered, Opened, Bounced, Spam Report

```env
SENDGRID_WEBHOOK_PUBLIC_KEY=<From Event Webhook settings, for signature verification>
```

## Mock Mode
If `SENDGRID_API_KEY` is not set, emails are logged to console (dev) or stored in Redis (demo).
