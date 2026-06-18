"""
Portal routes — Tenant self-service API.
Covers home dashboard, team management, channel status, and KB management.
"""

import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
import structlog
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.database import get_db
from app.auth import get_current_user
from app.models import (
    Tenant, Business, TenantMembership, OnboardingProgress,
    KBDocument, AnalyticsDaily, User,
)
from app.services import generate_embedding

logger = structlog.get_logger()
router = APIRouter()


# ─────────────────────────────────────────────────────────────
# Request/Response Schemas (portal-specific)
# ─────────────────────────────────────────────────────────────

class KBCreateRequest(BaseModel):
    doc_type: str
    title: str
    content: str


class KBUpdateRequest(BaseModel):
    title: str | None = None
    content: str | None = None


class KBWizardRoom(BaseModel):
    name: str
    description: str
    rate_myr: float | None = None


class KBWizardFaq(BaseModel):
    question: str
    answer: str


class KBWizardPolicies(BaseModel):
    checkin: str | None = None
    checkout: str | None = None
    cancellation: str | None = None


class KBWizardContact(BaseModel):
    phone: str | None = None
    email: str | None = None
    address: str | None = None


class KBIngestWizardRequest(BaseModel):
    business_name: str
    rooms: list[KBWizardRoom] = []
    facilities: list[str] = []
    faqs: list[KBWizardFaq] = []
    policies: KBWizardPolicies | None = None
    contact: KBWizardContact | None = None


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

async def _get_user_tenant_id(user: Any) -> uuid.UUID:
    """
    Return the primary tenant_id for the user.
    Raises 403 if the user has no TenantMembership (e.g. superadmin without tenant).
    """
    if isinstance(user, dict):
        raise HTTPException(status_code=403, detail="No tenant membership found for this user.")
    if not user.memberships:
        raise HTTPException(status_code=403, detail="No tenant membership found for this user.")
    sorted_memberships = sorted(user.memberships, key=lambda m: m.created_at)
    return sorted_memberships[0].tenant_id


