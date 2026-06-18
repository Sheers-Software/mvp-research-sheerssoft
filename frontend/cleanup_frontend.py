import os
import shutil
import re

frontend_dir = r"d:\repos\mvp-research-sheerssoft\frontend\src"

# 1. Delete hotel-specific directories
dirs_to_delete = [
    r"app\apply",
    r"app\audit",
    r"app\shadow",
    r"app\admin\shadow-pilots",
    r"app\admin\tools\revenue-audit"
]

for d in dirs_to_delete:
    path = os.path.join(frontend_dir, d)
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"Deleted {d}")

# 2. String replacements in portal and dashboard
def replace_in_file(rel_path, replacements):
    path = os.path.join(frontend_dir, rel_path)
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {rel_path}")

replace_in_file(r"app\dashboard\page.tsx", [
    ("property_id", "business_id"),
    ("property_name", "business_name"),
    ("properties", "businesses"),
    ("Property", "Business"),
    ("property", "business"),
    ("guest", "customer"),
    ("Revenue estimated as: leads captured × property ADR × 20% conversion rate.", 
     "Revenue estimated as: leads captured × average order value × 20% conversion rate.")
])

replace_in_file(r"app\portal\page.tsx", [
    ("property_id", "business_id"),
    ("property_name", "business_name"),
    ("properties", "businesses"),
    ("Property", "Business"),
    ("property", "business"),
    ("guest", "customer"),
])

replace_in_file(r"lib\tenant-context.tsx", [
    ("property_id", "business_id"),
    ("property_name", "business_name"),
    ("properties", "businesses"),
    ("Property", "Business"),
    ("property", "business"),
    ("setProperties", "setBusinesses"),
])

print("Frontend cleanup done.")
