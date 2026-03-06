from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_runs_stub() -> dict[str, str]:
    return {"status": "stub", "message": "runs endpoint placeholder"}
