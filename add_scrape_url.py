import os

schemas_py = r"d:\repos\mvp-research-sheerssoft\backend\app\schemas.py"
with open(schemas_py, "a", encoding="utf-8") as f:
    f.write("\n\nclass ScrapeUrlRequest(BaseModel):\n")
    f.write("    url: str = Field(..., min_length=5, max_length=500)\n\n")
    f.write("class ScrapeUrlResponse(BaseModel):\n")
    f.write("    tenant_id: uuid.UUID\n")
    f.write("    business_id: uuid.UUID\n")
    f.write("    business_name: str\n")
    f.write("    message: str\n")

print("Added schemas.")

onboarding_py = r"d:\repos\mvp-research-sheerssoft\backend\app\routes\onboarding.py"
with open(onboarding_py, "r", encoding="utf-8") as f:
    content = f.read()

# Add new imports
new_imports = """
from pydantic import BaseModel
import httpx
from bs4 import BeautifulSoup
from app.schemas import ScrapeUrlRequest, ScrapeUrlResponse
"""

content = content.replace("import httpx", new_imports)

new_route = """

# ─────────────────────────────────────────────────────────────
# Solopreneur "Paste URL" Flow
# ─────────────────────────────────────────────────────────────

@router.post("/onboarding/scrape-url", response_model=ScrapeUrlResponse)
async def scrape_url_flow(
    body: ScrapeUrlRequest,
    db: AsyncSession = Depends(get_db),
):
    \"\"\"
    Frictionless onboarding. Takes a URL, scrapes it using Jina Reader, 
    and instantly provisions a trial Business and KB document.
    \"\"\"
    url = body.url
    if not url.startswith("http"):
        url = "https://" + url

    # 1. Scrape using Jina Reader (free public API for clean markdown)
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(f"https://r.jina.ai/{url}")
            if resp.status_code >= 400:
                raise HTTPException(status_code=400, detail="Failed to scrape URL.")
            markdown_content = resp.text
    except Exception as e:
        logger.error("Scraping failed", error=str(e))
        raise HTTPException(status_code=400, detail="Failed to read website content.")

    # 2. Extract Business Name from title or URL
    # We could use an LLM here, but for MVP we parse the URL or first Header
    business_name = "My Business"
    first_line = markdown_content.split("\\n")[0] if markdown_content else ""
    if first_line.startswith("#"):
        business_name = first_line.replace("#", "").strip()
    else:
        # Fallback to domain name
        domain = url.split("//")[-1].split("/")[0]
        business_name = domain.replace("www.", "").split(".")[0].title()

    if len(business_name) < 2:
        business_name = "My Business"

    # 3. Create Tenant
    tenant_slug = _slugify(business_name)
    slug_check = await db.execute(select(Tenant).where(Tenant.slug == tenant_slug))
    if slug_check.scalar_one_or_none():
        tenant_slug = f"{tenant_slug}-{uuid.uuid4().hex[:6]}"

    tenant = Tenant(
        name=business_name,
        slug=tenant_slug,
        subscription_tier="trial",
        subscription_status="trialing",
    )
    db.add(tenant)
    await db.flush()

    # 4. Create Business
    business_slug = _slugify(business_name)
    prop_slug_check = await db.execute(select(Business).where(Business.slug == business_slug))
    if prop_slug_check.scalar_one_or_none():
        business_slug = f"{business_slug}-{uuid.uuid4().hex[:6]}"

    prop = Business(
        tenant_id=tenant.id,
        name=business_name,
        slug=business_slug,
        timezone="Asia/Kuala_Lumpur",
        plan_tier="trial",
        website_url=url,
    )
    db.add(prop)
    await db.flush()

    # 5. Save Knowledge Base Document
    doc = KBDocument(
        business_id=prop.id,
        doc_type="faqs",
        title="Website Content",
        content=markdown_content[:30000], # Cap size
    )
    db.add(doc)
    await db.commit()

    logger.info("URL Scraped and Business Provisioned", url=url, business_id=str(prop.id))

    return ScrapeUrlResponse(
        tenant_id=tenant.id,
        business_id=prop.id,
        business_name=business_name,
        message="Website ingested successfully. AI is ready to test."
    )

"""

content += new_route

with open(onboarding_py, "w", encoding="utf-8") as f:
    f.write(content)

print("Added onboarding route.")
