from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "wealthos-api",
        "version": "0.1.0",
    }
