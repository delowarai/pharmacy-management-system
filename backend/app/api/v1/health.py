from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
def health_check():
    return {"status": "ok", "time": datetime.now(timezone.utc)}

