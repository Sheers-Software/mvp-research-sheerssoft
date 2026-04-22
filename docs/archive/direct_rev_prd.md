**Product Requirements Document (PRD)**  
**DirectRev MY**  
**SaaS Platform for 3-4 Star Hotels in Malaysia**  
**Version 1.0** | **Date: 6 April 2026** | **Prepared by: Grok (for the startup team)**  

### 1. Executive Summary  
**DirectRev MY** is a cloud-based, all-in-one platform that combines a high-conversion direct booking engine, intelligent revenue management system (RMS), and smart channel manager.  

It is purpose-built for **3-4 star independent hotels in Malaysia** (50–250 rooms) to:  
- Reduce OTA dependency from typical 40–60% → target <30% within 6 months.  
- Cut OTA commission leakage (15–25%+) by driving **direct bookings** and **guest data ownership**.  
- Deliver **real-time dynamic pricing**, accurate forecasting, and automated operations.  

**Core value proposition**:  
“Keep more revenue in your pocket while running a smarter, less stressful hotel.”  

Target launch: MVP in Q3 2026 (ready for Visit Malaysia 2026 peak season).  

### 2. Problem Statement  
From deep research across LinkedIn, Facebook hotelier groups, MAH/MyBHA discussions, and industry reports (April 2025 – April 2026):  
- Hotels lose **15–30%** of every OTA booking in commissions.  
- Rate parity clauses block flexible direct pricing.  
- Guest data stays with OTAs → no remarketing or loyalty.  
- Manual Excel forecasting + outdated PMS → inaccurate occupancy & revenue decisions.  
- High operational costs + staffing shortages make every ringgit lost to OTAs hurt more.  

**Opportunity**: 3-4 star hotels in Malaysia represent the largest segment yet have the least sophisticated tech. A Malaysia-first solution that is affordable, Bahasa Malaysia/English bilingual, and fully compliant with 2026 e-Invoicing (MyInvois) + local payments can capture rapid adoption.

### 3. Business Objectives & Success Metrics (First 12 Months)  
**Primary Goals**  
- Help hotels increase direct bookings by **20–35%**.  
- Reduce effective OTA commission spend by **12–18%** on average.  
- Achieve **3–5x ROI** within 6 months for customers.  

**Key Performance Indicators (KPIs)**  
| Metric                        | Target (6 months) | Target (12 months) |
|-------------------------------|-------------------|--------------------|
| Direct booking share          | 25%+              | 40%+              |
| Avg. monthly revenue lift     | +RM8k–25k/property| +RM15k–40k/property|
| Churn rate                    | <8%               | <5%               |
| Customer NPS                  | >70               | >80               |
| Monthly Active Properties     | 50                | 200+              |

### 4. Target Users & Personas  
**Primary Users (3-4 star hotels, Malaysia)**  
1. **Revenue Manager** – Daily pricing & forecasting (most active).  
2. **Reservation Manager** – Handles bookings, channel updates, guest comms.  
3. **General Manager** – Oversees everything, approves reports.  
4. **Hotel Owner / Principal** – Views financial dashboards & ROI.  

**Secondary**  
- Front Desk / Night Audit (light usage).  
- Marketing / Sales team (guest remarketing).  

All users expect **mobile-friendly**, low-training interface (many are non-tech-savvy).

### 5. Key Features & Requirements  

#### 5.1 MVP Scope (Must-Have for Launch – Q3 2026)  
**Core Modules**  

| Module                  | Key Features                                                                 | Priority |
|-------------------------|-----------------------------------------------------------------------------|----------|
| **Direct Booking Engine** | • Real-time PMS-synced availability & rates<br>• Mobile-optimised, 3-step checkout<br>• Exclusive direct-only rates & packages<br>• WhatsApp & Google Hotel Ads integration<br>• Best-rate guarantee (auto-match OTA) | Must    |
| **Smart Revenue Management** | • AI-driven dynamic pricing (demand, competitor, events, seasonality)<br>• Occupancy & revenue forecasting (7/30/90/365 days)<br>• Rate parity bypass rules (where legally allowed)<br>• Minimum stay / length-of-stay controls | Must    |
| **Channel Manager Lite** | • Bi-directional sync with top OTAs (Booking.com, Agoda, Traveloka, Airbnb)<br>• Rate & inventory auto-update<br>• Commission tracking & savings calculator | Must    |
| **Guest Data & CRM**    | • Full guest profile ownership<br>• Automated remarketing (email/SMS/WhatsApp)<br>• Loyalty points engine<br>• Post-stay review automation | Must    |
| **Malaysia Compliance** | • Automatic e-Invoice generation & MyInvois API submission (2026 mandate)<br>• SST handling & reporting<br>• FPX, Touch ‘n Go, Boost, GrabPay, credit cards<br>• Bilingual (BM/English) UI & reports | Must    |

