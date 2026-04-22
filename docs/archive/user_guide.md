# 📋 Nocturn AI User Guide for Hotel Managers

## 1. Daily Workflow

### 📧 Morning Report (7:30 AM)
You will receive an email summarizing yesterday's performance:
- **Revenue Recovered**: Estimated value of bookings captured.
- **After-Hours Activity**: How many guests AI handled while staff were away.
- **Handoffs**: Conversations requiring staff follow-up.

### 💬 Dashboard Overview
Visit `<your-dashboard-url>` (e.g., `https://nocturn-dashboard.railway.app`) to see real-time stats.
- **Conversations**: View live chats from WhatsApp and Web.
- **Leads**: See captured guest details (Name, Phone, Intent).
- **Analytics**: Money view and Operations view.

## 2. Managing Conversations

### Active vs. Resolved
- **Active**: Ongoing chats. AI handles them automatically.
- **Handoff**: AI has flagged these for human attention (e.g. complaint, complex request).
  - Go to **Conversations > Filter: Handoff**.
  - Reply manually via WhatsApp Business App or Email.
  - Click **Resolve** in dashboard when done.

## 3. Updating Knowledge Base

To update room rates or policies:
1.  Edit your property configuration file (JSON).
2.  Contact your technical administrator to run the update script.
*(Self-service KB management coming in Sprint 5)*.

## 4. FAQs

**Q: Does the AI answer everything?**
A: It answers based on the Knowledge Base. If unsure, it politely directs the guest to staff.

**Q: Can I take over a chat?**
A: Yes. Reply directly via WhatsApp/Email. The AI will see your message but currently doesn't "pause" automatically. Best practice is to mark as "Resolved" if loop is closed.

**Q: How is revenue calculated?**
A: `(Nights * ADR)`. We assume 1 night if not specified.

**Q: Data Privacy?**
A: Guest data is stored securely. Leads older than 2 years are automatically deleted for PDPA compliance.
