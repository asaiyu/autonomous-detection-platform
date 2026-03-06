from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_rules_stub() -> dict[str, str]:
    return {"status": "stub", "message": "rules endpoint placeholder"}
