from fastapi import APIRouter

router = APIRouter()


@router.post("")
def ingest_stub() -> dict[str, str]:
    return {"status": "stub", "message": "ingest endpoint placeholder"}
