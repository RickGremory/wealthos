"""HTTP routes for the organizations module."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", include_in_schema=False)
async def organizations_module_health() -> dict[str, str]:
    """Scaffold probe — business endpoints land in the next sprint."""
    return {"module": "organizations", "status": "ready"}