#### 5.2 Future Phases (Post-MVP)  
- Full labor scheduling & housekeeping module (link to staffing pain #1).  
- Advanced analytics dashboard with competitor rate shopping.  
- AI concierge chatbot for guests.  
- Multi-property support for small chains.  
- Performance-based pricing (pay only % of incremental direct revenue).  

#### 5.3 Non-Functional Requirements  
- **Cloud-native** (AWS or Azure Malaysia region for low latency).  
- **Security**: SOC2 / ISO 27001, PCI-DSS compliant, data residency in Malaysia.  
- **Performance**: <2 sec page load, handle 500 concurrent users.  
- **Integrations**: Open API + native connectors for popular Malaysian PMS (e.g. Cloudbeds, Mews, IFCA, Hotelogix, Opera Lite).  
- **UI/UX**: Simple, dashboard-first, mobile-first, dark/light mode.  
- **Support**: In-app chat + WhatsApp support in BM/English.  
- **Scalability**: From 50-room boutique to 250-room resort.  
- **Pricing Model**: Tiered subscription (RM799 – RM2,999/month) + optional performance fee. Free 30-day pilot.  

### 6. User Stories (High-Level)  
**As a Revenue Manager**  
- I want real-time dynamic pricing suggestions so I can maximise ADR without manual Excel.  
- I want to see exact OTA commission leakage vs direct savings every day.  

**As a Reservation Manager**  
- I want one-click updates to all channels so no overbooking happens.  
- I want to send personalised WhatsApp confirmations instantly.  

**As a GM/Owner**  
- I want a one-page monthly report showing “How much we saved from OTAs this month”.  

### 7. Technical & Integration Requirements  
- RESTful APIs + webhooks.  
- Bi-directional PMS sync (availability, rates, reservations, folio).  
- MyInvois e-Invoice API integration (mandatory for 2026).  
- Google Hotel Ads & Meta direct booking ads connector.  
- Data export to Excel/PDF for legacy owners.  

### 8. Roadmap  
- **MVP** (Q3 2026): Booking engine + RMS + Channel Lite + Compliance.  
- **V1.1** (Q4 2026): Advanced analytics + CRM remarketing.  
- **V2** (Q1 2027): Labor scheduling + full AI concierge.  

### 9. Assumptions, Risks & Dependencies  
**Assumptions**  
- Hotels have basic PMS in place (90%+ do).  
- Early adopters willing to run 30-day pilot.  

**Risks & Mitigations**  
- Rate parity legal issues → Build “best-rate guarantee” + value-add packages instead of direct undercutting.  
- Slow decision-making by owners → Offer ROI calculator + case studies from first 10 pilots.  
- Integration complexity → Start with top 5 PMS used in Malaysia + open API.  

**Dependencies**  
- Access to beta PMS APIs.  
- Legal review of rate parity in Malaysia.  

### 10. Appendix  
- **Competitor Landscape**: Cloudbeds, Mews, SiteMinder, RMS Cloud, Duetto – but none are Malaysia-first with built-in MyInvois + BM language + 3-4 star pricing.  
- **Go-to-Market Alignment**: This PRD directly maps to the sales pipeline you already have (discovery call → demo → pilot).  

**Next Steps for the Team**  
1. Review & approve this PRD (48 hours).  
2. Wireframe key screens (booking engine + dashboard).  
3. Start PMS integration scoping with 2–3 Malaysian PMS providers.  

This PRD is ready to hand to your developers, designers, and sales team. It is laser-focused on the **highest-pain problem (#5)** while positioning you to solve adjacent pains (#3, #4, #8, #9, #10) as well.  

Want me to expand any section (e.g. detailed wireframes description, full user stories, or pricing page mockup text)? Or generate the Google Docs / Notion version template? Just say the word and I’ll deliver it immediately.  

You now have a complete, research-backed PRD you can start building from **today**. Let’s get this into the hands of your first 3-4 star hotel pilots! 🚀