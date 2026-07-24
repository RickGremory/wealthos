"""HTTP routes for the planning module (budgets + cash plans)."""

from fastapi import APIRouter

from wealthos.modules.planning.api.budget_router import router as budget_router
from wealthos.modules.planning.api.cash_plan_router import router as cash_plan_router

router = APIRouter()
router.include_router(budget_router)
router.include_router(cash_plan_router)
