from app.worker.celery_app import celery_app


@celery_app.task(name="tasks.ingest.process")
def process_ingest(payload: dict | None = None) -> dict[str, str]:
    _ = payload
    return {"status": "stub", "task": "ingest"}
