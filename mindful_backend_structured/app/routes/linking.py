from fastapi import APIRouter, Depends, HTTPException
from app.deps.auth import supabase_user, user_id_from
from app.models.dto import LinkCodeCreateOut, LinkCodeConsumeIn
from app.services.identity import (
    ensure_parent,
    ensure_child,
    create_link_code,
    consume_link_code,
)

router = APIRouter(tags=["linking"])


@router.post("/api/parent/link-code/create", response_model=LinkCodeCreateOut)
async def link_code_create(user=Depends(supabase_user)):
    parent_id = await ensure_parent(user_id_from(user))

    # generate new code, store in LinkCodes
    out = await create_link_code(parent_id, ttl_minutes=1440)

    return out


@router.post("/api/child/link-code/consume")
async def link_code_consume(payload: LinkCodeConsumeIn, user=Depends(supabase_user)):
    uid = user_id_from(user)
    child_id = await ensure_child(uid, payload.display_name)

    try:
        # consume code (validate expiry + consumed flag)
        info = await consume_link_code(payload.code, child_id)

        # `consume_link_code` should:
        # 1. Mark code as consumed in LinkCodes
        # 2. Insert permanent relation into FamilyLinks
        # Example FamilyLinks row:
        # {id, parent_id, child_id, created_at, code, expired_at}

    except ValueError as e:
        raise HTTPException(400, str(e))

    return {
        "child_id": child_id,
        "parent_id": info["parent_id"],
        "linked_at": info["created_at"],
        "expires_at": info["expires_at"],
    }
