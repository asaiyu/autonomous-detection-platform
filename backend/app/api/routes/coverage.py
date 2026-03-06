from fastapi import APIRouter

router = APIRouter()


@router.get("")
def coverage_stub() -> dict[str, str]:
    return {"status": "stub", "message": "coverage endpoint placeholder"}
