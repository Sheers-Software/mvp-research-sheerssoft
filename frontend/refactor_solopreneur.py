import os
import glob

frontend_src = r"d:\repos\mvp-research-sheerssoft\frontend\src"
files = glob.glob(os.path.join(frontend_src, "**", "*.tsx"), recursive=True) + \
        glob.glob(os.path.join(frontend_src, "**", "*.ts"), recursive=True)

replacements = {
    "Hotel Concierge Intelligence": "AI Concierge for Solopreneurs",
    "hotel clients": "solopreneur clients",
    "Hotel / Group Name": "Business Name",
    "hotel_name": "business_name",
    "Hotel Owner": "Solopreneur",
    "gm@hotel.com": "owner@business.com",
    "reservations@hotel.com": "hello@business.com",
    "staff@yourhotel.com": "staff@business.com",
    "https://www.hotel.com": "https://www.yourbusiness.com",
    "Hotel Dashboard": "Business Dashboard",
    "hotel businesses": "businesses",
    "Grand Palace Hotel KL": "Sarah Photography Studios",
    "Lumière Hospitality Group": "Sarah's Creative Services",
    "Lumière Suites Kuala Lumpur": "Sarah Photography",
    "Lumière Boutique Penang": "Sarah Videography",
    "Lumière Suites": "Sarah Photography",
    "lumierehotels.com": "sarahphotography.com",
    "aisha.rahman@": "sarah@",
    "Aisha Rahman": "Sarah Jane",
    "Lumière Ballroom": "Photo Studio",
    "room booking": "service booking",
    "room_booking": "service_booking",
    "Deluxe King": "Portrait Session",
    "Superior Queen": "Mini Session",
    "Sunset Bay Hotel": "Tech Fixes LLC",
    "Sunset Bay Resort": "Tech Fixes LLC",
    "KL Capsule Pods": "Marketing Pro",
    "Cameron Highlands Inn": "FitLife Coaching",
    "Tropika Resorts": "Nail Art Studio",
    "Heritage Stays Melaka": "Boutique Bakery",
    "Borneo Eco Lodges": "Freelance Designer",
    "City Inn Express": "Local Plumber",
    "room_count": "monthly_inquiries",
    "hotel group": "business portfolio",
    "hotel staff": "business staff",
    "PROPERTY_ID": "BUSINESS_ID",
    "PROPERTY_NAME": "BUSINESS_NAME",
    "property_id": "business_id",
    "property_name": "business_name",
    "properties": "businesses",
    "Properties": "Businesses",
    "Property": "Business",
    "hotel": "business",
    "Hotel": "Business",
    "property": "business",
}

for file_path in files:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    for old, new in replacements.items():
        content = content.replace(old, new)

    if content != original:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {file_path}")

print("Done.")