async def _verify_property_access(
    db: AsyncSession,
    business_id: uuid.UUID,
    user: Any,
) -> Business:
    """
    Verify the business exists and belongs to the user's tenant.
    Returns the Business ORM object on success, raises 403/404 otherwise.
    """
    tenant_id = await _get_user_tenant_id(user)

    result = await db.execute(
        select(Business).where(
            Business.id == business_id,
            Business.tenant_id == tenant_id,
            Business.deleted_at.is_(None),
        )
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(
            status_code=404,
            detail="Business not found or you do not have access to it.",
        )
    return prop


def _compute_score(progress: OnboardingProgress) -> int:
    """Compute the gamified onboarding score (0-100)."""
    score = 10  # account_created always true
    channels_connected = all(
        s in ("active", "skipped")
        for s in [progress.whatsapp_status, progress.email_status, progress.website_status]
    )
    if channels_connected:
        score += 20
    if progress.kb_populated:
        score += 20
    if progress.first_inquiry_received:
        score += 15
    if progress.first_morning_report_sent:
        score += 15
    if progress.first_lead_captured:
        score += 10
    if progress.owner_first_login:
        score += 10
    return score


# ─────────────────────────────────────────────────────────────
# Portal Home
# ─────────────────────────────────────────────────────────────

@router.get("/portal/home")
async def portal_home(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Tenant portal home — summary card for all businesses with weekly metrics.
    """
    tenant_id = await _get_user_tenant_id(user)

    # Load tenant details
    tenant_result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = tenant_result.scalar_one_or_none()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found.")

    # Load all active businesses for this tenant
    props_result = await db.execute(
        select(Business).where(
            Business.tenant_id == tenant_id,
            Business.deleted_at.is_(None),
        ).order_by(Business.created_at)
    )
    businesses = props_result.scalars().all()

    # For each business compute 7-day analytics
    seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).date()

    property_summaries = []
    for prop in businesses:
        # Load last 7 days of AnalyticsDaily
        analytics_result = await db.execute(
            select(AnalyticsDaily).where(
                AnalyticsDaily.business_id == prop.id,
                AnalyticsDaily.report_date >= seven_days_ago,
            )
        )
        analytics_rows = analytics_result.scalars().all()

        weekly_inquiries = sum(r.total_inquiries for r in analytics_rows)
        weekly_leads = sum(r.leads_captured for r in analytics_rows)
        weekly_revenue_rm = float(sum(
            r.estimated_revenue_recovered for r in analytics_rows
        ))

        # Load OnboardingProgress
        progress_result = await db.execute(
            select(OnboardingProgress).where(
                OnboardingProgress.business_id == prop.id
            )
        )
        progress = progress_result.scalar_one_or_none()

        onboarding_score = _compute_score(progress) if progress else 0
        channel_statuses = {
            "whatsapp": progress.whatsapp_status if progress else "pending",
            "email": progress.email_status if progress else "pending",
            "website": progress.website_status if progress else "pending",
        }

        property_summaries.append({
            "id": str(prop.id),
            "name": prop.name,
            "slug": prop.slug,
            "is_active": prop.is_active,
            "weekly_inquiries": weekly_inquiries,
            "weekly_leads": weekly_leads,
            "weekly_revenue_rm": weekly_revenue_rm,
            "onboarding_score": onboarding_score,
            "channel_statuses": channel_statuses,
        })

    return {
        "tenant": {
            "id": str(tenant.id),
            "name": tenant.name,
            "subscription_tier": tenant.subscription_tier,
            "subscription_status": tenant.subscription_status,
            "pilot_end_date": tenant.pilot_end_date.isoformat() if tenant.pilot_end_date else None,
        },
        "businesses": property_summaries,
    }


# ─────────────────────────────────────────────────────────────
# Team Management
# ─────────────────────────────────────────────────────────────

@router.get("/portal/team")
async def portal_team(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    List all team members for the user's tenant.
    """
    tenant_id = await _get_user_tenant_id(user)

    result = await db.execute(
        select(TenantMembership)
        .options(selectinload(TenantMembership.user))
        .where(TenantMembership.tenant_id == tenant_id)
        .order_by(TenantMembership.created_at)
    )
    memberships = result.scalars().all()

    return [
        {
            "membership_id": str(m.id),
            "user_id": str(m.user_id),
            "email": m.user.email if m.user else None,
            "full_name": m.user.full_name if m.user else None,
            "role": m.role,
            "accessible_property_ids": m.accessible_property_ids,
            "last_login_at": m.user.last_login_at.isoformat() if m.user and m.user.last_login_at else None,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in memberships
    ]


@router.delete("/portal/team/{membership_id}")
async def remove_team_member(
    membership_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Remove a team member from the tenant.
    Only owners and admins may remove members.
    Cannot remove the last owner or your own membership.
    """
    tenant_id = await _get_user_tenant_id(user)

    # Determine the calling user's role
    if isinstance(user, dict):
        raise HTTPException(status_code=403, detail="Insufficient permissions.")
    sorted_memberships = sorted(user.memberships, key=lambda m: m.created_at)
    caller_membership = next(
        (m for m in sorted_memberships if m.tenant_id == tenant_id), None
    )
    if not caller_membership or caller_membership.role not in ("owner", "admin"):
        raise HTTPException(
            status_code=403,
            detail="Only owners and admins can remove team members.",
        )

    # Load the target membership
    result = await db.execute(
        select(TenantMembership).where(
            TenantMembership.id == membership_id,
            TenantMembership.tenant_id == tenant_id,
        )
    )
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Membership not found.")

    # Cannot remove your own membership
    if target.user_id == user.id:
        raise HTTPException(status_code=400, detail="You cannot remove your own membership.")

    # Cannot remove the last owner
    if target.role == "owner":
        owner_count_result = await db.execute(
            select(func.count(TenantMembership.id)).where(
                TenantMembership.tenant_id == tenant_id,
                TenantMembership.role == "owner",
            )
        )
        owner_count = owner_count_result.scalar() or 0
        if owner_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot remove the last owner of a tenant.",
            )

    await db.delete(target)
    await db.commit()

    logger.info("Team member removed", membership_id=str(membership_id), tenant_id=str(tenant_id))
    return {"message": "Member removed"}


# ─────────────────────────────────────────────────────────────
# Channel Status
# ─────────────────────────────────────────────────────────────

@router.get("/portal/channels")
async def portal_channels(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Channel setup status for all businesses in the user's tenant.
    Includes the embeddable widget code for each business.
    """
    tenant_id = await _get_user_tenant_id(user)

    props_result = await db.execute(
        select(Business).where(
            Business.tenant_id == tenant_id,
            Business.deleted_at.is_(None),
        ).order_by(Business.created_at)
    )
    businesses = props_result.scalars().all()

    summaries = []
    for prop in businesses:
        progress_result = await db.execute(
            select(OnboardingProgress).where(
                OnboardingProgress.business_id == prop.id
            )
        )
        progress = progress_result.scalar_one_or_none()

        widget_embed_code = (
            f'<script src="https://ai.sheerssoft.com/widget.js" '
            f'data-business="{prop.slug}"></script>'
        )

        summaries.append({
            "business_id": str(prop.id),
            "business_name": prop.name,
            "whatsapp_status": progress.whatsapp_status if progress else "pending",
            "email_status": progress.email_status if progress else "pending",
            "website_status": progress.website_status if progress else "pending",
            "channel_errors": progress.channel_errors if progress else None,
            "widget_embed_code": widget_embed_code,
        })

    return summaries


# ─────────────────────────────────────────────────────────────
# Knowledge Base
# ─────────────────────────────────────────────────────────────

@router.get("/businesses/{business_id}/kb")
async def list_kb_documents(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    List all KB documents for a business, ordered by doc_type then title.
    """
    await _verify_property_access(db, business_id, user)

    result = await db.execute(
        select(KBDocument)
        .where(KBDocument.business_id == business_id)
        .order_by(KBDocument.doc_type, KBDocument.title)
    )
    docs = result.scalars().all()

    return [
        {
            "id": str(d.id),
            "doc_type": d.doc_type,
            "title": d.title,
            "content_preview": d.content[:200] if d.content else "",
            "char_count": len(d.content) if d.content else 0,
            "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        }
        for d in docs
    ]


@router.post("/businesses/{business_id}/kb", status_code=201)
async def create_kb_document(
    business_id: uuid.UUID,
    body: KBCreateRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Create a new KB document for a business and generate its embedding.
    Sets OnboardingProgress.kb_populated = True on first document.
    """
    await _verify_property_access(db, business_id, user)

    # Generate embedding
    embedding = await generate_embedding(body.content)

    doc = KBDocument(
        business_id=business_id,
        doc_type=body.doc_type,
        title=body.title,
        content=body.content,
        embedding=embedding,
    )
    db.add(doc)
    await db.flush()

    # Set kb_populated flag on first document
    progress_result = await db.execute(
        select(OnboardingProgress).where(
            OnboardingProgress.business_id == business_id
        )
    )
    progress = progress_result.scalar_one_or_none()
    if progress and not progress.kb_populated:
        progress.kb_populated = True
        logger.info("KB populated milestone set", business_id=str(business_id))

    await db.commit()
    await db.refresh(doc)

    logger.info("KB document created", doc_id=str(doc.id), business_id=str(business_id))

    return {
        "id": str(doc.id),
        "doc_type": doc.doc_type,
        "title": doc.title,
        "char_count": len(doc.content) if doc.content else 0,
        "message": "Document created successfully.",
    }


@router.put("/businesses/{business_id}/kb/{doc_id}")
async def update_kb_document(
    business_id: uuid.UUID,
    doc_id: uuid.UUID,
    body: KBUpdateRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Update a KB document. Regenerates the embedding if content changed.
    """
    await _verify_property_access(db, business_id, user)

    result = await db.execute(
        select(KBDocument).where(
            KBDocument.id == doc_id,
            KBDocument.business_id == business_id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    if body.title is not None:
        doc.title = body.title

    if body.content is not None and body.content != doc.content:
        doc.content = body.content
        doc.embedding = await generate_embedding(body.content)

    doc.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(doc)

    return {
        "id": str(doc.id),
        "doc_type": doc.doc_type,
        "title": doc.title,
        "char_count": len(doc.content) if doc.content else 0,
        "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
    }


@router.delete("/businesses/{business_id}/kb/{doc_id}")
async def delete_kb_document(
    business_id: uuid.UUID,
    doc_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Hard-delete a KB document.
    """
    await _verify_property_access(db, business_id, user)

    result = await db.execute(
        select(KBDocument).where(
            KBDocument.id == doc_id,
            KBDocument.business_id == business_id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    await db.delete(doc)
    await db.commit()

    logger.info("KB document deleted", doc_id=str(doc_id), business_id=str(business_id))
    return {"message": "Document deleted"}


@router.post("/businesses/{business_id}/kb/ingest-wizard", status_code=201)
async def ingest_kb_wizard(
    business_id: uuid.UUID,
    body: KBIngestWizardRequest,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Bulk-ingest structured business info as KB documents.
    Creates separate documents for rooms, facilities, FAQs, policies, and contact.
    Embeddings are generated in parallel (batched to max 10 at a time).
    Sets OnboardingProgress.kb_populated = True.
    """
    await _verify_property_access(db, business_id, user)

    # Build (doc_type, title, content) tuples from wizard data
    docs_to_create: list[tuple[str, str, str]] = []

    # Rooms
    if body.rooms:
        for room in body.rooms:
            rate_str = f" — Rate: RM {room.rate_myr:.2f}/night" if room.rate_myr else ""
            content = f"{room.name}{rate_str}\n{room.description}"
            docs_to_create.append(("rooms", room.name, content))

    # Facilities
    if body.facilities:
        content = "\n".join(f"- {f}" for f in body.facilities)
        docs_to_create.append(("facilities", f"{body.business_name} Facilities", content))

    # FAQs
    for faq in body.faqs:
        content = f"Q: {faq.question}\nA: {faq.answer}"
        docs_to_create.append(("faqs", faq.question, content))

    # Policies
    if body.policies:
        policy_lines = []
        if body.policies.checkin:
            policy_lines.append(f"Check-in: {body.policies.checkin}")
        if body.policies.checkout:
            policy_lines.append(f"Check-out: {body.policies.checkout}")
        if body.policies.cancellation:
            policy_lines.append(f"Cancellation: {body.policies.cancellation}")
        if policy_lines:
            docs_to_create.append(("policies", "Hotel Policies", "\n".join(policy_lines)))

    # Contact
    if body.contact:
        contact_lines = []
        if body.contact.phone:
            contact_lines.append(f"Phone: {body.contact.phone}")
        if body.contact.email:
            contact_lines.append(f"Email: {body.contact.email}")
        if body.contact.address:
            contact_lines.append(f"Address: {body.contact.address}")
        if contact_lines:
            docs_to_create.append(("directions", "Contact & Location", "\n".join(contact_lines)))

    if not docs_to_create:
        return {"docs_created": 0, "message": "No content provided to ingest."}

    # Generate embeddings in parallel, batched to max 10 at a time
    BATCH_SIZE = 10
    embeddings: list[list[float]] = []
    for i in range(0, len(docs_to_create), BATCH_SIZE):
        batch = docs_to_create[i : i + BATCH_SIZE]
        batch_embeddings = await asyncio.gather(
            *[generate_embedding(content) for _, _, content in batch]
        )
        embeddings.extend(batch_embeddings)

    # Persist all documents
    for (doc_type, title, content), embedding in zip(docs_to_create, embeddings):
        doc = KBDocument(
            business_id=business_id,
            doc_type=doc_type,
            title=title,
            content=content,
            embedding=embedding,
        )
        db.add(doc)

    # Set kb_populated flag
    progress_result = await db.execute(
        select(OnboardingProgress).where(
            OnboardingProgress.business_id == business_id
        )
    )
    progress = progress_result.scalar_one_or_none()
    if progress and not progress.kb_populated:
        progress.kb_populated = True

    await db.commit()

    logger.info(
        "KB wizard ingest complete",
        business_id=str(business_id),
        docs_created=len(docs_to_create),
    )
    return {
        "docs_created": len(docs_to_create),
        "message": f"Successfully ingested {len(docs_to_create)} knowledge base documents.",
    }


# ─────────────────────────────────────────────────────────────
# Onboarding Completion
# ─────────────────────────────────────────────────────────────

@router.post("/onboarding/complete/{business_id}")
async def complete_onboarding(
    business_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Mark a business as active (onboarding complete).
    Verifies tenant ownership before activating.
    """
    prop = await _verify_property_access(db, business_id, user)

    prop.is_active = True
    await db.commit()

    logger.info("Business activated via onboarding complete", business_id=str(business_id))
    return {
        "business_id": str(business_id),
        "activated": True,
        "message": "Business is now live!",
    }
