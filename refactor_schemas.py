import re
import os

file_path = r"d:\repos\mvp-research-sheerssoft\backend\app\schemas.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update BusinessResponse
content = re.sub(
    r'    adr: float\n    ota_commission_pct: float\n    hourly_rate: float\n',
    '    industry: str | None = None\n    business_url: str | None = None\n    booking_link: str | None = None\n',
    content
)

# 2. Update BusinessCreateRequest
content = re.sub(
    r'    adr: float = 230\.00\n    ota_commission_pct: float = 20\.00\n    hourly_rate: float = 25\.00\n',
    '    industry: str | None = None\n    business_url: str | None = None\n    booking_link: str | None = None\n',
    content
)

# 3. Update BusinessSettingsUpdateRequest
content = re.sub(
    r'    adr: float \| None = None\n    hourly_rate: float \| None = None\n',
    '    industry: str | None = None\n    business_url: str | None = None\n    booking_link: str | None = None\n',
    content
)

# 4. Update ApplicationCreateRequest
content = re.sub(r'    hotel_name: str = Field\(..., min_length=1, max_length=255\)\n', '', content)
content = re.sub(r'    room_count: int \| None = None\n', '', content)
content = re.sub(r'    adr_estimate: float \| None = None\n', '', content)
content = re.sub(r'    star_rating: int \| None = None\n', '', content)
# We have a business_name: str | None = None already. Let's make it required.
content = re.sub(r'    business_name: str \| None = None\n', '    business_name: str = Field(..., min_length=1, max_length=255)\n', content)

# 5. Update ApplicationResponse
content = re.sub(r'    hotel_name: str\n', '    business_name: str\n', content)
content = re.sub(r'    room_count: int \| None\n', '', content)

# 6. Update Analytics Responses
content = re.sub(r'    estimated_revenue_recovered: float\n', '', content)
content = re.sub(r'    cost_savings: float\n', '', content)

# 7. Update DashboardStatsResponse
content = re.sub(r'    estimated_revenue_recovered: float = 0.0\n', '', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated schemas.py")
