-- ═══════════════════════════════════════════════════════
-- Demo Data Seed: Conversations, Messages, Leads, Analytics
-- Grand Horizon Resort
-- ═══════════════════════════════════════════════════════

BEGIN;

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('347d700f-566f-442f-bfed-1e29bf4c83bc', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'web', '+60123456001', 'Sarah Chen', 'active', true, 'concierge', '2026-03-05 02:02:23+00', '2026-03-05 02:41:23+00', '2026-03-05 02:41:23+00', 5);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('e846f209-2f99-4625-85ac-185155f49b74', '347d700f-566f-442f-bfed-1e29bf4c83bc', 'guest', 'Hi, do you have any suites available for tomorrow night?', '2026-03-05 02:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('70827075-f614-40cb-83a6-220214033074', '347d700f-566f-442f-bfed-1e29bf4c83bc', 'ai', 'Good evening! Thank you for reaching out to Grand Horizon Resort. Yes, we do have suites available for tomorrow night. Our Executive Suite (65 sqm) is available at RM 850/night, and our Grand Suite (90 sqm) is at RM 1,200/night. Both come with complimentary breakfast, airport shuttle, and access to our infinity pool and spa.

Would you like me to hold one for you? I just need your preferred room type and the number of guests.', '2026-03-05 02:02:34+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('c366b610-11d8-41a5-bac6-15a016e6ab37', '347d700f-566f-442f-bfed-1e29bf4c83bc', 'guest', 'That sounds great! Can I get more details?', '2026-03-05 02:03:34+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('80687ba9-f615-405a-9de4-71aa2cb4b77d', '347d700f-566f-442f-bfed-1e29bf4c83bc', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-03-05 02:12:34+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('e78841bb-0722-41ac-9194-1b78e3f50e99', '347d700f-566f-442f-bfed-1e29bf4c83bc', 'guest', 'Sure, it''s Sarah Chen, sarah.chen@gmail.com', '2026-03-05 02:22:34+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('ca37d9aa-01f1-484a-903f-dececa4a61ac', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456002', 'Michael Rodriguez', 'resolved', true, 'handoff', '2026-03-06 04:02:23+00', '2026-03-06 05:47:23+00', '2026-03-06 05:47:23+00', 6);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('9dc41f32-86b3-4a18-9166-e3c377187068', 'ca37d9aa-01f1-484a-903f-dececa4a61ac', 'guest', 'Hello! I''m planning a wedding reception for 200 guests. What packages do you offer?', '2026-03-06 04:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('8c653b50-1b8e-43e6-81a3-1643ecd3380e', 'ca37d9aa-01f1-484a-903f-dececa4a61ac', 'ai', 'Hello! Congratulations on your upcoming wedding! 🎉 We''d love to help you plan your special day. Our Grand Ballroom can comfortably accommodate 200 guests and includes:

- Custom-designed setup with floral arrangements
- 5-course gala dinner with premium beverages
- Complimentary bridal suite for 1 night
- Wedding coordination team

Packages start from RM 280 per person. Shall I arrange a site visit for you?', '2026-03-06 04:02:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('cfe33034-f63f-47bb-90e0-d3f2fc0ea8cb', 'ca37d9aa-01f1-484a-903f-dececa4a61ac', 'guest', 'That sounds great! Can I get more details?', '2026-03-06 04:11:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('ce5f60e8-3d4a-4813-b5a6-3d7f732a90b0', 'ca37d9aa-01f1-484a-903f-dececa4a61ac', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-03-06 04:16:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('1959d5f0-0bfd-4b92-8687-ff36577b66f9', 'ca37d9aa-01f1-484a-903f-dececa4a61ac', 'guest', 'Sure, it''s Michael Rodriguez, m.rodriguez@outlook.com', '2026-03-06 04:26:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('5c2bd9a7-bf9a-419a-9cd2-e8d7c12f4b02', 'ca37d9aa-01f1-484a-903f-dececa4a61ac', 'ai', 'Wonderful! Thank you, Michael. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-03-06 04:34:36+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('d94d92d6-0a96-4a8c-b9b1-0fa2ea44e71a', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'email', '+60123456003', 'Aisha binti Karim', 'resolved', true, 'concierge', '2026-02-10 15:02:23+00', '2026-02-10 15:57:23+00', '2026-02-10 15:57:23+00', 3);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('e9e68890-f85b-4cea-8886-c3d592e13c02', 'd94d92d6-0a96-4a8c-b9b1-0fa2ea44e71a', 'guest', 'Good evening, I''d like to check availability for a family room this weekend.', '2026-02-10 15:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('a4b4c161-79b5-488c-9213-384dc7c57191', 'd94d92d6-0a96-4a8c-b9b1-0fa2ea44e71a', 'ai', 'Thank you for your inquiry! I''d be happy to help. For this weekend, we have several family-friendly options:

🏨 Family Deluxe Room (45 sqm): RM 480/night
🏨 Family Suite (70 sqm): RM 720/night

Both include extra beds for children, kids'' welcome amenity, and access to our children''s pool. Shall I check exact availability for your dates?', '2026-02-10 15:02:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('2bf49d6c-7b3a-4c26-91e4-a4a1abd1b4a8', 'd94d92d6-0a96-4a8c-b9b1-0fa2ea44e71a', 'guest', 'That sounds great! Can I get more details?', '2026-02-10 15:12:30+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('42c33600-bd20-402e-9e64-c327ed68279b', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456004', 'James O''Brien', 'resolved', false, 'concierge', '2026-02-12 02:02:23+00', '2026-02-12 03:16:23+00', '2026-02-12 03:16:23+00', 6);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('b49422fd-d79c-4364-a806-f6b86e3a0b4d', '42c33600-bd20-402e-9e64-c327ed68279b', 'guest', 'Do you have a conference room for a corporate event next month?', '2026-02-12 02:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('27f52263-b373-4abb-a4df-429aaf6a0357', '42c33600-bd20-402e-9e64-c327ed68279b', 'ai', 'Hello! We have excellent meeting facilities available. Our Business Center offers:

📋 Boardroom (up to 20 pax): RM 1,500/day
📋 Conference Hall (up to 100 pax): RM 4,500/day
📋 Grand Ballroom (up to 300 pax): RM 8,000/day

All include AV equipment, WiFi, coffee breaks, and a dedicated event coordinator. What size meeting are you planning?', '2026-02-12 02:02:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('69fbcf61-bd36-49e9-97a0-3ca3f23a2f47', '42c33600-bd20-402e-9e64-c327ed68279b', 'guest', 'That sounds great! Can I get more details?', '2026-02-12 02:08:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('d0bc86e1-168a-4662-b8e1-3dcd5cf3e82b', '42c33600-bd20-402e-9e64-c327ed68279b', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-12 02:10:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('2e4c2722-dfa4-45b0-8ba0-15704b8a23ea', '42c33600-bd20-402e-9e64-c327ed68279b', 'guest', 'Sure, it''s James O''Brien, james.obrien@icloud.com', '2026-02-12 02:18:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('22490025-d1ca-460f-ab44-07b79477b8bf', '42c33600-bd20-402e-9e64-c327ed68279b', 'ai', 'Wonderful! Thank you, James. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-02-12 02:22:30+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('0cb32fa1-9ae5-4e0c-b566-33f253cec100', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'web', '+60123456005', 'Fatimah Zahra', 'active', false, 'concierge', '2026-03-03 20:02:23+00', '2026-03-03 21:20:23+00', '2026-03-03 21:20:23+00', 3);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('a6e4a2c8-4e4f-49e0-96e7-d7cca2c0243b', '0cb32fa1-9ae5-4e0c-b566-33f253cec100', 'guest', 'What are the rates for a deluxe room for 3 nights?', '2026-03-03 20:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('4cd44c47-1572-4ae9-bcd7-c79f82e413cb', '0cb32fa1-9ae5-4e0c-b566-33f253cec100', 'ai', 'Great question! Our rates for the Deluxe Room are:

- Weekday: RM 380/night
- Weekend: RM 450/night
- 3-night package: RM 1,050 (save 8%!)

All rates include daily breakfast buffet, WiFi, and gym access. Would you like me to proceed with a booking?', '2026-03-03 20:02:29+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('0e71b764-75fd-4fcf-a16f-6dfecc6fda87', '0cb32fa1-9ae5-4e0c-b566-33f253cec100', 'guest', 'That sounds great! Can I get more details?', '2026-03-03 20:07:29+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('20ee0b89-176b-4c88-82b3-df96ca794024', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'web', '+60123456006', 'David Kim', 'active', false, 'concierge', '2026-02-12 11:02:23+00', '2026-02-12 11:09:23+00', '2026-02-12 11:09:23+00', 6);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('dab98b11-a765-4cd4-9d32-fcb298502462', '20ee0b89-176b-4c88-82b3-df96ca794024', 'guest', 'Hi there! I''m looking for a romantic getaway package. What do you recommend?', '2026-02-12 11:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('617e57dd-8e12-4950-ae69-3a069ae75e2d', '20ee0b89-176b-4c88-82b3-df96ca794024', 'ai', 'Good evening! Thank you for reaching out to Grand Horizon Resort. Yes, we do have suites available for tomorrow night. Our Executive Suite (65 sqm) is available at RM 850/night, and our Grand Suite (90 sqm) is at RM 1,200/night. Both come with complimentary breakfast, airport shuttle, and access to our infinity pool and spa.

Would you like me to hold one for you? I just need your preferred room type and the number of guests.', '2026-02-12 11:02:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('43ad1ad0-454f-4e87-9e62-171fb9db522a', '20ee0b89-176b-4c88-82b3-df96ca794024', 'guest', 'That sounds great! Can I get more details?', '2026-02-12 11:11:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('21f43a9a-397f-48be-953b-7df11a278bbe', '20ee0b89-176b-4c88-82b3-df96ca794024', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-12 11:16:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('e30c53b2-278e-41e5-997f-f423333ee881', '20ee0b89-176b-4c88-82b3-df96ca794024', 'guest', 'Sure, it''s David Kim, dkim@gmail.com', '2026-02-12 11:23:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('d9c2995c-b341-43c3-8c04-911c97aace09', '20ee0b89-176b-4c88-82b3-df96ca794024', 'ai', 'Wonderful! Thank you, David. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-02-12 11:27:36+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('b4cbc592-67a2-4760-bea6-7c1e9b0451be', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'web', '+60123456007', 'Priya Sharma', 'resolved', false, 'lead_capture', '2026-03-01 03:02:23+00', '2026-03-01 03:50:23+00', '2026-03-01 03:50:23+00', 3);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('1a6ce9fd-3ebf-4c07-bd8c-a8d65cccaeea', 'b4cbc592-67a2-4760-bea6-7c1e9b0451be', 'guest', 'Can I book a room with an ocean view for New Year''s Eve?', '2026-03-01 03:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('2583a000-6da3-4350-8fb4-d3832c6e0a11', 'b4cbc592-67a2-4760-bea6-7c1e9b0451be', 'ai', 'Hello! Congratulations on your upcoming wedding! 🎉 We''d love to help you plan your special day. Our Grand Ballroom can comfortably accommodate 200 guests and includes:

- Custom-designed setup with floral arrangements
- 5-course gala dinner with premium beverages
- Complimentary bridal suite for 1 night
- Wedding coordination team

Packages start from RM 280 per person. Shall I arrange a site visit for you?', '2026-03-01 03:02:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('ade62dca-8640-43c5-ae2d-725ff29a4bad', 'b4cbc592-67a2-4760-bea6-7c1e9b0451be', 'guest', 'That sounds great! Can I get more details?', '2026-03-01 03:08:36+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('3c24759e-bbe7-423e-9502-28bd878c9c8d', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'email', '+60123456008', 'Thomas Weber', 'active', true, 'handoff', '2026-02-20 19:02:23+00', '2026-02-20 20:59:23+00', '2026-02-20 20:59:23+00', 8);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('78d877cd-1c89-4ffe-927a-f2597a24d70c', '3c24759e-bbe7-423e-9502-28bd878c9c8d', 'guest', 'Hello, we need 10 rooms for a company retreat next week. Group discount?', '2026-02-20 19:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('1f7b3087-07bc-4d94-9345-1763ab201f37', '3c24759e-bbe7-423e-9502-28bd878c9c8d', 'ai', 'Thank you for your inquiry! I''d be happy to help. For this weekend, we have several family-friendly options:

🏨 Family Deluxe Room (45 sqm): RM 480/night
🏨 Family Suite (70 sqm): RM 720/night

Both include extra beds for children, kids'' welcome amenity, and access to our children''s pool. Shall I check exact availability for your dates?', '2026-02-20 19:02:38+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('bf8d2863-f4b1-4a51-88a4-a159ec2e5130', '3c24759e-bbe7-423e-9502-28bd878c9c8d', 'guest', 'That sounds great! Can I get more details?', '2026-02-20 19:03:38+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('a68879e3-f633-4d93-ba33-bf0b7a31fbcc', '3c24759e-bbe7-423e-9502-28bd878c9c8d', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-20 19:11:38+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('aafd5560-ebf6-4223-bec1-491b8f35f33f', '3c24759e-bbe7-423e-9502-28bd878c9c8d', 'guest', 'Sure, it''s Thomas Weber, t.weber@gmail.com', '2026-02-20 19:17:38+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('4b0581b8-4a1d-478e-9b19-13f3caa326f2', '3c24759e-bbe7-423e-9502-28bd878c9c8d', 'ai', 'Wonderful! Thank you, Thomas. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-02-20 19:25:38+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('8b656d13-2800-4941-abdc-edb3a556a64c', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456009', 'Nur Aisyah', 'active', true, 'concierge', '2026-02-15 17:02:23+00', '2026-02-15 18:39:23+00', '2026-02-15 18:39:23+00', 8);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('9eb9924c-175f-49e0-88d9-d234ed54d1d1', '8b656d13-2800-4941-abdc-edb3a556a64c', 'guest', 'Is breakfast included with the standard room?', '2026-02-15 17:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('2456fa7a-a471-44cc-82a3-dd40a79bb57f', '8b656d13-2800-4941-abdc-edb3a556a64c', 'ai', 'Hello! We have excellent meeting facilities available. Our Business Center offers:

📋 Boardroom (up to 20 pax): RM 1,500/day
📋 Conference Hall (up to 100 pax): RM 4,500/day
📋 Grand Ballroom (up to 300 pax): RM 8,000/day

All include AV equipment, WiFi, coffee breaks, and a dedicated event coordinator. What size meeting are you planning?', '2026-02-15 17:02:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('67e3afdf-38b4-4577-ab31-f950a770d92c', '8b656d13-2800-4941-abdc-edb3a556a64c', 'guest', 'That sounds great! Can I get more details?', '2026-02-15 17:06:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('dee3a3be-9504-46f1-85ee-bb6ea37ea65c', '8b656d13-2800-4941-abdc-edb3a556a64c', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-15 17:13:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('81bf381f-6109-44e6-b0ba-1919e4445d79', '8b656d13-2800-4941-abdc-edb3a556a64c', 'guest', 'Sure, it''s Nur Aisyah, nuraisyah@gmail.com', '2026-02-15 17:14:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('6f519954-36b0-4d5b-8a58-90ec1150b743', '8b656d13-2800-4941-abdc-edb3a556a64c', 'ai', 'Wonderful! Thank you, Nur. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-02-15 17:17:30+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('e175b561-b9a7-4504-aecf-74146c73c7e0', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'web', '+60123456010', 'Robert Taylor', 'resolved', false, 'concierge', '2026-02-14 19:02:23+00', '2026-02-14 19:57:23+00', '2026-02-14 19:57:23+00', 2);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('d313bb87-8ecc-4037-840e-19890579a4d5', 'e175b561-b9a7-4504-aecf-74146c73c7e0', 'guest', 'I''d like to inquire about your spa and wellness packages.', '2026-02-14 19:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('8d0a84c6-6709-496a-a4d5-9562727af755', 'e175b561-b9a7-4504-aecf-74146c73c7e0', 'ai', 'Great question! Our rates for the Deluxe Room are:

- Weekday: RM 380/night
- Weekend: RM 450/night
- 3-night package: RM 1,050 (save 8%!)

All rates include daily breakfast buffet, WiFi, and gym access. Would you like me to proceed with a booking?', '2026-02-14 19:02:34+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('9e14d40f-8422-4333-8ed2-5d0840eaf295', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456011', 'Lena Fischer', 'resolved', false, 'concierge', '2026-02-04 21:02:23+00', '2026-02-04 21:54:23+00', '2026-02-04 21:54:23+00', 5);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('433a6340-737f-4437-a67a-db0ad550fed0', '9e14d40f-8422-4333-8ed2-5d0840eaf295', 'guest', 'Do you allow pets in the hotel? I have a small dog.', '2026-02-04 21:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('44922ad0-a2d9-4b12-af67-2c0b641a7054', '9e14d40f-8422-4333-8ed2-5d0840eaf295', 'ai', 'Good evening! Thank you for reaching out to Grand Horizon Resort. Yes, we do have suites available for tomorrow night. Our Executive Suite (65 sqm) is available at RM 850/night, and our Grand Suite (90 sqm) is at RM 1,200/night. Both come with complimentary breakfast, airport shuttle, and access to our infinity pool and spa.

Would you like me to hold one for you? I just need your preferred room type and the number of guests.', '2026-02-04 21:02:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('32d0111b-9f2f-466b-9bca-0acfc1c9a61d', '9e14d40f-8422-4333-8ed2-5d0840eaf295', 'guest', 'That sounds great! Can I get more details?', '2026-02-04 21:03:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('397c4c2b-895d-445c-9b3e-4091194cac0a', '9e14d40f-8422-4333-8ed2-5d0840eaf295', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-04 21:13:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('7de868ef-de07-42c2-b7bc-45c339ef06ed', '9e14d40f-8422-4333-8ed2-5d0840eaf295', 'guest', 'Sure, it''s Lena Fischer, lena.fischer@web.de', '2026-02-04 21:14:30+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('684d9ddd-345b-4332-8a16-6ebfec3d541d', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'email', '+60123456012', 'Ahmad Faisal', 'active', false, 'concierge', '2026-02-18 06:02:23+00', '2026-02-18 07:26:23+00', '2026-02-18 07:26:23+00', 2);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('459954dd-2b56-440a-8398-924725ec92cb', '684d9ddd-345b-4332-8a16-6ebfec3d541d', 'guest', 'What time is check-in and check-out?', '2026-02-18 06:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('b6080c30-481e-4054-a4c0-1f7eb16e7f5c', '684d9ddd-345b-4332-8a16-6ebfec3d541d', 'ai', 'Hello! Congratulations on your upcoming wedding! 🎉 We''d love to help you plan your special day. Our Grand Ballroom can comfortably accommodate 200 guests and includes:

- Custom-designed setup with floral arrangements
- 5-course gala dinner with premium beverages
- Complimentary bridal suite for 1 night
- Wedding coordination team

Packages start from RM 280 per person. Shall I arrange a site visit for you?', '2026-02-18 06:02:34+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('5c44785f-0de9-49b2-9088-ec229105f1ce', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'email', '+60123456013', 'Emily Watson', 'resolved', false, 'concierge', '2026-02-15 06:02:23+00', '2026-02-15 07:04:23+00', '2026-02-15 07:04:23+00', 2);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('ec25e9cd-049d-408b-8f70-c008ae9a6d16', '5c44785f-0de9-49b2-9088-ec229105f1ce', 'guest', 'Can you arrange airport pickup for us? We arrive at 3 PM.', '2026-02-15 06:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('3b235527-f2a7-4aa2-ba6c-3889a6d69912', '5c44785f-0de9-49b2-9088-ec229105f1ce', 'ai', 'Thank you for your inquiry! I''d be happy to help. For this weekend, we have several family-friendly options:

🏨 Family Deluxe Room (45 sqm): RM 480/night
🏨 Family Suite (70 sqm): RM 720/night

Both include extra beds for children, kids'' welcome amenity, and access to our children''s pool. Shall I check exact availability for your dates?', '2026-02-15 06:02:32+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('149eebfc-03eb-4c26-b9cf-3de4ba82aa44', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'web', '+60123456014', 'Hiroshi Tanaka', 'active', true, 'handoff', '2026-02-20 17:02:23+00', '2026-02-20 18:31:23+00', '2026-02-20 18:31:23+00', 7);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('cf172ddc-7c1c-4af2-8204-a327b85a43b0', '149eebfc-03eb-4c26-b9cf-3de4ba82aa44', 'guest', 'I need a room with wheelchair accessibility. What options do you have?', '2026-02-20 17:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('a4d01132-3aa2-4723-9d20-cb1504fddb78', '149eebfc-03eb-4c26-b9cf-3de4ba82aa44', 'ai', 'Hello! We have excellent meeting facilities available. Our Business Center offers:

📋 Boardroom (up to 20 pax): RM 1,500/day
📋 Conference Hall (up to 100 pax): RM 4,500/day
📋 Grand Ballroom (up to 300 pax): RM 8,000/day

All include AV equipment, WiFi, coffee breaks, and a dedicated event coordinator. What size meeting are you planning?', '2026-02-20 17:02:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('66f6ac6c-acef-46a0-8375-4391dfdebde9', '149eebfc-03eb-4c26-b9cf-3de4ba82aa44', 'guest', 'That sounds great! Can I get more details?', '2026-02-20 17:10:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('53d92188-d860-4028-9232-3e88e9f8dc69', '149eebfc-03eb-4c26-b9cf-3de4ba82aa44', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-20 17:18:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('79a847ad-fd36-45f5-97c8-c7a44bcd323d', '149eebfc-03eb-4c26-b9cf-3de4ba82aa44', 'guest', 'Sure, it''s Hiroshi Tanaka, h.tanaka@jp.company.com', '2026-02-20 17:21:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('400d178f-e04e-4d31-beb0-599d4c016657', '149eebfc-03eb-4c26-b9cf-3de4ba82aa44', 'ai', 'Wonderful! Thank you, Hiroshi. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-02-20 17:31:36+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('f2b312e0-bb4f-47d1-b38b-3a78216b255d', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'web', '+60123456015', 'Siti Nurhaliza', 'handed_off', true, 'concierge', '2026-02-21 09:02:23+00', '2026-02-21 10:42:23+00', '2026-02-21 10:42:23+00', 5);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('fd32d2c1-66fb-4c1f-b816-8e9c860bd60f', 'f2b312e0-bb4f-47d1-b38b-3a78216b255d', 'guest', 'Are there any special promotions for the lunar new year period?', '2026-02-21 09:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('cacb04cb-f5bc-4532-a2ed-2b3e1881ff73', 'f2b312e0-bb4f-47d1-b38b-3a78216b255d', 'ai', 'Great question! Our rates for the Deluxe Room are:

- Weekday: RM 380/night
- Weekend: RM 450/night
- 3-night package: RM 1,050 (save 8%!)

All rates include daily breakfast buffet, WiFi, and gym access. Would you like me to proceed with a booking?', '2026-02-21 09:02:38+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('41e5d02d-2e95-4c1f-88d1-26271eb8c106', 'f2b312e0-bb4f-47d1-b38b-3a78216b255d', 'guest', 'That sounds great! Can I get more details?', '2026-02-21 09:11:38+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('ff0167b3-5f5c-4695-b625-a41e20e99c53', 'f2b312e0-bb4f-47d1-b38b-3a78216b255d', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-21 09:18:38+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('02680f48-e049-43b9-bf04-3053ee82d0ed', 'f2b312e0-bb4f-47d1-b38b-3a78216b255d', 'guest', 'Sure, it''s Siti Nurhaliza, siti.n@gmail.com', '2026-02-21 09:28:38+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('54524ed6-3c49-4094-9fdc-597cbff90edd', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456016', 'Carlos Mendez', 'handed_off', false, 'lead_capture', '2026-02-07 09:02:23+00', '2026-02-07 10:33:23+00', '2026-02-07 10:33:23+00', 2);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('51de453f-16ce-4ee7-8be4-0d5c3fb5f8e1', '54524ed6-3c49-4094-9fdc-597cbff90edd', 'guest', 'Can I get a late check-out on Sunday? We have an afternoon flight.', '2026-02-07 09:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('081d22e5-a9c9-4c9b-992e-4367dcc53c3f', '54524ed6-3c49-4094-9fdc-597cbff90edd', 'ai', 'Good evening! Thank you for reaching out to Grand Horizon Resort. Yes, we do have suites available for tomorrow night. Our Executive Suite (65 sqm) is available at RM 850/night, and our Grand Suite (90 sqm) is at RM 1,200/night. Both come with complimentary breakfast, airport shuttle, and access to our infinity pool and spa.

Would you like me to hold one for you? I just need your preferred room type and the number of guests.', '2026-02-07 09:02:32+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('6c0757bd-65e3-4ccc-9afa-cf68a5577b9f', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'email', '+60123456017', 'Rachel Green', 'handed_off', false, 'lead_capture', '2026-03-03 11:02:23+00', '2026-03-03 11:19:23+00', '2026-03-03 11:19:23+00', 2);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('16457021-b692-48a4-80c8-50b18fec9f1d', '6c0757bd-65e3-4ccc-9afa-cf68a5577b9f', 'guest', 'What''s the cancellation policy for bookings?', '2026-03-03 11:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('ef9fa9cf-0031-4e19-81d9-c6d943e4e2ad', '6c0757bd-65e3-4ccc-9afa-cf68a5577b9f', 'ai', 'Hello! Congratulations on your upcoming wedding! 🎉 We''d love to help you plan your special day. Our Grand Ballroom can comfortably accommodate 200 guests and includes:

- Custom-designed setup with floral arrangements
- 5-course gala dinner with premium beverages
- Complimentary bridal suite for 1 night
- Wedding coordination team

Packages start from RM 280 per person. Shall I arrange a site visit for you?', '2026-03-03 11:02:29+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('da8c7ff5-f030-4799-b4ef-953ca1dcc44a', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'web', '+60123456018', 'Omar Hassan', 'active', true, 'concierge', '2026-02-23 05:02:23+00', '2026-02-23 05:47:23+00', '2026-02-23 05:47:23+00', 3);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('a65f9d8b-85b0-424e-b527-2059c0514511', 'da8c7ff5-f030-4799-b4ef-953ca1dcc44a', 'guest', 'Do you have interconnecting rooms? We''re traveling with kids.', '2026-02-23 05:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('b5314b09-b041-4ed7-a4b8-ae67772b1a3a', 'da8c7ff5-f030-4799-b4ef-953ca1dcc44a', 'ai', 'Thank you for your inquiry! I''d be happy to help. For this weekend, we have several family-friendly options:

🏨 Family Deluxe Room (45 sqm): RM 480/night
🏨 Family Suite (70 sqm): RM 720/night

Both include extra beds for children, kids'' welcome amenity, and access to our children''s pool. Shall I check exact availability for your dates?', '2026-02-23 05:02:35+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('2fdc98ea-df86-41c6-ab5c-1d58964b7d41', 'da8c7ff5-f030-4799-b4ef-953ca1dcc44a', 'guest', 'That sounds great! Can I get more details?', '2026-02-23 05:03:35+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('a6d194c3-2ae3-4086-b84d-e1b0a7cb1786', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456019', 'Lisa Anderson', 'handed_off', true, 'handoff', '2026-02-17 00:02:23+00', '2026-02-17 00:06:23+00', '2026-02-17 00:06:23+00', 8);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('c63aee02-8036-4610-bddb-5ab4a0900ae8', 'a6d194c3-2ae3-4086-b84d-e1b0a7cb1786', 'guest', 'Is there parking available at the hotel?', '2026-02-17 00:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('1c222450-681f-48da-ba35-afc92a81bb1d', 'a6d194c3-2ae3-4086-b84d-e1b0a7cb1786', 'ai', 'Hello! We have excellent meeting facilities available. Our Business Center offers:

📋 Boardroom (up to 20 pax): RM 1,500/day
📋 Conference Hall (up to 100 pax): RM 4,500/day
📋 Grand Ballroom (up to 300 pax): RM 8,000/day

All include AV equipment, WiFi, coffee breaks, and a dedicated event coordinator. What size meeting are you planning?', '2026-02-17 00:02:35+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('17118e31-86dc-4e60-907a-81b3cadf1f76', 'a6d194c3-2ae3-4086-b84d-e1b0a7cb1786', 'guest', 'That sounds great! Can I get more details?', '2026-02-17 00:05:35+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('48bbfc93-1bba-46bb-b41e-c2f283210ab3', 'a6d194c3-2ae3-4086-b84d-e1b0a7cb1786', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-17 00:08:35+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('d26c452c-380d-454e-8dbb-0f7178670554', 'a6d194c3-2ae3-4086-b84d-e1b0a7cb1786', 'guest', 'Sure, it''s Lisa Anderson, lisa.a@company.com', '2026-02-17 00:09:35+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('c0aff746-5926-4091-830a-02cdc948341a', 'a6d194c3-2ae3-4086-b84d-e1b0a7cb1786', 'ai', 'Wonderful! Thank you, Lisa. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-02-17 00:11:35+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('9ace0ee1-9fb4-4b33-881e-5cfe2debe529', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456020', 'Tan Wei Ming', 'active', false, 'lead_capture', '2026-02-18 08:02:23+00', '2026-02-18 08:50:23+00', '2026-02-18 08:50:23+00', 5);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('61db62ef-cef7-4882-a4de-cca87916a685', '9ace0ee1-9fb4-4b33-881e-5cfe2debe529', 'guest', 'I''d like to book the presidential suite for my anniversary.', '2026-02-18 08:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('9d25b222-1a47-47d4-abd1-7006c762395e', '9ace0ee1-9fb4-4b33-881e-5cfe2debe529', 'ai', 'Great question! Our rates for the Deluxe Room are:

- Weekday: RM 380/night
- Weekend: RM 450/night
- 3-night package: RM 1,050 (save 8%!)

All rates include daily breakfast buffet, WiFi, and gym access. Would you like me to proceed with a booking?', '2026-02-18 08:02:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('93e0ce5c-b92f-413e-9a09-ee9193b38d6e', '9ace0ee1-9fb4-4b33-881e-5cfe2debe529', 'guest', 'That sounds great! Can I get more details?', '2026-02-18 08:10:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('3f408ae6-6b07-47f1-9542-adc10c967ada', '9ace0ee1-9fb4-4b33-881e-5cfe2debe529', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-18 08:19:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('bb8df88a-598b-49ed-829a-5a2ac5109e57', '9ace0ee1-9fb4-4b33-881e-5cfe2debe529', 'guest', 'Sure, it''s Tan Wei Ming, weiming.tan@gmail.com', '2026-02-18 08:21:30+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('602b988e-453e-4c6c-a37a-b79c9999358f', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'web', '+60123456021', 'Sophie Martin', 'handed_off', true, 'concierge', '2026-03-03 01:02:23+00', '2026-03-03 02:46:23+00', '2026-03-03 02:46:23+00', 5);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('468c15c1-2722-444b-8645-b0a4c06867d7', '602b988e-453e-4c6c-a37a-b79c9999358f', 'guest', 'Hi, do you have any suites available for tomorrow night?', '2026-03-03 01:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('0ce4c7a7-e7f2-4857-bd91-751b50027d6b', '602b988e-453e-4c6c-a37a-b79c9999358f', 'ai', 'Good evening! Thank you for reaching out to Grand Horizon Resort. Yes, we do have suites available for tomorrow night. Our Executive Suite (65 sqm) is available at RM 850/night, and our Grand Suite (90 sqm) is at RM 1,200/night. Both come with complimentary breakfast, airport shuttle, and access to our infinity pool and spa.

Would you like me to hold one for you? I just need your preferred room type and the number of guests.', '2026-03-03 01:02:34+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('2f9ce3b8-173a-4c97-be3f-ee35e8f4ff75', '602b988e-453e-4c6c-a37a-b79c9999358f', 'guest', 'That sounds great! Can I get more details?', '2026-03-03 01:06:34+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('a5cc4968-e628-4300-8ca4-42c00c25024e', '602b988e-453e-4c6c-a37a-b79c9999358f', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-03-03 01:07:34+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('21ba6540-8f30-42b3-b18f-8fff7262746c', '602b988e-453e-4c6c-a37a-b79c9999358f', 'guest', 'Sure, it''s Sophie Martin, sophie.m@gmail.com', '2026-03-03 01:17:34+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('617470c2-5945-4ee8-9984-cf0030dccad4', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456022', 'Raj Patel', 'active', true, 'handoff', '2026-02-21 22:02:23+00', '2026-02-21 22:49:23+00', '2026-02-21 22:49:23+00', 6);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('52d53c97-4f04-480d-8daf-12ce555ec9dd', '617470c2-5945-4ee8-9984-cf0030dccad4', 'guest', 'Hello! I''m planning a wedding reception for 200 guests. What packages do you offer?', '2026-02-21 22:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('ed54cbd0-7a24-47a5-b24e-f242a3a1146e', '617470c2-5945-4ee8-9984-cf0030dccad4', 'ai', 'Hello! Congratulations on your upcoming wedding! 🎉 We''d love to help you plan your special day. Our Grand Ballroom can comfortably accommodate 200 guests and includes:

- Custom-designed setup with floral arrangements
- 5-course gala dinner with premium beverages
- Complimentary bridal suite for 1 night
- Wedding coordination team

Packages start from RM 280 per person. Shall I arrange a site visit for you?', '2026-02-21 22:02:26+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('a796c54f-8f0c-4550-adc2-9449526c678f', '617470c2-5945-4ee8-9984-cf0030dccad4', 'guest', 'That sounds great! Can I get more details?', '2026-02-21 22:09:26+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('fbb6dc7a-8ed5-42b0-9c65-82c285404268', '617470c2-5945-4ee8-9984-cf0030dccad4', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-21 22:13:26+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('a6764bc3-7e5a-49e2-8e63-407476c9ae29', '617470c2-5945-4ee8-9984-cf0030dccad4', 'guest', 'Sure, it''s Raj Patel, raj.patel@hotmail.com', '2026-02-21 22:16:26+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('edbdbb7e-d37b-486c-8dc4-5fd3f802e85d', '617470c2-5945-4ee8-9984-cf0030dccad4', 'ai', 'Wonderful! Thank you, Raj. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-02-21 22:21:26+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('9e3e34ff-108b-4c65-8a61-a22ee6a06ede', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456023', 'Anna Kowalski', 'resolved', true, 'concierge', '2026-02-12 07:02:23+00', '2026-02-12 08:04:23+00', '2026-02-12 08:04:23+00', 5);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('1467d01a-fa92-45e2-a692-871cf1b7f9cf', '9e3e34ff-108b-4c65-8a61-a22ee6a06ede', 'guest', 'Good evening, I''d like to check availability for a family room this weekend.', '2026-02-12 07:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('bf125050-b46a-4d4d-a219-e8f13d120ff0', '9e3e34ff-108b-4c65-8a61-a22ee6a06ede', 'ai', 'Thank you for your inquiry! I''d be happy to help. For this weekend, we have several family-friendly options:

🏨 Family Deluxe Room (45 sqm): RM 480/night
🏨 Family Suite (70 sqm): RM 720/night

Both include extra beds for children, kids'' welcome amenity, and access to our children''s pool. Shall I check exact availability for your dates?', '2026-02-12 07:02:37+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('24bcf027-d4a9-45d7-a59a-2864790d1b4d', '9e3e34ff-108b-4c65-8a61-a22ee6a06ede', 'guest', 'That sounds great! Can I get more details?', '2026-02-12 07:10:37+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('bbc3c2f7-f32c-4df1-9eca-177948e20248', '9e3e34ff-108b-4c65-8a61-a22ee6a06ede', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-12 07:13:37+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('faef8adc-fef1-43c1-88bb-5d9018fbca14', '9e3e34ff-108b-4c65-8a61-a22ee6a06ede', 'guest', 'Sure, it''s Anna Kowalski, anna.k@gmail.com', '2026-02-12 07:21:37+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('05dc4ee5-938e-4ae8-84ca-390a6396d3b8', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'email', '+60123456024', 'Muhammad Rizki', 'resolved', false, 'handoff', '2026-02-23 12:02:23+00', '2026-02-23 12:28:23+00', '2026-02-23 12:28:23+00', 3);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('cddd8a7c-d9b4-4377-92a5-eed36f73c1a7', '05dc4ee5-938e-4ae8-84ca-390a6396d3b8', 'guest', 'Do you have a conference room for a corporate event next month?', '2026-02-23 12:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('20393c4d-f816-4901-a3f5-5c33e2bc6e38', '05dc4ee5-938e-4ae8-84ca-390a6396d3b8', 'ai', 'Hello! We have excellent meeting facilities available. Our Business Center offers:

📋 Boardroom (up to 20 pax): RM 1,500/day
📋 Conference Hall (up to 100 pax): RM 4,500/day
📋 Grand Ballroom (up to 300 pax): RM 8,000/day

All include AV equipment, WiFi, coffee breaks, and a dedicated event coordinator. What size meeting are you planning?', '2026-02-23 12:02:28+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('a0a1728d-68cc-4a68-860f-8dc365ba1583', '05dc4ee5-938e-4ae8-84ca-390a6396d3b8', 'guest', 'That sounds great! Can I get more details?', '2026-02-23 12:03:28+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('81a44c21-0c55-4952-a871-0fbbcb68baaf', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456025', 'Jennifer Liu', 'handed_off', false, 'concierge', '2026-02-25 04:02:23+00', '2026-02-25 04:38:23+00', '2026-02-25 04:38:23+00', 7);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('517133e9-dcd8-4785-82e9-43f9ef1b5054', '81a44c21-0c55-4952-a871-0fbbcb68baaf', 'guest', 'What are the rates for a deluxe room for 3 nights?', '2026-02-25 04:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('ae58742b-8595-4f9e-8b93-1c499fca8efd', '81a44c21-0c55-4952-a871-0fbbcb68baaf', 'ai', 'Great question! Our rates for the Deluxe Room are:

- Weekday: RM 380/night
- Weekend: RM 450/night
- 3-night package: RM 1,050 (save 8%!)

All rates include daily breakfast buffet, WiFi, and gym access. Would you like me to proceed with a booking?', '2026-02-25 04:02:33+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('76b1d77b-7adb-4a05-a53a-df3da598ac77', '81a44c21-0c55-4952-a871-0fbbcb68baaf', 'guest', 'That sounds great! Can I get more details?', '2026-02-25 04:05:33+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('f3134ea4-c0f1-429f-9449-48b2532a84f4', '81a44c21-0c55-4952-a871-0fbbcb68baaf', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-25 04:07:33+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('57cafe74-7d97-46f0-a8e7-2233167c5b53', '81a44c21-0c55-4952-a871-0fbbcb68baaf', 'guest', 'Sure, it''s Jennifer Liu, jennifer.liu@gmail.com', '2026-02-25 04:14:33+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('61a86e81-612c-4732-9acc-501c8d2a2a8b', '81a44c21-0c55-4952-a871-0fbbcb68baaf', 'ai', 'Wonderful! Thank you, Jennifer. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-02-25 04:15:33+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('cd5191db-1165-4558-aad4-02ec7d552f63', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456001', 'Sarah Chen', 'resolved', true, 'concierge', '2026-02-08 20:02:23+00', '2026-02-08 21:32:23+00', '2026-02-08 21:32:23+00', 6);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('4a76554d-5539-403e-bab1-f92dbaf7a9fd', 'cd5191db-1165-4558-aad4-02ec7d552f63', 'guest', 'Hi there! I''m looking for a romantic getaway package. What do you recommend?', '2026-02-08 20:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('99330464-ff10-4681-82f6-9cf159d8da74', 'cd5191db-1165-4558-aad4-02ec7d552f63', 'ai', 'Good evening! Thank you for reaching out to Grand Horizon Resort. Yes, we do have suites available for tomorrow night. Our Executive Suite (65 sqm) is available at RM 850/night, and our Grand Suite (90 sqm) is at RM 1,200/night. Both come with complimentary breakfast, airport shuttle, and access to our infinity pool and spa.

Would you like me to hold one for you? I just need your preferred room type and the number of guests.', '2026-02-08 20:02:26+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('2a14e405-870f-4733-9b50-76498a618f5b', 'cd5191db-1165-4558-aad4-02ec7d552f63', 'guest', 'That sounds great! Can I get more details?', '2026-02-08 20:04:26+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('c69a49d8-d5a4-4f68-89c8-a38363ce3117', 'cd5191db-1165-4558-aad4-02ec7d552f63', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-08 20:08:26+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('1e3ed97b-eefd-47c6-9ffd-103b753792a1', 'cd5191db-1165-4558-aad4-02ec7d552f63', 'guest', 'Sure, it''s Sarah Chen, sarah.chen@gmail.com', '2026-02-08 20:17:26+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('529a74c8-dc53-417a-ab64-269163581ee0', 'cd5191db-1165-4558-aad4-02ec7d552f63', 'ai', 'Wonderful! Thank you, Sarah. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-02-08 20:25:26+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('bfcaa216-6cc7-4eb6-9813-528ef4860e47', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456002', 'Michael Rodriguez', 'active', false, 'lead_capture', '2026-02-15 04:02:23+00', '2026-02-15 04:22:23+00', '2026-02-15 04:22:23+00', 5);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('77269046-543c-42d0-9edd-341403f36705', 'bfcaa216-6cc7-4eb6-9813-528ef4860e47', 'guest', 'Can I book a room with an ocean view for New Year''s Eve?', '2026-02-15 04:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('bdc12da3-512f-4e38-a744-cb43f72c52e3', 'bfcaa216-6cc7-4eb6-9813-528ef4860e47', 'ai', 'Hello! Congratulations on your upcoming wedding! 🎉 We''d love to help you plan your special day. Our Grand Ballroom can comfortably accommodate 200 guests and includes:

- Custom-designed setup with floral arrangements
- 5-course gala dinner with premium beverages
- Complimentary bridal suite for 1 night
- Wedding coordination team

Packages start from RM 280 per person. Shall I arrange a site visit for you?', '2026-02-15 04:02:34+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('73979850-31f5-40a8-a134-943bccad66c6', 'bfcaa216-6cc7-4eb6-9813-528ef4860e47', 'guest', 'That sounds great! Can I get more details?', '2026-02-15 04:10:34+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('126123a8-b19b-4eb7-8cff-b20feb2d2622', 'bfcaa216-6cc7-4eb6-9813-528ef4860e47', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-15 04:16:34+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('b010afcf-2050-4519-b220-e6996e104d19', 'bfcaa216-6cc7-4eb6-9813-528ef4860e47', 'guest', 'Sure, it''s Michael Rodriguez, m.rodriguez@outlook.com', '2026-02-15 04:17:34+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('85766a8b-7629-4cb8-8534-fa6847ed801c', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456003', 'Aisha binti Karim', 'resolved', false, 'lead_capture', '2026-02-07 22:02:23+00', '2026-02-07 22:42:23+00', '2026-02-07 22:42:23+00', 5);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('e00d661b-ef45-4738-a4dd-73760560623e', '85766a8b-7629-4cb8-8534-fa6847ed801c', 'guest', 'Hello, we need 10 rooms for a company retreat next week. Group discount?', '2026-02-07 22:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('ae3ad8dd-4670-4ecd-9a14-2c752de698c0', '85766a8b-7629-4cb8-8534-fa6847ed801c', 'ai', 'Thank you for your inquiry! I''d be happy to help. For this weekend, we have several family-friendly options:

🏨 Family Deluxe Room (45 sqm): RM 480/night
🏨 Family Suite (70 sqm): RM 720/night

Both include extra beds for children, kids'' welcome amenity, and access to our children''s pool. Shall I check exact availability for your dates?', '2026-02-07 22:02:27+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('5f72e784-dea1-4fd6-9e7f-2769bfd0fa2c', '85766a8b-7629-4cb8-8534-fa6847ed801c', 'guest', 'That sounds great! Can I get more details?', '2026-02-07 22:03:27+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('fbf46b90-87fb-475b-b283-765ef7b3a1f5', '85766a8b-7629-4cb8-8534-fa6847ed801c', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-07 22:11:27+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('6aa1aa32-edbd-42d9-adb0-d1d85cfe6c05', '85766a8b-7629-4cb8-8534-fa6847ed801c', 'guest', 'Sure, it''s Aisha binti Karim, aisha.karim@yahoo.com', '2026-02-07 22:19:27+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('b975952c-6bd2-49dc-b853-587c9954a42e', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456004', 'James O''Brien', 'resolved', false, 'concierge', '2026-03-06 03:02:23+00', '2026-03-06 04:05:23+00', '2026-03-06 04:05:23+00', 4);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('dae51aea-43ce-4600-a984-8ce9d8cc3770', 'b975952c-6bd2-49dc-b853-587c9954a42e', 'guest', 'Is breakfast included with the standard room?', '2026-03-06 03:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('3db1c1f1-9b7f-4b49-b59e-09b56b4b003e', 'b975952c-6bd2-49dc-b853-587c9954a42e', 'ai', 'Hello! We have excellent meeting facilities available. Our Business Center offers:

📋 Boardroom (up to 20 pax): RM 1,500/day
📋 Conference Hall (up to 100 pax): RM 4,500/day
📋 Grand Ballroom (up to 300 pax): RM 8,000/day

All include AV equipment, WiFi, coffee breaks, and a dedicated event coordinator. What size meeting are you planning?', '2026-03-06 03:02:35+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('999de17a-8018-4847-8bef-834bdc65e46d', 'b975952c-6bd2-49dc-b853-587c9954a42e', 'guest', 'That sounds great! Can I get more details?', '2026-03-06 03:09:35+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('e7a04289-e334-437d-beed-2c132629dda8', 'b975952c-6bd2-49dc-b853-587c9954a42e', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-03-06 03:12:35+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('03cf97a6-aee2-4d12-b4d5-012eb2e88eb3', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456005', 'Fatimah Zahra', 'active', true, 'concierge', '2026-02-28 09:02:23+00', '2026-02-28 10:51:23+00', '2026-02-28 10:51:23+00', 4);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('373463d3-afd9-4bca-941e-eba3135d8ae1', '03cf97a6-aee2-4d12-b4d5-012eb2e88eb3', 'guest', 'I''d like to inquire about your spa and wellness packages.', '2026-02-28 09:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('0e921c14-8e69-4e3a-9f66-7937a296271f', '03cf97a6-aee2-4d12-b4d5-012eb2e88eb3', 'ai', 'Great question! Our rates for the Deluxe Room are:

- Weekday: RM 380/night
- Weekend: RM 450/night
- 3-night package: RM 1,050 (save 8%!)

All rates include daily breakfast buffet, WiFi, and gym access. Would you like me to proceed with a booking?', '2026-02-28 09:02:34+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('6a5fe588-4c43-4f55-b62a-5d8d419bebac', '03cf97a6-aee2-4d12-b4d5-012eb2e88eb3', 'guest', 'That sounds great! Can I get more details?', '2026-02-28 09:12:34+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('1f1bd8aa-b261-47d5-be12-7aca985f4807', '03cf97a6-aee2-4d12-b4d5-012eb2e88eb3', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-28 09:15:34+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('5e306ac7-fc9a-46c6-a580-6c383f73f0c7', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456006', 'David Kim', 'active', true, 'lead_capture', '2026-02-13 16:02:23+00', '2026-02-13 17:35:23+00', '2026-02-13 17:35:23+00', 8);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('7bd87ae8-b126-4c0e-81ff-b89cd97452d5', '5e306ac7-fc9a-46c6-a580-6c383f73f0c7', 'guest', 'Do you allow pets in the hotel? I have a small dog.', '2026-02-13 16:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('3a694267-f7a3-4c17-8bc4-e197b59db1a0', '5e306ac7-fc9a-46c6-a580-6c383f73f0c7', 'ai', 'Good evening! Thank you for reaching out to Grand Horizon Resort. Yes, we do have suites available for tomorrow night. Our Executive Suite (65 sqm) is available at RM 850/night, and our Grand Suite (90 sqm) is at RM 1,200/night. Both come with complimentary breakfast, airport shuttle, and access to our infinity pool and spa.

Would you like me to hold one for you? I just need your preferred room type and the number of guests.', '2026-02-13 16:02:26+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('f24517dd-5501-4e7b-97ac-24de3dc9f749', '5e306ac7-fc9a-46c6-a580-6c383f73f0c7', 'guest', 'That sounds great! Can I get more details?', '2026-02-13 16:10:26+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('6fa4bb7c-636b-4fa2-8cf4-f3b9161115b7', '5e306ac7-fc9a-46c6-a580-6c383f73f0c7', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-13 16:19:26+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('eeb0aaaa-fb51-42a2-a1d5-ac051820e080', '5e306ac7-fc9a-46c6-a580-6c383f73f0c7', 'guest', 'Sure, it''s David Kim, dkim@gmail.com', '2026-02-13 16:24:26+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('30534229-39e6-40f6-8b77-2a5b81a5fcdc', '5e306ac7-fc9a-46c6-a580-6c383f73f0c7', 'ai', 'Wonderful! Thank you, David. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-02-13 16:34:26+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('e4537a1b-689d-4f3a-8906-a56dd403abec', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'web', '+60123456007', 'Priya Sharma', 'active', false, 'concierge', '2026-02-05 18:02:23+00', '2026-02-05 18:42:23+00', '2026-02-05 18:42:23+00', 3);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('44ea3414-550c-4da7-ac55-610be7697b62', 'e4537a1b-689d-4f3a-8906-a56dd403abec', 'guest', 'What time is check-in and check-out?', '2026-02-05 18:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('2f06e016-c65b-48f7-98ad-15a2b699d035', 'e4537a1b-689d-4f3a-8906-a56dd403abec', 'ai', 'Hello! Congratulations on your upcoming wedding! 🎉 We''d love to help you plan your special day. Our Grand Ballroom can comfortably accommodate 200 guests and includes:

- Custom-designed setup with floral arrangements
- 5-course gala dinner with premium beverages
- Complimentary bridal suite for 1 night
- Wedding coordination team

Packages start from RM 280 per person. Shall I arrange a site visit for you?', '2026-02-05 18:02:33+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('46ca67b7-0b3a-460c-8ca3-ce19020c104b', 'e4537a1b-689d-4f3a-8906-a56dd403abec', 'guest', 'That sounds great! Can I get more details?', '2026-02-05 18:07:33+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('2474c791-1e87-42b1-893f-20a7c7010cb6', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'web', '+60123456008', 'Thomas Weber', 'active', false, 'lead_capture', '2026-02-07 01:02:23+00', '2026-02-07 01:41:23+00', '2026-02-07 01:41:23+00', 2);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('b6e67ac9-a844-4626-adbc-2447692edb2f', '2474c791-1e87-42b1-893f-20a7c7010cb6', 'guest', 'Can you arrange airport pickup for us? We arrive at 3 PM.', '2026-02-07 01:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('18b8b978-4c05-46c7-8fe5-b1b0adb1d669', '2474c791-1e87-42b1-893f-20a7c7010cb6', 'ai', 'Thank you for your inquiry! I''d be happy to help. For this weekend, we have several family-friendly options:

🏨 Family Deluxe Room (45 sqm): RM 480/night
🏨 Family Suite (70 sqm): RM 720/night

Both include extra beds for children, kids'' welcome amenity, and access to our children''s pool. Shall I check exact availability for your dates?', '2026-02-07 01:02:37+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('78f14fa7-b54e-41fa-acb2-4eeea2dc35ef', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456009', 'Nur Aisyah', 'resolved', true, 'concierge', '2026-02-20 16:02:23+00', '2026-02-20 16:46:23+00', '2026-02-20 16:46:23+00', 7);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('44c63c85-f6eb-40fb-a867-4291a0a61182', '78f14fa7-b54e-41fa-acb2-4eeea2dc35ef', 'guest', 'I need a room with wheelchair accessibility. What options do you have?', '2026-02-20 16:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('8aceebc2-a306-4aaa-b099-b89eba423fbc', '78f14fa7-b54e-41fa-acb2-4eeea2dc35ef', 'ai', 'Hello! We have excellent meeting facilities available. Our Business Center offers:

📋 Boardroom (up to 20 pax): RM 1,500/day
📋 Conference Hall (up to 100 pax): RM 4,500/day
📋 Grand Ballroom (up to 300 pax): RM 8,000/day

All include AV equipment, WiFi, coffee breaks, and a dedicated event coordinator. What size meeting are you planning?', '2026-02-20 16:02:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('fdda160d-8cc2-4b59-bfdc-edfc3c0c53ee', '78f14fa7-b54e-41fa-acb2-4eeea2dc35ef', 'guest', 'That sounds great! Can I get more details?', '2026-02-20 16:04:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('97aa9c00-8431-48e1-be81-1982e21d6e3f', '78f14fa7-b54e-41fa-acb2-4eeea2dc35ef', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-20 16:05:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('82aa4340-c773-4770-a620-0695993e2490', '78f14fa7-b54e-41fa-acb2-4eeea2dc35ef', 'guest', 'Sure, it''s Nur Aisyah, nuraisyah@gmail.com', '2026-02-20 16:14:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('0ef4aadd-831f-4628-90d9-a75974fcc74b', '78f14fa7-b54e-41fa-acb2-4eeea2dc35ef', 'ai', 'Wonderful! Thank you, Nur. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-02-20 16:19:36+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('21b16867-a178-4058-bac7-019c256e1155', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'web', '+60123456010', 'Robert Taylor', 'active', true, 'lead_capture', '2026-02-12 14:02:23+00', '2026-02-12 16:02:23+00', '2026-02-12 16:02:23+00', 5);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('6610b2de-141d-42a6-97a5-26561cfb8287', '21b16867-a178-4058-bac7-019c256e1155', 'guest', 'Are there any special promotions for the lunar new year period?', '2026-02-12 14:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('fbf5949b-2c59-4b6f-b891-b16d17471456', '21b16867-a178-4058-bac7-019c256e1155', 'ai', 'Great question! Our rates for the Deluxe Room are:

- Weekday: RM 380/night
- Weekend: RM 450/night
- 3-night package: RM 1,050 (save 8%!)

All rates include daily breakfast buffet, WiFi, and gym access. Would you like me to proceed with a booking?', '2026-02-12 14:02:28+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('94eb5984-78ff-4dd3-a6ef-4199571cf73c', '21b16867-a178-4058-bac7-019c256e1155', 'guest', 'That sounds great! Can I get more details?', '2026-02-12 14:08:28+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('a9df74f8-ca41-4ac3-baea-236001d0ee61', '21b16867-a178-4058-bac7-019c256e1155', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-12 14:10:28+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('4a53cb29-7c91-4663-ba2e-3341c5ce9ecb', '21b16867-a178-4058-bac7-019c256e1155', 'guest', 'Sure, it''s Robert Taylor, robert.t@yahoo.com', '2026-02-12 14:11:28+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('3aea3b2b-a677-4e95-b516-72e8c115a20d', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'web', '+60123456011', 'Lena Fischer', 'active', true, 'concierge', '2026-02-11 12:02:23+00', '2026-02-11 13:01:23+00', '2026-02-11 13:01:23+00', 2);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('7e16a87b-7303-46a7-8a71-bb83137ccfba', '3aea3b2b-a677-4e95-b516-72e8c115a20d', 'guest', 'Can I get a late check-out on Sunday? We have an afternoon flight.', '2026-02-11 12:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('0a97e2d4-4897-48c6-8c2d-fef0a1da85c8', '3aea3b2b-a677-4e95-b516-72e8c115a20d', 'ai', 'Good evening! Thank you for reaching out to Grand Horizon Resort. Yes, we do have suites available for tomorrow night. Our Executive Suite (65 sqm) is available at RM 850/night, and our Grand Suite (90 sqm) is at RM 1,200/night. Both come with complimentary breakfast, airport shuttle, and access to our infinity pool and spa.

Would you like me to hold one for you? I just need your preferred room type and the number of guests.', '2026-02-11 12:02:36+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('0638a0fd-d287-4b80-8dbf-ee96c4031bf7', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'web', '+60123456012', 'Ahmad Faisal', 'resolved', false, 'concierge', '2026-02-16 13:02:23+00', '2026-02-16 14:20:23+00', '2026-02-16 14:20:23+00', 7);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('ac67892b-48a0-476a-9f20-543bd2d5c346', '0638a0fd-d287-4b80-8dbf-ee96c4031bf7', 'guest', 'What''s the cancellation policy for bookings?', '2026-02-16 13:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('16d18180-fd2e-4601-95b8-7331d168c888', '0638a0fd-d287-4b80-8dbf-ee96c4031bf7', 'ai', 'Hello! Congratulations on your upcoming wedding! 🎉 We''d love to help you plan your special day. Our Grand Ballroom can comfortably accommodate 200 guests and includes:

- Custom-designed setup with floral arrangements
- 5-course gala dinner with premium beverages
- Complimentary bridal suite for 1 night
- Wedding coordination team

Packages start from RM 280 per person. Shall I arrange a site visit for you?', '2026-02-16 13:02:29+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('f69f6d5a-928b-4b39-9f61-2da22993685b', '0638a0fd-d287-4b80-8dbf-ee96c4031bf7', 'guest', 'That sounds great! Can I get more details?', '2026-02-16 13:03:29+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('d8c265b1-8d74-4c11-962b-6ba9f03fc483', '0638a0fd-d287-4b80-8dbf-ee96c4031bf7', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-16 13:04:29+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('e1d3bccd-66e3-49cd-9843-0bf7b1ba78cd', '0638a0fd-d287-4b80-8dbf-ee96c4031bf7', 'guest', 'Sure, it''s Ahmad Faisal, ahmadfaisal@gmail.com', '2026-02-16 13:05:29+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('08c2a76a-4ab5-4641-ae63-e4dbb47c388d', '0638a0fd-d287-4b80-8dbf-ee96c4031bf7', 'ai', 'Wonderful! Thank you, Ahmad. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-02-16 13:08:29+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('85f84c12-12a1-4d8c-81b1-289381c0c9fe', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'web', '+60123456013', 'Emily Watson', 'active', true, 'concierge', '2026-02-07 10:02:23+00', '2026-02-07 11:19:23+00', '2026-02-07 11:19:23+00', 2);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('94ba338b-0823-4681-a2e6-1ab8548966bb', '85f84c12-12a1-4d8c-81b1-289381c0c9fe', 'guest', 'Do you have interconnecting rooms? We''re traveling with kids.', '2026-02-07 10:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('dd38050c-6229-4804-a8a7-47bb9a40fb5f', '85f84c12-12a1-4d8c-81b1-289381c0c9fe', 'ai', 'Thank you for your inquiry! I''d be happy to help. For this weekend, we have several family-friendly options:

🏨 Family Deluxe Room (45 sqm): RM 480/night
🏨 Family Suite (70 sqm): RM 720/night

Both include extra beds for children, kids'' welcome amenity, and access to our children''s pool. Shall I check exact availability for your dates?', '2026-02-07 10:02:30+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('aef66ee7-3473-4de4-9711-abbfff91997e', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456014', 'Hiroshi Tanaka', 'resolved', false, 'concierge', '2026-02-13 20:02:23+00', '2026-02-13 21:43:23+00', '2026-02-13 21:43:23+00', 4);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('663c28ce-2919-4a51-897c-f7089b0cc737', 'aef66ee7-3473-4de4-9711-abbfff91997e', 'guest', 'Is there parking available at the hotel?', '2026-02-13 20:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('f840cfb1-4048-4743-ac51-73e514f22b62', 'aef66ee7-3473-4de4-9711-abbfff91997e', 'ai', 'Hello! We have excellent meeting facilities available. Our Business Center offers:

📋 Boardroom (up to 20 pax): RM 1,500/day
📋 Conference Hall (up to 100 pax): RM 4,500/day
📋 Grand Ballroom (up to 300 pax): RM 8,000/day

All include AV equipment, WiFi, coffee breaks, and a dedicated event coordinator. What size meeting are you planning?', '2026-02-13 20:02:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('10952f84-236b-4fca-a3b0-f933c4d74e41', 'aef66ee7-3473-4de4-9711-abbfff91997e', 'guest', 'That sounds great! Can I get more details?', '2026-02-13 20:03:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('e7d37da9-684a-455e-ae4a-55e0e9942749', 'aef66ee7-3473-4de4-9711-abbfff91997e', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-13 20:09:36+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('c5cedd6a-5580-4b13-aad3-a9388eb9c8aa', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'web', '+60123456015', 'Siti Nurhaliza', 'active', true, 'concierge', '2026-02-09 13:02:23+00', '2026-02-09 13:26:23+00', '2026-02-09 13:26:23+00', 4);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('f3794d95-b4f4-4ae7-8e15-8bb9d96e7449', 'c5cedd6a-5580-4b13-aad3-a9388eb9c8aa', 'guest', 'I''d like to book the presidential suite for my anniversary.', '2026-02-09 13:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('526483ee-3b76-4d64-870c-1b57af087df1', 'c5cedd6a-5580-4b13-aad3-a9388eb9c8aa', 'ai', 'Great question! Our rates for the Deluxe Room are:

- Weekday: RM 380/night
- Weekend: RM 450/night
- 3-night package: RM 1,050 (save 8%!)

All rates include daily breakfast buffet, WiFi, and gym access. Would you like me to proceed with a booking?', '2026-02-09 13:02:34+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('52004157-cc77-4ea2-9424-da371f9432bc', 'c5cedd6a-5580-4b13-aad3-a9388eb9c8aa', 'guest', 'That sounds great! Can I get more details?', '2026-02-09 13:08:34+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('5ba542cb-1ad9-429c-b9e9-d4be017be929', 'c5cedd6a-5580-4b13-aad3-a9388eb9c8aa', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-09 13:16:34+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('47d8f38e-ba43-4989-96f9-924a2dba7a22', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456016', 'Carlos Mendez', 'resolved', true, 'handoff', '2026-02-07 07:02:23+00', '2026-02-07 07:43:23+00', '2026-02-07 07:43:23+00', 2);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('4b6dd0ac-a1fb-4d6a-ab6f-4b8dca7e0caa', '47d8f38e-ba43-4989-96f9-924a2dba7a22', 'guest', 'Hi, do you have any suites available for tomorrow night?', '2026-02-07 07:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('862f8c44-50a2-4ab3-b8b5-eed5fc870c0c', '47d8f38e-ba43-4989-96f9-924a2dba7a22', 'ai', 'Good evening! Thank you for reaching out to Grand Horizon Resort. Yes, we do have suites available for tomorrow night. Our Executive Suite (65 sqm) is available at RM 850/night, and our Grand Suite (90 sqm) is at RM 1,200/night. Both come with complimentary breakfast, airport shuttle, and access to our infinity pool and spa.

Would you like me to hold one for you? I just need your preferred room type and the number of guests.', '2026-02-07 07:02:36+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('1374a911-dc71-49c3-8e93-0fe4e9543581', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456017', 'Rachel Green', 'handed_off', true, 'lead_capture', '2026-03-05 18:02:23+00', '2026-03-05 19:18:23+00', '2026-03-05 19:18:23+00', 2);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('b6fe9805-bdc1-4491-8892-36a0e6598f2c', '1374a911-dc71-49c3-8e93-0fe4e9543581', 'guest', 'Hello! I''m planning a wedding reception for 200 guests. What packages do you offer?', '2026-03-05 18:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('06f9227c-9e95-44f5-a6fd-27d6b93cc17a', '1374a911-dc71-49c3-8e93-0fe4e9543581', 'ai', 'Hello! Congratulations on your upcoming wedding! 🎉 We''d love to help you plan your special day. Our Grand Ballroom can comfortably accommodate 200 guests and includes:

- Custom-designed setup with floral arrangements
- 5-course gala dinner with premium beverages
- Complimentary bridal suite for 1 night
- Wedding coordination team

Packages start from RM 280 per person. Shall I arrange a site visit for you?', '2026-03-05 18:02:34+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('7b056f7a-3883-430c-b948-63d8eafc89a6', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456018', 'Omar Hassan', 'resolved', false, 'concierge', '2026-02-28 13:02:23+00', '2026-02-28 14:33:23+00', '2026-02-28 14:33:23+00', 5);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('4b62f6b0-6b1a-418c-8ec0-b78a98487150', '7b056f7a-3883-430c-b948-63d8eafc89a6', 'guest', 'Good evening, I''d like to check availability for a family room this weekend.', '2026-02-28 13:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('a7a728c5-03a5-4982-8b93-6bbc90f97deb', '7b056f7a-3883-430c-b948-63d8eafc89a6', 'ai', 'Thank you for your inquiry! I''d be happy to help. For this weekend, we have several family-friendly options:

🏨 Family Deluxe Room (45 sqm): RM 480/night
🏨 Family Suite (70 sqm): RM 720/night

Both include extra beds for children, kids'' welcome amenity, and access to our children''s pool. Shall I check exact availability for your dates?', '2026-02-28 13:02:29+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('9e794069-7a2a-419b-a282-a73e9f4f95e9', '7b056f7a-3883-430c-b948-63d8eafc89a6', 'guest', 'That sounds great! Can I get more details?', '2026-02-28 13:03:29+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('4ef46d4a-edfb-4038-807a-52c21f7fae18', '7b056f7a-3883-430c-b948-63d8eafc89a6', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-28 13:11:29+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('d0375b8b-6fa9-4eba-a9b6-38f16baf1964', '7b056f7a-3883-430c-b948-63d8eafc89a6', 'guest', 'Sure, it''s Omar Hassan, omar.hassan@outlook.com', '2026-02-28 13:17:29+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('e3acf0b2-2d59-4b24-a805-97d904880a7b', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'web', '+60123456019', 'Lisa Anderson', 'active', false, 'concierge', '2026-02-18 19:02:23+00', '2026-02-18 20:44:23+00', '2026-02-18 20:44:23+00', 8);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('ee638cdc-ad5e-4b0c-89a1-56345e8bae70', 'e3acf0b2-2d59-4b24-a805-97d904880a7b', 'guest', 'Do you have a conference room for a corporate event next month?', '2026-02-18 19:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('066753b9-cdc6-428e-9494-d00c3aa04a1f', 'e3acf0b2-2d59-4b24-a805-97d904880a7b', 'ai', 'Hello! We have excellent meeting facilities available. Our Business Center offers:

📋 Boardroom (up to 20 pax): RM 1,500/day
📋 Conference Hall (up to 100 pax): RM 4,500/day
📋 Grand Ballroom (up to 300 pax): RM 8,000/day

All include AV equipment, WiFi, coffee breaks, and a dedicated event coordinator. What size meeting are you planning?', '2026-02-18 19:02:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('db00258c-59a6-4667-9d94-20d1d3558a5a', 'e3acf0b2-2d59-4b24-a805-97d904880a7b', 'guest', 'That sounds great! Can I get more details?', '2026-02-18 19:04:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('66f82be3-518a-4935-8993-087330652709', 'e3acf0b2-2d59-4b24-a805-97d904880a7b', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-18 19:05:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('0baf0914-0f70-4a97-b04a-4bb20207f394', 'e3acf0b2-2d59-4b24-a805-97d904880a7b', 'guest', 'Sure, it''s Lisa Anderson, lisa.a@company.com', '2026-02-18 19:08:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('9a1b8aa4-73fc-4429-a59b-dbec08ace3c4', 'e3acf0b2-2d59-4b24-a805-97d904880a7b', 'ai', 'Wonderful! Thank you, Lisa. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-02-18 19:15:30+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('8f419f0d-7e14-4115-a81d-45c97cd330c1', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456020', 'Tan Wei Ming', 'handed_off', false, 'concierge', '2026-03-01 07:02:23+00', '2026-03-01 08:45:23+00', '2026-03-01 08:45:23+00', 8);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('c1dd7b0c-149d-4fea-a72a-606dd0cadc1a', '8f419f0d-7e14-4115-a81d-45c97cd330c1', 'guest', 'What are the rates for a deluxe room for 3 nights?', '2026-03-01 07:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('78987471-a6bd-490c-b268-b7b0773a2d93', '8f419f0d-7e14-4115-a81d-45c97cd330c1', 'ai', 'Great question! Our rates for the Deluxe Room are:

- Weekday: RM 380/night
- Weekend: RM 450/night
- 3-night package: RM 1,050 (save 8%!)

All rates include daily breakfast buffet, WiFi, and gym access. Would you like me to proceed with a booking?', '2026-03-01 07:02:31+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('2e496e2f-fd6a-4de0-91d0-678add1bbd6c', '8f419f0d-7e14-4115-a81d-45c97cd330c1', 'guest', 'That sounds great! Can I get more details?', '2026-03-01 07:09:31+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('7c9535b5-9f24-4538-9aab-7882d5b1fea7', '8f419f0d-7e14-4115-a81d-45c97cd330c1', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-03-01 07:11:31+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('7e99330d-0ae3-48b7-8d96-13a093ac073d', '8f419f0d-7e14-4115-a81d-45c97cd330c1', 'guest', 'Sure, it''s Tan Wei Ming, weiming.tan@gmail.com', '2026-03-01 07:17:31+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('6aeb4ea6-63f6-4c49-8603-2c8e92ba5ee6', '8f419f0d-7e14-4115-a81d-45c97cd330c1', 'ai', 'Wonderful! Thank you, Tan. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-03-01 07:18:31+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('909c878e-296b-4477-94c7-7fcfa68a4443', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'web', '+60123456021', 'Sophie Martin', 'active', true, 'concierge', '2026-02-27 22:02:23+00', '2026-02-27 22:57:23+00', '2026-02-27 22:57:23+00', 3);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('21dd957f-2b38-4e72-8ff0-714eacca2822', '909c878e-296b-4477-94c7-7fcfa68a4443', 'guest', 'Hi there! I''m looking for a romantic getaway package. What do you recommend?', '2026-02-27 22:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('2fcaf8f1-9206-4c12-8e67-12525f5a1b08', '909c878e-296b-4477-94c7-7fcfa68a4443', 'ai', 'Good evening! Thank you for reaching out to Grand Horizon Resort. Yes, we do have suites available for tomorrow night. Our Executive Suite (65 sqm) is available at RM 850/night, and our Grand Suite (90 sqm) is at RM 1,200/night. Both come with complimentary breakfast, airport shuttle, and access to our infinity pool and spa.

Would you like me to hold one for you? I just need your preferred room type and the number of guests.', '2026-02-27 22:02:37+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('10651e94-97f9-4da0-bc97-44c81519fdda', '909c878e-296b-4477-94c7-7fcfa68a4443', 'guest', 'That sounds great! Can I get more details?', '2026-02-27 22:06:37+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('3b707ddc-9d3c-4ea7-a314-300bf9958ae3', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456022', 'Raj Patel', 'resolved', true, 'handoff', '2026-02-04 06:02:23+00', '2026-02-04 07:50:23+00', '2026-02-04 07:50:23+00', 5);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('f80b5c6d-9678-4837-a73e-6d629eb51846', '3b707ddc-9d3c-4ea7-a314-300bf9958ae3', 'guest', 'Can I book a room with an ocean view for New Year''s Eve?', '2026-02-04 06:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('7f35fdc4-4d6b-4702-83bc-36e0697e2ce2', '3b707ddc-9d3c-4ea7-a314-300bf9958ae3', 'ai', 'Hello! Congratulations on your upcoming wedding! 🎉 We''d love to help you plan your special day. Our Grand Ballroom can comfortably accommodate 200 guests and includes:

- Custom-designed setup with floral arrangements
- 5-course gala dinner with premium beverages
- Complimentary bridal suite for 1 night
- Wedding coordination team

Packages start from RM 280 per person. Shall I arrange a site visit for you?', '2026-02-04 06:02:34+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('258b87e2-cfbf-4910-b5ae-9feb48641d7c', '3b707ddc-9d3c-4ea7-a314-300bf9958ae3', 'guest', 'That sounds great! Can I get more details?', '2026-02-04 06:09:34+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('a0bd630d-a316-40aa-805f-56b1e9db755b', '3b707ddc-9d3c-4ea7-a314-300bf9958ae3', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-04 06:15:34+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('9d857ee0-cffa-4483-993f-4e70a8b39d86', '3b707ddc-9d3c-4ea7-a314-300bf9958ae3', 'guest', 'Sure, it''s Raj Patel, raj.patel@hotmail.com', '2026-02-04 06:21:34+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('6e005fca-1a23-4538-9541-0e49a68a2011', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'email', '+60123456023', 'Anna Kowalski', 'resolved', false, 'handoff', '2026-02-19 16:02:23+00', '2026-02-19 17:06:23+00', '2026-02-19 17:06:23+00', 2);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('ca99b4d5-79b1-45c4-a8d1-a6431c575879', '6e005fca-1a23-4538-9541-0e49a68a2011', 'guest', 'Hello, we need 10 rooms for a company retreat next week. Group discount?', '2026-02-19 16:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('c6050f23-ab5e-43d2-b7f7-501aa0f9574a', '6e005fca-1a23-4538-9541-0e49a68a2011', 'ai', 'Thank you for your inquiry! I''d be happy to help. For this weekend, we have several family-friendly options:

🏨 Family Deluxe Room (45 sqm): RM 480/night
🏨 Family Suite (70 sqm): RM 720/night

Both include extra beds for children, kids'' welcome amenity, and access to our children''s pool. Shall I check exact availability for your dates?', '2026-02-19 16:02:30+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('28ed8ec2-49e3-4671-85d3-d2e95367e1cc', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456024', 'Muhammad Rizki', 'resolved', true, 'lead_capture', '2026-02-28 19:02:23+00', '2026-02-28 20:16:23+00', '2026-02-28 20:16:23+00', 2);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('f1ba99aa-8cc3-4876-a7a5-09a528828900', '28ed8ec2-49e3-4671-85d3-d2e95367e1cc', 'guest', 'Is breakfast included with the standard room?', '2026-02-28 19:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('d1dda7cc-9492-43ec-ac60-655827279b7a', '28ed8ec2-49e3-4671-85d3-d2e95367e1cc', 'ai', 'Hello! We have excellent meeting facilities available. Our Business Center offers:

📋 Boardroom (up to 20 pax): RM 1,500/day
📋 Conference Hall (up to 100 pax): RM 4,500/day
📋 Grand Ballroom (up to 300 pax): RM 8,000/day

All include AV equipment, WiFi, coffee breaks, and a dedicated event coordinator. What size meeting are you planning?', '2026-02-28 19:02:27+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('42c0995f-a325-4f0a-9191-085338b917db', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456025', 'Jennifer Liu', 'resolved', false, 'lead_capture', '2026-02-13 23:02:23+00', '2026-02-13 23:18:23+00', '2026-02-13 23:18:23+00', 8);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('68833f7b-46ab-4605-9e0a-71e343e6b553', '42c0995f-a325-4f0a-9191-085338b917db', 'guest', 'I''d like to inquire about your spa and wellness packages.', '2026-02-13 23:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('ad299dd4-566f-4eee-82f8-72e7dc9030f2', '42c0995f-a325-4f0a-9191-085338b917db', 'ai', 'Great question! Our rates for the Deluxe Room are:

- Weekday: RM 380/night
- Weekend: RM 450/night
- 3-night package: RM 1,050 (save 8%!)

All rates include daily breakfast buffet, WiFi, and gym access. Would you like me to proceed with a booking?', '2026-02-13 23:02:26+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('7238d7f7-8121-4921-a707-7683934bcaba', '42c0995f-a325-4f0a-9191-085338b917db', 'guest', 'That sounds great! Can I get more details?', '2026-02-13 23:09:26+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('b5c4a7af-28f8-4820-ac90-282b54bec7d5', '42c0995f-a325-4f0a-9191-085338b917db', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-13 23:15:26+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('774ea221-a84d-4ae5-a18b-43380e00683a', '42c0995f-a325-4f0a-9191-085338b917db', 'guest', 'Sure, it''s Jennifer Liu, jennifer.liu@gmail.com', '2026-02-13 23:16:26+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('a897f79e-e104-4508-93d9-ee59491cb22e', '42c0995f-a325-4f0a-9191-085338b917db', 'ai', 'Wonderful! Thank you, Jennifer. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-02-13 23:22:26+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('57fa1136-fa90-4423-85d4-fdef7c0dee1f', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456001', 'Sarah Chen', 'resolved', false, 'concierge', '2026-02-14 02:02:23+00', '2026-02-14 02:47:23+00', '2026-02-14 02:47:23+00', 7);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('1a0cba23-0398-449f-8ffd-974bb97c1527', '57fa1136-fa90-4423-85d4-fdef7c0dee1f', 'guest', 'Do you allow pets in the hotel? I have a small dog.', '2026-02-14 02:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('e5a53d90-dc30-48e3-a6f4-b2ae6f38c27c', '57fa1136-fa90-4423-85d4-fdef7c0dee1f', 'ai', 'Good evening! Thank you for reaching out to Grand Horizon Resort. Yes, we do have suites available for tomorrow night. Our Executive Suite (65 sqm) is available at RM 850/night, and our Grand Suite (90 sqm) is at RM 1,200/night. Both come with complimentary breakfast, airport shuttle, and access to our infinity pool and spa.

Would you like me to hold one for you? I just need your preferred room type and the number of guests.', '2026-02-14 02:02:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('d52c7088-5920-4fed-95fa-0100893e1d72', '57fa1136-fa90-4423-85d4-fdef7c0dee1f', 'guest', 'That sounds great! Can I get more details?', '2026-02-14 02:09:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('f730d0fa-5c4b-47c8-b9e3-8d4731634316', '57fa1136-fa90-4423-85d4-fdef7c0dee1f', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-14 02:15:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('d9cb8287-9a95-42c4-aced-a95598675a83', '57fa1136-fa90-4423-85d4-fdef7c0dee1f', 'guest', 'Sure, it''s Sarah Chen, sarah.chen@gmail.com', '2026-02-14 02:16:36+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('bfef5892-b15e-4682-accd-b9d1425966c1', '57fa1136-fa90-4423-85d4-fdef7c0dee1f', 'ai', 'Wonderful! Thank you, Sarah. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-02-14 02:21:36+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('b75e1983-cd9c-4c9c-bfcd-4f678c2398a4', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456002', 'Michael Rodriguez', 'active', false, 'lead_capture', '2026-02-17 09:02:23+00', '2026-02-17 10:42:23+00', '2026-02-17 10:42:23+00', 2);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('0ae58704-94a1-43c1-b299-9d64920d87f1', 'b75e1983-cd9c-4c9c-bfcd-4f678c2398a4', 'guest', 'What time is check-in and check-out?', '2026-02-17 09:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('8a7e5a31-8ead-4121-bd84-5675b69707a1', 'b75e1983-cd9c-4c9c-bfcd-4f678c2398a4', 'ai', 'Hello! Congratulations on your upcoming wedding! 🎉 We''d love to help you plan your special day. Our Grand Ballroom can comfortably accommodate 200 guests and includes:

- Custom-designed setup with floral arrangements
- 5-course gala dinner with premium beverages
- Complimentary bridal suite for 1 night
- Wedding coordination team

Packages start from RM 280 per person. Shall I arrange a site visit for you?', '2026-02-17 09:02:32+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('7c16ab1f-fe16-4646-b98b-707a80f90b4e', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'email', '+60123456003', 'Aisha binti Karim', 'active', true, 'handoff', '2026-02-22 03:02:23+00', '2026-02-22 04:23:23+00', '2026-02-22 04:23:23+00', 6);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('05394bf6-442f-4625-8608-6cb1c7bad8c9', '7c16ab1f-fe16-4646-b98b-707a80f90b4e', 'guest', 'Can you arrange airport pickup for us? We arrive at 3 PM.', '2026-02-22 03:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('909fcd03-9834-4da3-b0a4-b9f91f148b90', '7c16ab1f-fe16-4646-b98b-707a80f90b4e', 'ai', 'Thank you for your inquiry! I''d be happy to help. For this weekend, we have several family-friendly options:

🏨 Family Deluxe Room (45 sqm): RM 480/night
🏨 Family Suite (70 sqm): RM 720/night

Both include extra beds for children, kids'' welcome amenity, and access to our children''s pool. Shall I check exact availability for your dates?', '2026-02-22 03:02:31+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('1fce5931-7d7a-4896-919b-b6d824c6f97c', '7c16ab1f-fe16-4646-b98b-707a80f90b4e', 'guest', 'That sounds great! Can I get more details?', '2026-02-22 03:04:31+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('4c442155-92cf-4a34-9cbd-61e6e0ede33f', '7c16ab1f-fe16-4646-b98b-707a80f90b4e', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-22 03:09:31+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('07e0a189-d494-40cf-9022-0cc965765be8', '7c16ab1f-fe16-4646-b98b-707a80f90b4e', 'guest', 'Sure, it''s Aisha binti Karim, aisha.karim@yahoo.com', '2026-02-22 03:15:31+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('663a7330-a88c-41db-939e-b15fb3e8965c', '7c16ab1f-fe16-4646-b98b-707a80f90b4e', 'ai', 'Wonderful! Thank you, Aisha. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-02-22 03:20:31+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('dd8bb11e-ed67-4da8-a05a-34cd5eafd49b', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'email', '+60123456004', 'James O''Brien', 'resolved', true, 'concierge', '2026-02-08 15:02:23+00', '2026-02-08 16:32:23+00', '2026-02-08 16:32:23+00', 5);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('bebd7cb3-8380-464f-8465-d62271c96300', 'dd8bb11e-ed67-4da8-a05a-34cd5eafd49b', 'guest', 'I need a room with wheelchair accessibility. What options do you have?', '2026-02-08 15:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('43f6b889-aa2a-4313-830d-4ef8c361177c', 'dd8bb11e-ed67-4da8-a05a-34cd5eafd49b', 'ai', 'Hello! We have excellent meeting facilities available. Our Business Center offers:

📋 Boardroom (up to 20 pax): RM 1,500/day
📋 Conference Hall (up to 100 pax): RM 4,500/day
📋 Grand Ballroom (up to 300 pax): RM 8,000/day

All include AV equipment, WiFi, coffee breaks, and a dedicated event coordinator. What size meeting are you planning?', '2026-02-08 15:02:29+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('af5070c9-2e91-4b50-b54b-a4a4e3d98797', 'dd8bb11e-ed67-4da8-a05a-34cd5eafd49b', 'guest', 'That sounds great! Can I get more details?', '2026-02-08 15:11:29+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('c5e7334d-7f76-49aa-8e57-3a1128f199b8', 'dd8bb11e-ed67-4da8-a05a-34cd5eafd49b', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-08 15:12:29+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('9b358279-455d-475d-a905-a6bae3be50be', 'dd8bb11e-ed67-4da8-a05a-34cd5eafd49b', 'guest', 'Sure, it''s James O''Brien, james.obrien@icloud.com', '2026-02-08 15:15:29+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('bc3e49e5-1e30-4134-a33d-aa8158e3eb7e', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456005', 'Fatimah Zahra', 'resolved', false, 'handoff', '2026-02-23 15:02:23+00', '2026-02-23 16:45:23+00', '2026-02-23 16:45:23+00', 7);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('0cebd095-5bec-41f0-91a4-58597586630b', 'bc3e49e5-1e30-4134-a33d-aa8158e3eb7e', 'guest', 'Are there any special promotions for the lunar new year period?', '2026-02-23 15:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('5048b328-2623-447c-9e33-2aac74885205', 'bc3e49e5-1e30-4134-a33d-aa8158e3eb7e', 'ai', 'Great question! Our rates for the Deluxe Room are:

- Weekday: RM 380/night
- Weekend: RM 450/night
- 3-night package: RM 1,050 (save 8%!)

All rates include daily breakfast buffet, WiFi, and gym access. Would you like me to proceed with a booking?', '2026-02-23 15:02:32+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('59ece45a-5d12-4658-ba0a-10bcedccf7d3', 'bc3e49e5-1e30-4134-a33d-aa8158e3eb7e', 'guest', 'That sounds great! Can I get more details?', '2026-02-23 15:06:32+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('bfca7d0f-67bf-4f2a-b31e-e28cec80f537', 'bc3e49e5-1e30-4134-a33d-aa8158e3eb7e', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-23 15:08:32+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('b59db77d-6bf6-40f3-b90d-55c803f426d9', 'bc3e49e5-1e30-4134-a33d-aa8158e3eb7e', 'guest', 'Sure, it''s Fatimah Zahra, fatimah.z@hotmail.com', '2026-02-23 15:15:32+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('7d10f597-67bd-46cb-93ce-d69c780e60ee', 'bc3e49e5-1e30-4134-a33d-aa8158e3eb7e', 'ai', 'Wonderful! Thank you, Fatimah. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-02-23 15:25:32+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('e021f7b5-21d1-49c9-8c7f-05a33cd58f19', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456006', 'David Kim', 'active', false, 'handoff', '2026-02-28 15:02:23+00', '2026-02-28 16:37:23+00', '2026-02-28 16:37:23+00', 5);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('3ea8b8df-3109-4e95-83bb-c3023215da7c', 'e021f7b5-21d1-49c9-8c7f-05a33cd58f19', 'guest', 'Can I get a late check-out on Sunday? We have an afternoon flight.', '2026-02-28 15:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('549a3a1c-a00e-4140-a206-995062f9d6d2', 'e021f7b5-21d1-49c9-8c7f-05a33cd58f19', 'ai', 'Good evening! Thank you for reaching out to Grand Horizon Resort. Yes, we do have suites available for tomorrow night. Our Executive Suite (65 sqm) is available at RM 850/night, and our Grand Suite (90 sqm) is at RM 1,200/night. Both come with complimentary breakfast, airport shuttle, and access to our infinity pool and spa.

Would you like me to hold one for you? I just need your preferred room type and the number of guests.', '2026-02-28 15:02:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('4c3c8043-44f5-4387-8570-83a6566d4c76', 'e021f7b5-21d1-49c9-8c7f-05a33cd58f19', 'guest', 'That sounds great! Can I get more details?', '2026-02-28 15:06:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('d7e13237-ac73-493b-abb0-9708ee7f5e9f', 'e021f7b5-21d1-49c9-8c7f-05a33cd58f19', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-28 15:08:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('f83323f1-48ad-4eac-9082-a522c89d053d', 'e021f7b5-21d1-49c9-8c7f-05a33cd58f19', 'guest', 'Sure, it''s David Kim, dkim@gmail.com', '2026-02-28 15:09:30+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('297f9134-7f5e-4464-bbc6-d69aa09c334c', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'web', '+60123456007', 'Priya Sharma', 'handed_off', false, 'lead_capture', '2026-03-03 13:02:23+00', '2026-03-03 14:23:23+00', '2026-03-03 14:23:23+00', 8);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('7e2613f6-033a-4829-90f1-8a5e0b13f6d5', '297f9134-7f5e-4464-bbc6-d69aa09c334c', 'guest', 'What''s the cancellation policy for bookings?', '2026-03-03 13:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('aaf4136b-b72c-4d7f-b89f-77c29a152fe5', '297f9134-7f5e-4464-bbc6-d69aa09c334c', 'ai', 'Hello! Congratulations on your upcoming wedding! 🎉 We''d love to help you plan your special day. Our Grand Ballroom can comfortably accommodate 200 guests and includes:

- Custom-designed setup with floral arrangements
- 5-course gala dinner with premium beverages
- Complimentary bridal suite for 1 night
- Wedding coordination team

Packages start from RM 280 per person. Shall I arrange a site visit for you?', '2026-03-03 13:02:38+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('37b88c04-7ce2-4017-9b0c-628830db370e', '297f9134-7f5e-4464-bbc6-d69aa09c334c', 'guest', 'That sounds great! Can I get more details?', '2026-03-03 13:04:38+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('ff2e8fdd-40f9-4e76-b73f-fa0e3653bb18', '297f9134-7f5e-4464-bbc6-d69aa09c334c', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-03-03 13:06:38+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('f2a1a251-bf7b-43d9-9ec3-a3169d044276', '297f9134-7f5e-4464-bbc6-d69aa09c334c', 'guest', 'Sure, it''s Priya Sharma, priya.sharma@company.com', '2026-03-03 13:09:38+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('c70fefc8-a478-49bc-9003-949f8ba13d1d', '297f9134-7f5e-4464-bbc6-d69aa09c334c', 'ai', 'Wonderful! Thank you, Priya. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-03-03 13:12:38+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('9d9651ed-6057-463a-a1a5-b86b13806e8b', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456008', 'Thomas Weber', 'resolved', false, 'handoff', '2026-02-24 05:02:23+00', '2026-02-24 06:08:23+00', '2026-02-24 06:08:23+00', 6);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('ea5e3244-5099-4858-bdde-f7eec92e11db', '9d9651ed-6057-463a-a1a5-b86b13806e8b', 'guest', 'Do you have interconnecting rooms? We''re traveling with kids.', '2026-02-24 05:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('66013fd7-86db-4dfa-8321-9d71bc3ac624', '9d9651ed-6057-463a-a1a5-b86b13806e8b', 'ai', 'Thank you for your inquiry! I''d be happy to help. For this weekend, we have several family-friendly options:

🏨 Family Deluxe Room (45 sqm): RM 480/night
🏨 Family Suite (70 sqm): RM 720/night

Both include extra beds for children, kids'' welcome amenity, and access to our children''s pool. Shall I check exact availability for your dates?', '2026-02-24 05:02:37+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('7fb0b11d-f885-42d6-84a1-96f4dc5e50b4', '9d9651ed-6057-463a-a1a5-b86b13806e8b', 'guest', 'That sounds great! Can I get more details?', '2026-02-24 05:11:37+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('dd32b446-627f-4df7-a57b-9f8035111ba0', '9d9651ed-6057-463a-a1a5-b86b13806e8b', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-24 05:17:37+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('0cce5dd3-05a5-4c26-b335-696c20794116', '9d9651ed-6057-463a-a1a5-b86b13806e8b', 'guest', 'Sure, it''s Thomas Weber, t.weber@gmail.com', '2026-02-24 05:24:37+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('c30b1be4-8b0a-4496-82c1-558a8b868213', '9d9651ed-6057-463a-a1a5-b86b13806e8b', 'ai', 'Wonderful! Thank you, Thomas. I''ve noted your details. Our reservations team will reach out shortly with a personalized quote. Is there anything else I can help you with?', '2026-02-24 05:31:37+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('47d8757c-5891-488b-8fa0-d9e2cd4b7f4b', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'whatsapp', '+60123456009', 'Nur Aisyah', 'resolved', false, 'handoff', '2026-02-10 11:02:23+00', '2026-02-10 12:14:23+00', '2026-02-10 12:14:23+00', 5);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('04137943-1bb7-4b49-bf09-edbe790eacd5', '47d8757c-5891-488b-8fa0-d9e2cd4b7f4b', 'guest', 'Is there parking available at the hotel?', '2026-02-10 11:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('211a99a2-a2da-4b26-b3eb-94c415f09537', '47d8757c-5891-488b-8fa0-d9e2cd4b7f4b', 'ai', 'Hello! We have excellent meeting facilities available. Our Business Center offers:

📋 Boardroom (up to 20 pax): RM 1,500/day
📋 Conference Hall (up to 100 pax): RM 4,500/day
📋 Grand Ballroom (up to 300 pax): RM 8,000/day

All include AV equipment, WiFi, coffee breaks, and a dedicated event coordinator. What size meeting are you planning?', '2026-02-10 11:02:37+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('9b014d93-2690-4a70-85c0-b1f06067e4e1', '47d8757c-5891-488b-8fa0-d9e2cd4b7f4b', 'guest', 'That sounds great! Can I get more details?', '2026-02-10 11:06:37+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('e1110d9d-ac2a-441c-a1b8-4fa9c024f5e7', '47d8757c-5891-488b-8fa0-d9e2cd4b7f4b', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-10 11:10:37+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('9bb54982-07b7-48b4-9418-e11f9b6297bf', '47d8757c-5891-488b-8fa0-d9e2cd4b7f4b', 'guest', 'Sure, it''s Nur Aisyah, nuraisyah@gmail.com', '2026-02-10 11:19:37+00');

INSERT INTO conversations (id, property_id, channel, guest_identifier, guest_name, status, is_after_hours, ai_mode, started_at, last_message_at, last_interaction_at, message_count)
VALUES ('c1dd45ce-d54b-48c1-9f15-d6385b29e02e', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'email', '+60123456010', 'Robert Taylor', 'active', false, 'concierge', '2026-02-18 06:02:23+00', '2026-02-18 07:08:23+00', '2026-02-18 07:08:23+00', 5);

INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('1c0e6124-7b76-4c33-a3a7-e5cc86ce6256', 'c1dd45ce-d54b-48c1-9f15-d6385b29e02e', 'guest', 'I''d like to book the presidential suite for my anniversary.', '2026-02-18 06:02:23+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('e577f8da-0832-4b66-989d-138235a92cf4', 'c1dd45ce-d54b-48c1-9f15-d6385b29e02e', 'ai', 'Great question! Our rates for the Deluxe Room are:

- Weekday: RM 380/night
- Weekend: RM 450/night
- 3-night package: RM 1,050 (save 8%!)

All rates include daily breakfast buffet, WiFi, and gym access. Would you like me to proceed with a booking?', '2026-02-18 06:02:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('c2f62f87-09a4-4948-bfa4-df8189708531', 'c1dd45ce-d54b-48c1-9f15-d6385b29e02e', 'guest', 'That sounds great! Can I get more details?', '2026-02-18 06:06:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('145058a8-41b2-4aaf-8b0c-8da4e221370c', 'c1dd45ce-d54b-48c1-9f15-d6385b29e02e', 'ai', 'Of course! To proceed with the reservation, may I have your full name and email address? This way I can send you a confirmation with all the details.', '2026-02-18 06:14:30+00');
INSERT INTO messages (id, conversation_id, role, content, sent_at)
VALUES ('d691e302-8906-4255-8220-7e2a67e0246b', 'c1dd45ce-d54b-48c1-9f15-d6385b29e02e', 'guest', 'Sure, it''s Robert Taylor, robert.t@yahoo.com', '2026-02-18 06:23:30+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('e8a2553f-b00a-4aa0-8c52-655c7e9428bf', '347d700f-566f-442f-bfed-1e29bf4c83bc', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Sarah Chen', '+60123456001', 'sarah.chen@gmail.com', 'fb_inquiry', 'whatsapp', false, 'qualified', 850, NULL, 'standard', NULL, '2026-02-15 17:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('6c3088c2-1337-4a9c-8d1a-749d2bff285c', 'ca37d9aa-01f1-484a-903f-dececa4a61ac', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Michael Rodriguez', '+60123456002', 'm.rodriguez@outlook.com', 'fb_inquiry', 'web', true, 'new', 850, NULL, 'standard', NULL, '2026-02-20 19:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('43d84e08-23f5-4558-9e16-117891ab3278', 'd94d92d6-0a96-4a8c-b9b1-0fa2ea44e71a', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Aisha binti Karim', '+60123456003', 'aisha.karim@yahoo.com', 'fb_inquiry', 'web', false, 'contacted', 16240, NULL, 'high_value', 'Corporate event', '2026-02-16 18:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('8abac479-50bf-42a0-836f-36fbe9ca22f9', '42c33600-bd20-402e-9e64-c327ed68279b', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'James O''Brien', '+60123456004', 'james.obrien@icloud.com', 'fb_inquiry', 'web', false, 'new', 850, NULL, 'standard', NULL, '2026-02-23 17:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('454be628-4783-4c1d-a8a6-015f3d201ea0', '0cb32fa1-9ae5-4e0c-b566-33f253cec100', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Fatimah Zahra', '+60123456005', 'fatimah.z@hotmail.com', 'room_booking', 'email', false, 'contacted', 720, NULL, 'standard', NULL, '2026-02-05 20:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('79a989b6-4d39-4d9c-a008-a010f8c225a2', '20ee0b89-176b-4c88-82b3-df96ca794024', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'David Kim', '+60123456006', 'dkim@gmail.com', 'room_booking', 'web', false, 'contacted', 2400, NULL, 'high_value', 'Long-stay booking', '2026-02-04 20:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('6bbdede0-417e-458c-ab19-f0340f37eba3', 'b4cbc592-67a2-4760-bea6-7c1e9b0451be', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Priya Sharma', '+60123456007', 'priya.sharma@company.com', 'room_booking', 'web', false, 'qualified', 850, NULL, 'standard', NULL, '2026-02-08 23:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('55b12eca-70db-47e9-8774-b83882f15305', '3c24759e-bbe7-423e-9502-28bd878c9c8d', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Thomas Weber', '+60123456008', 't.weber@gmail.com', 'room_booking', 'web', false, 'contacted', 350, NULL, 'standard', NULL, '2026-02-14 03:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('b88431c4-6943-43ed-8f3d-a9c28215ed6d', '8b656d13-2800-4941-abdc-edb3a556a64c', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Nur Aisyah', '+60123456009', 'nuraisyah@gmail.com', 'event', 'whatsapp', false, 'converted', 41720, 48604.51, 'high_value', 'VIP guest', '2026-02-16 19:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('3c400d5f-2285-4108-9a98-5450b068b648', 'e175b561-b9a7-4504-aecf-74146c73c7e0', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Robert Taylor', '+60123456010', 'robert.t@yahoo.com', 'event', 'email', false, 'converted', 2400, 2426.42, 'high_value', 'Wedding reception', '2026-02-19 17:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('0af8e949-9f27-4f1d-8671-2c590cb72eb0', '9e14d40f-8422-4333-8ed2-5d0840eaf295', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Lena Fischer', '+60123456011', 'lena.fischer@web.de', 'room_booking', 'whatsapp', false, 'converted', 8000, 8420.51, 'high_value', 'Corporate event', '2026-02-28 19:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('361c8915-3883-4b14-98fc-fc750d1f9fb8', '684d9ddd-345b-4332-8a16-6ebfec3d541d', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Ahmad Faisal', '+60123456012', 'ahmadfaisal@gmail.com', 'event', 'whatsapp', false, 'contacted', 4500, NULL, 'high_value', 'Corporate event', '2026-02-11 04:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('d2b47cd6-2936-4ede-9121-c05a1ecf7815', '5c44785f-0de9-49b2-9088-ec229105f1ce', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Emily Watson', '+60123456013', 'e.watson@outlook.com', 'room_booking', 'web', false, 'contacted', 480, NULL, 'standard', NULL, '2026-02-26 20:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('e8571876-22d7-4bc7-b625-cb0219d48a36', '149eebfc-03eb-4c26-b9cf-3de4ba82aa44', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Hiroshi Tanaka', '+60123456014', 'h.tanaka@jp.company.com', 'fb_inquiry', 'whatsapp', false, 'new', 8000, NULL, 'high_value', 'Corporate event', '2026-02-20 02:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('85e1efa8-856d-438a-a57e-3b3ef6649161', 'f2b312e0-bb4f-47d1-b38b-3a78216b255d', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Siti Nurhaliza', '+60123456015', 'siti.n@gmail.com', 'room_booking', 'whatsapp', false, 'contacted', 40320, NULL, 'high_value', 'Long-stay booking', '2026-02-05 18:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('9e155a57-48e1-4626-8f14-00fd9c3505d4', '54524ed6-3c49-4094-9fdc-597cbff90edd', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Carlos Mendez', '+60123456016', 'carlos.m@gmail.com', 'event', 'whatsapp', false, 'qualified', 1500, NULL, 'standard', NULL, '2026-02-24 01:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('9c683629-6e59-4f74-a2ef-c1164fb5d056', '6c0757bd-65e3-4ccc-9afa-cf68a5577b9f', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Rachel Green', '+60123456017', 'rachel.green@gmail.com', 'fb_inquiry', 'email', true, 'qualified', 850, NULL, 'standard', NULL, '2026-02-06 21:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('67eaa178-9c72-4bc3-9687-b021d216877a', 'da8c7ff5-f030-4799-b4ef-953ca1dcc44a', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Omar Hassan', '+60123456018', 'omar.hassan@outlook.com', 'event', 'whatsapp', false, 'new', 8000, NULL, 'high_value', 'VIP guest', '2026-02-13 17:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('64fc52a0-721a-4e35-9a0c-ca8e51fd0cb5', 'a6d194c3-2ae3-4086-b84d-e1b0a7cb1786', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Lisa Anderson', '+60123456019', 'lisa.a@company.com', 'room_booking', 'email', false, 'converted', 20440, 19855.26, 'high_value', 'VIP guest', '2026-02-17 02:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('e6daf117-826e-4aa4-84ef-e13c3c36de8e', '9ace0ee1-9fb4-4b33-881e-5cfe2debe529', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Tan Wei Ming', '+60123456020', 'weiming.tan@gmail.com', 'general', 'web', false, 'new', 1200, NULL, 'standard', NULL, '2026-02-12 04:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('73d6fae0-e83c-4321-bae5-9bf3fb1695fa', '602b988e-453e-4c6c-a37a-b79c9999358f', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Sophie Martin', '+60123456021', 'sophie.m@gmail.com', 'general', 'whatsapp', false, 'new', 4500, NULL, 'high_value', 'Wedding reception', '2026-02-26 01:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('4cebe5dd-679d-4d31-bfb0-552c827ac8dc', '617470c2-5945-4ee8-9984-cf0030dccad4', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Raj Patel', '+60123456022', 'raj.patel@hotmail.com', 'room_booking', 'whatsapp', true, 'converted', 33880, 28006.78, 'high_value', 'Long-stay booking', '2026-02-10 19:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('74448522-7edf-4881-9bab-206a0935c239', '9e3e34ff-108b-4c65-8a61-a22ee6a06ede', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Anna Kowalski', '+60123456023', 'anna.k@gmail.com', 'fb_inquiry', 'email', false, 'new', 850, NULL, 'standard', NULL, '2026-02-25 22:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('33fc1c8e-4fbe-4f01-aa34-6e9e26bfa447', '05dc4ee5-938e-4ae8-84ca-390a6396d3b8', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Muhammad Rizki', '+60123456024', 'rizki.m@yahoo.com', 'room_booking', 'whatsapp', false, 'contacted', 39200, NULL, 'high_value', 'Corporate event', '2026-02-05 04:02:23+00');

INSERT INTO leads (id, conversation_id, property_id, guest_name, guest_phone, guest_email, intent, source_channel, is_after_hours, status, estimated_value, actual_revenue, priority, flag_reason, captured_at)
VALUES ('1ce4f526-8543-41d5-8d28-d9d817d36528', '81a44c21-0c55-4952-a871-0fbbcb68baaf', '6ac91eab-99f5-4020-91c1-49abebd2d860', 'Jennifer Liu', '+60123456025', 'jennifer.liu@gmail.com', 'event', 'whatsapp', true, 'converted', 480, 531.04, 'standard', NULL, '2026-02-14 00:02:23+00');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('55b0aa22-7ec8-463f-947e-003ad1630d34', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-05', 13, 5, 4, 3, 0, 13, 0, 3.62, 2386.09, 0, 515.34, '{"whatsapp": 7, "web": 2, "email": 1}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('619bf61a-01ec-4361-b870-6a4a8a9d6b35', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-06', 5, 1, 0, 1, 1, 4, 1, 2.84, 770.35, 0, 218.26, '{"whatsapp": 3, "web": 0, "email": 0}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('393e6a1b-d65b-4c72-80ab-ce1b0fc33f9f', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-07', 24, 6, 5, 6, 2, 22, 2, 2.65, 2667.57, 0, 914.7, '{"whatsapp": 12, "web": 5, "email": 3}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('cb0e4c8e-f221-4971-9f38-03743c3a25d0', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-08', 19, 8, 6, 2, 0, 19, 0, 2.9, 1147.54, 0, 545.76, '{"whatsapp": 11, "web": 3, "email": 1}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('5e774be7-40b1-4daa-8d89-7fd12cd1fb9c', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-09', 14, 6, 5, 3, 0, 14, 0, 7.95, 1199.74, 0, 619.63, '{"whatsapp": 8, "web": 3, "email": 1}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('acb51da1-871b-42ac-a4e5-73e356461efd', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-10', 6, 2, 1, 1, 1, 5, 1, 5.08, 658.38, 0, 269.39, '{"whatsapp": 4, "web": 1, "email": 0}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('c86654da-ee35-4687-bcce-9675d7e4a067', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-11', 15, 7, 6, 2, 1, 14, 1, 5.98, 1040.85, 0, 460.66, '{"whatsapp": 8, "web": 2, "email": 0}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('04f0367b-831f-419a-8b70-0a18f775614f', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-12', 5, 1, 0, 2, 1, 4, 1, 7.86, 745.5, 0, 208.89, '{"whatsapp": 2, "web": 1, "email": 0}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('30b852e2-dddb-4874-8c72-999f8974a6d4', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-13', 18, 5, 4, 1, 0, 18, 0, 3.65, 397.33, 0, 727.01, '{"whatsapp": 11, "web": 4, "email": 2}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('af91c06a-625a-4424-bda3-9b3c8b13a0e2', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-14', 29, 14, 12, 6, 0, 29, 0, 3.71, 3320.89, 0, 850.38, '{"whatsapp": 15, "web": 7, "email": 4}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('614d4b06-e7b4-4d32-95a3-ada017ec609c', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-15', 33, 9, 8, 2, 1, 32, 1, 3.18, 1062.26, 0, 1067.9, '{"whatsapp": 21, "web": 6, "email": 4}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('9b8ca721-f06d-46d3-abfc-b827fb2a03c0', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-16', 14, 5, 4, 4, 1, 13, 1, 6.42, 2878.31, 0, 561.16, '{"whatsapp": 8, "web": 3, "email": 1}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('32ebf447-3b08-4d25-9aef-49f88ba799bd', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-17', 14, 6, 5, 4, 0, 14, 0, 4.72, 1650.78, 0, 453.0, '{"whatsapp": 7, "web": 2, "email": 1}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('07f8a420-d8d3-43c8-be2e-11fdfd509ee5', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-18', 18, 7, 6, 1, 1, 17, 1, 4.14, 747.67, 0, 710.2, '{"whatsapp": 10, "web": 2, "email": 1}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('87f5b7af-741b-46e2-8862-b4868d1ba1f2', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-19', 12, 4, 3, 3, 1, 11, 1, 2.76, 1861.34, 0, 440.97, '{"whatsapp": 7, "web": 2, "email": 0}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('1c7d4740-addc-417d-8d5b-7cf5663d7d9a', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-20', 19, 6, 5, 3, 1, 18, 1, 3.37, 1271.29, 0, 797.99, '{"whatsapp": 11, "web": 3, "email": 2}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('028f7473-0fa5-48d1-afd6-cff304cb495d', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-21', 16, 6, 5, 1, 1, 15, 1, 4.84, 475.55, 0, 534.62, '{"whatsapp": 8, "web": 2, "email": 1}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('94f19671-50d3-4b6f-9a7b-6ce97be851b9', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-22', 35, 17, 15, 9, 1, 34, 1, 6.17, 4505.45, 0, 1484.26, '{"whatsapp": 20, "web": 10, "email": 4}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('3745cb72-0a1e-4339-b919-294a297e34dc', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-23', 5, 2, 1, 2, 1, 4, 1, 6.78, 1563.24, 0, 168.94, '{"whatsapp": 2, "web": 1, "email": 0}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('4c559f78-bf94-4c24-9233-aa14d4d159c6', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-24', 19, 6, 5, 3, 0, 19, 0, 7.9, 1261.45, 0, 592.37, '{"whatsapp": 12, "web": 3, "email": 1}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('54807f43-be56-4e36-8b4a-ec96f2d8cc52', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-25', 14, 4, 3, 1, 1, 13, 1, 4.36, 511.54, 0, 442.23, '{"whatsapp": 7, "web": 4, "email": 1}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('8c29f75c-8f15-4dda-9e36-8409f905cbba', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-26', 12, 4, 3, 2, 1, 11, 1, 6.64, 972.99, 0, 316.72, '{"whatsapp": 6, "web": 3, "email": 0}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('db5540d4-3f93-4c11-8f4b-03e0a216e91a', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-27', 20, 6, 5, 1, 0, 20, 0, 7.24, 432.52, 0, 812.98, '{"whatsapp": 10, "web": 3, "email": 2}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('721ab023-9d56-4513-abc4-a04bdcd63b2c', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-02-28', 31, 11, 9, 9, 1, 30, 1, 4.69, 3692.98, 0, 1183.68, '{"whatsapp": 16, "web": 6, "email": 3}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('0b2c68c3-24a0-4e54-b343-74e26ad2180a', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-03-01', 15, 4, 3, 3, 1, 14, 1, 4.22, 2164.98, 0, 671.59, '{"whatsapp": 7, "web": 2, "email": 1}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('7af5c25f-2ba4-4b9e-b53f-75d647b09920', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-03-02', 6, 1, 0, 1, 1, 5, 1, 5.38, 782.05, 0, 203.22, '{"whatsapp": 3, "web": 1, "email": 0}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('aa465659-38d3-48f2-a6e3-01f24e947373', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-03-03', 12, 4, 3, 1, 1, 11, 1, 6.58, 618.95, 0, 468.35, '{"whatsapp": 8, "web": 3, "email": 0}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('9838b3c6-28d8-44dc-adab-7478ac86b96f', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-03-04', 15, 6, 5, 2, 1, 14, 1, 6.98, 752.57, 0, 447.82, '{"whatsapp": 8, "web": 3, "email": 2}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('61295c47-192e-46c4-8700-843748dc2451', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-03-05', 13, 5, 4, 3, 1, 12, 1, 6.24, 1541.01, 0, 479.47, '{"whatsapp": 7, "web": 3, "email": 1}');

INSERT INTO analytics_daily (id, property_id, report_date, total_inquiries, after_hours_inquiries, after_hours_responded, leads_captured, handoffs, inquiries_handled_by_ai, inquiries_handled_manually, avg_response_time_sec, estimated_revenue_recovered, actual_revenue_recovered, cost_savings, channel_breakdown)
VALUES ('c492fae5-7ca6-4354-aec4-6e7615f7c73c', '6ac91eab-99f5-4020-91c1-49abebd2d860', '2026-03-06', 12, 4, 3, 3, 1, 11, 1, 3.89, 2342.89, 0, 461.01, '{"whatsapp": 8, "web": 2, "email": 1}');

COMMIT;
