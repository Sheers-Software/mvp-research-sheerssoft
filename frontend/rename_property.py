import os
import glob

frontend_src = r"d:\repos\mvp-research-sheerssoft\frontend\src"
files = glob.glob(os.path.join(frontend_src, "**", "*.tsx"), recursive=True) + \
        glob.glob(os.path.join(frontend_src, "**", "*.ts"), recursive=True)

for file_path in files:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    # Order matters to prevent double replacement
    content = content.replace("property_id", "business_id")
    content = content.replace("property_name", "business_name")
    content = content.replace("properties", "businesses")
    content = content.replace("Properties", "Businesses")
    content = content.replace("Property", "Business")
    content = content.replace("property", "business")

    # Revert CSS properties (if any got hit by lower case property)
    # usually CSS uses 'properties', but in JS it's rarely just 'property' except for the entity here.
    if content != original:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {file_path}")

print("Done.")
