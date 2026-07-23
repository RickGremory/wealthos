"""HTTP routes for the identity module (health probe only)."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", include_in_schema=False)
async def identity_module_health() -> dict[str, str]:
    return {"module": "identity", "status": "ready"}
