from app.worker.celery_app import celery_app


@celery_app.task(name="tasks.replay.validate")
def validate_replay(run_id: str) -> dict[str, str]:
    _ = run_id
    return {"status": "stub", "task": "replay"}
