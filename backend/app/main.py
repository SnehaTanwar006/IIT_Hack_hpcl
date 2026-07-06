"""FastAPI entrypoint for the HPCL lead intelligence prototype."""

from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.app.core.pipeline import build_demo_repository, preview_notification


app = FastAPI(
    title="HPCL B2B Lead Intelligence API",
    version="0.2.0",
    description="Recruiter-ready demo API for source ingestion, lead dossiers, scoring, routing, feedback, and alerts.",
)

repository = build_demo_repository(limit=25)


class StatusUpdate(BaseModel):
    status: Literal["NEW", "ACCEPTED", "REJECTED", "CONVERTED"]
    note: str = ""


class NotificationRequest(BaseModel):
    channel: Literal["whatsapp", "email", "teams", "sms"] = "whatsapp"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/pipeline/run-demo")
def run_demo(limit: int = 25) -> dict[str, object]:
    global repository
    repository = build_demo_repository(limit=limit)
    return {"message": "demo pipeline completed", "lead_count": len(repository.list())}


@app.get("/leads")
def list_leads(status: str | None = None, priority: str | None = None) -> list[dict]:
    return repository.list(status=status, priority=priority)


@app.get("/leads/{lead_id}")
def get_lead(lead_id: str) -> dict:
    lead = repository.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@app.patch("/leads/{lead_id}/status")
def update_status(lead_id: str, update: StatusUpdate) -> dict:
    if not repository.get(lead_id):
        raise HTTPException(status_code=404, detail="Lead not found")
    return repository.update_status(lead_id, update.status, update.note)


@app.get("/analytics/summary")
def analytics_summary() -> dict:
    return repository.analytics()


@app.post("/leads/{lead_id}/notifications/preview")
def notification_preview(lead_id: str, request: NotificationRequest) -> dict:
    lead = repository.get(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return preview_notification(lead, channel=request.channel)
