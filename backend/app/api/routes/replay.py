from fastapi import APIRouter

router = APIRouter()


@router.post("")
def replay_stub() -> dict[str, str]:
    return {"status": "stub", "message": "replay endpoint placeholder"}
