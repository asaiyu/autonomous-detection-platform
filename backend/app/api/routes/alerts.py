from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_alerts_stub() -> dict[str, str]:
    return {"status": "stub", "message": "alerts endpoint placeholder"}
