"""Celery worker setup for async JSON processing tasks."""

import os

from celery import Celery

broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "json_url_utility",
    broker=broker_url,
    backend=broker_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    broker_connection_retry_on_startup=True,
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_json_url(self, url: str) -> dict:
    """Fetch a URL, parse its response as JSON, and return the result.

    Intended for offloading heavy or slow HTTP fetches out of the request
    thread so the API stays responsive.

    Args:
        url: The URL to fetch JSON from.

    Returns:
        dict with 'url', 'status', 'data' (parsed JSON) or 'error'.
    """
    import urllib.request
    import json

    try:
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
            return {"url": url, "status": resp.status, "data": data}
    except Exception as exc:
        try:
            self.retry(exc=exc)
        except self.max_retries_exceeded:
            return {"url": url, "error": str(exc)}
