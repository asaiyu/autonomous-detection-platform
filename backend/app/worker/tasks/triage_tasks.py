from app.worker.celery_app import celery_app


@celery_app.task(name="tasks.triage.alert")
def triage_alert(alert_id: str) -> dict[str, str]:
    _ = alert_id
    return {"status": "stub", "task": "triage"}
