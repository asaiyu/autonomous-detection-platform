from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_events_stub() -> dict[str, str]:
    return {"status": "stub", "message": "events endpoint placeholder"}
