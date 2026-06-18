import re
import os

file_path = r"d:\repos\mvp-research-sheerssoft\backend\app\models.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Rename Property to Business (Class name)
content = re.sub(r'\bclass Property\(Base\):', 'class Business(Base):', content)
content = re.sub(r'\bProperty\b', 'Business', content)
content = re.sub(r'__tablename__ = "properties"', '__tablename__ = "businesses"', content)

# 2. Rename fields and variables
content = re.sub(r'\bproperty_id\b', 'business_id', content)
content = re.sub(r'\bproperties\b', 'businesses', content)
content = re.sub(r'\baccessible_property_ids\b', 'accessible_business_ids', content)
content = re.sub(r'\bproperty_name\b', 'business_name', content)

# 3. Clean up Tenant model
content = re.sub(r'performance_fee_balance_rm.*?\n.*?\n', '', content)

# 4. Clean up Business (formerly Property) hotel fields
fields_to_remove = [
    r'adr: Mapped\[Decimal\].*?\n.*?\n',
    r'ota_commission_pct: Mapped\[Decimal\].*?\n.*?\n',
    r'hourly_rate: Mapped\[Decimal\].*?\n.*?\n',
    r'avg_stay_nights: Mapped\[float\].*?\n',
    r'audit_only_mode.*?\n',
    r'shadow_pilot_start_date.*?\n',
    r'shadow_pilot_phone.*?\n',
    r'shadow_pilot_mode.*?\n',
    r'shadow_pilot_session_active.*?\n',
    r'shadow_pilot_session_last_seen.*?\n',
    r'shadow_pilot_dashboard_token.*?\n',
    r'shadow_pilot_dashboard_token_expires.*?\n',
    r'shadow_pilot_report_sent_at.*?\n',
    r'audit_estimated_monthly_leakage_rm.*?\n'
]

for pattern in fields_to_remove:
    content = re.sub(pattern, '', content)

# Add generic business fields to Business
business_additions = """    industry: Mapped[str | None] = mapped_column(String(255))
    business_url: Mapped[str | None] = mapped_column(String(500))
    booking_link: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
"""
content = re.sub(r'    created_at: Mapped\[datetime\] = mapped_column\(', business_additions, content, count=1)

# 5. Remove AuditRecord entirely
content = re.sub(r'class AuditRecord\(Base\):.*?(?=\n\n# ─)', '', content, flags=re.DOTALL)

# 6. Remove ShadowPilotConversation entirely
content = re.sub(r'class ShadowPilotConversation\(Base\):.*?(?=\n\nclass ShadowPilotAnalyticsDaily)', '', content, flags=re.DOTALL)

# 7. Remove ShadowPilotAnalyticsDaily entirely
content = re.sub(r'class ShadowPilotAnalyticsDaily\(Base\):.*', '', content, flags=re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Refactored models.py successfully.")
