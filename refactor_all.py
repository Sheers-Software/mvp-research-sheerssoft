import os
import glob
import re

backend_path = r"d:\repos\mvp-research-sheerssoft\backend\app\**\*.py"

for filepath in glob.glob(backend_path, recursive=True):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Standard replacements
    content = re.sub(r'\bProperty\b', 'Business', content)
    content = re.sub(r'\bproperty_id\b', 'business_id', content)
    content = re.sub(r'\bproperties\b', 'businesses', content)
    content = re.sub(r'\bproperty_name\b', 'business_name', content)
    content = re.sub(r'\bproperty_slug\b', 'business_slug', content)
    content = re.sub(r'\bproperty\b', 'business', content) # Lowercase property -> business
    content = re.sub(r'\bPropertyResponse\b', 'BusinessResponse', content)
    content = re.sub(r'\bPropertyCreateRequest\b', 'BusinessCreateRequest', content)
    content = re.sub(r'\bPropertySettingsUpdateRequest\b', 'BusinessSettingsUpdateRequest', content)
    
    # We must be careful not to rename things like `@property` decorator, but let's see.
    content = re.sub(r'@business\b', '@property', content) # Restore python decorators

    if original != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

print("Global refactor completed.")
