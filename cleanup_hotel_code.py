import os
import re

backend_dir = r"d:\repos\mvp-research-sheerssoft\backend\app"

# 1. Delete hotel-specific files
files_to_delete = [
    r"routes\audit.py",
    r"routes\shadow_pilot_public.py",
    r"services\shadow_pilot_aggregator.py",
    r"services\shadow_pilot_processor.py",
    r"services\shadow_pilot_reporter.py"
]

for f in files_to_delete:
    path = os.path.join(backend_dir, f)
    if os.path.exists(path):
        os.remove(path)
        print(f"Deleted {f}")

# 2. Update main.py to remove routers
main_py = os.path.join(backend_dir, "main.py")
with open(main_py, "r", encoding="utf-8") as f:
    main_content = f.read()

main_content = re.sub(r'from app\.routes import .*audit.*\n', '', main_content)
main_content = re.sub(r'from app\.routes import .*shadow_pilot_public.*\n', '', main_content)
main_content = re.sub(r'app\.include_router\(audit\.router,.*\n', '', main_content)
main_content = re.sub(r'app\.include_router\(shadow_pilot_public\.router,.*\n', '', main_content)

# Remove adr from SQL strings in main.py
main_content = re.sub(r'                adr\s+NUMERIC.*\n', '', main_content)
main_content = re.sub(r'                ota_commission_pct\s+NUMERIC.*\n', '', main_content)
main_content = re.sub(r'                hourly_rate\s+NUMERIC.*\n', '', main_content)

with open(main_py, "w", encoding="utf-8") as f:
    f.write(main_content)
print("Updated main.py")

# 3. Update routes/admin.py
admin_py = os.path.join(backend_dir, r"routes\admin.py")
with open(admin_py, "r", encoding="utf-8") as f:
    admin_content = f.read()

admin_content = re.sub(r'\s*adr=Decimal\(str\(body\.adr\)\),', '', admin_content)
admin_content = re.sub(r'\s*ota_commission_pct=Decimal\(str\(body\.ota_commission_pct\)\),', '', admin_content)
admin_content = re.sub(r'\s*hourly_rate=Decimal\(str\(body\.hourly_rate\)\),', '', admin_content)
admin_content = re.sub(r'\s*adr=float\(prop\.adr\),', '', admin_content)
admin_content = re.sub(r'\s*ota_commission_pct=float\(prop\.ota_commission_pct\),', '', admin_content)
admin_content = re.sub(r'\s*hourly_rate=float\(prop\.hourly_rate\),', '', admin_content)
admin_content = re.sub(r'\s*"adr":.*,', '', admin_content)
admin_content = re.sub(r'\s*if body\.adr is not None:\s*prop\.adr = Decimal\(str\(body\.adr\)\)', '', admin_content)
admin_content = re.sub(r'\s*if body\.hourly_rate is not None:\s*prop\.hourly_rate = Decimal\(str\(body\.hourly_rate\)\)', '', admin_content)

with open(admin_py, "w", encoding="utf-8") as f:
    f.write(admin_content)
print("Updated admin.py")

# 4. Update services/analytics.py
analytics_py = os.path.join(backend_dir, r"services\analytics.py")
with open(analytics_py, "r", encoding="utf-8") as f:
    analytics_content = f.read()

analytics_content = re.sub(r'select\(Business\.adr\)', 'select(Business.id)', analytics_content)
analytics_content = re.sub(r'prop_result\.scalar\(\) or Decimal\("230"\)', 'Decimal("0")', analytics_content)
analytics_content = re.sub(r'total_revenue \+= adr', 'pass', analytics_content)

with open(analytics_py, "w", encoding="utf-8") as f:
    f.write(analytics_content)
print("Updated analytics.py")

# 5. Update services/conversation.py
conv_py = os.path.join(backend_dir, r"services\conversation.py")
with open(conv_py, "r", encoding="utf-8") as f:
    conv_content = f.read()

conv_content = re.sub(r'prop\.adr', 'Decimal("0")', conv_content)

with open(conv_py, "w", encoding="utf-8") as f:
    f.write(conv_content)
print("Updated conversation.py")

# 6. Update routes/superadmin.py
superadmin_py = os.path.join(backend_dir, r"routes\superadmin.py")
with open(superadmin_py, "r", encoding="utf-8") as f:
    superadmin_content = f.read()

superadmin_content = re.sub(r'\s*adr_estimate=body\.adr_estimate,', '', superadmin_content)
superadmin_content = re.sub(r'\s*room_count=body\.room_count,', '', superadmin_content)
superadmin_content = re.sub(r'\s*if body\.get\("adr"\):\s*prop\.adr = body\["adr"\]', '', superadmin_content)

with open(superadmin_py, "w", encoding="utf-8") as f:
    f.write(superadmin_content)
print("Updated superadmin.py")

# 7. Update services/scheduler.py
scheduler_py = os.path.join(backend_dir, r"services\scheduler.py")
with open(scheduler_py, "r", encoding="utf-8") as f:
    sched_content = f.read()

# Delete shadow pilot logic
sched_content = re.sub(r'from app\.services\.shadow_pilot_processor import .*?\n', '', sched_content)
sched_content = re.sub(r'from app\.services\.shadow_pilot_aggregator import .*?\n', '', sched_content)
sched_content = re.sub(r'from app\.services\.shadow_pilot_reporter import .*?\n', '', sched_content)
sched_content = re.sub(r'async def _run_shadow_pilot_aggregation.*?async def _run_billing_checks', 'async def _run_billing_checks', sched_content, flags=re.DOTALL)
sched_content = re.sub(r'async def _run_shadow_pilot_daily_reports.*?async def _run_shadow_pilot_aggregation', 'async def _run_shadow_pilot_aggregation', sched_content, flags=re.DOTALL)
sched_content = re.sub(r'async def _run_audit_drip_campaign.*?async def _run_shadow_pilot_daily_reports', 'async def _run_shadow_pilot_daily_reports', sched_content, flags=re.DOTALL)
# It's safer to just comment out the references in start_scheduler
sched_content = re.sub(r'asyncio\.create_task\(_run_audit_drip_campaign', '# asyncio.create_task(_run_audit_drip_campaign', sched_content)
sched_content = re.sub(r'asyncio\.create_task\(_run_shadow_pilot_daily_reports', '# asyncio.create_task(_run_shadow_pilot_daily_reports', sched_content)
sched_content = re.sub(r'asyncio\.create_task\(_run_shadow_pilot_aggregation', '# asyncio.create_task(_run_shadow_pilot_aggregation', sched_content)

with open(scheduler_py, "w", encoding="utf-8") as f:
    f.write(sched_content)
print("Updated scheduler.py")

print("Hotel cleanup done.")
