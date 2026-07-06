"""Demo pipeline and in-memory repository for recruiter-friendly demos."""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dateutil import parser


REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from entity_resolution.company_profile import CompanyProfileBuilder
from lead_scoring.lead_scorer import LeadScorer
from lead_scoring.territory_router import TerritoryRouter
from product_inference.inference_engine import ProductInferenceEngine


@dataclass
class DemoSignal:
    """Normalized public signal used as demo pipeline input."""

    signal_id: str
    source_type: str
    source_name: str
    source_url: str
    title: str
    text: str
    company_name: str
    location: str
    industry: str
    published_at: datetime
    expected_products: list[str] = field(default_factory=list)
    expected_priority: str = "MEDIUM"

    @property
    def full_text(self) -> str:
        return f"{self.title}. {self.text}"


class LeadIntelligencePipeline:
    """Runs the existing intelligence modules and builds lead dossiers."""

    def __init__(self) -> None:
        self.product_engine = ProductInferenceEngine()
        self.lead_scorer = LeadScorer()
        self.territory_router = TerritoryRouter()
        self.profile_builder = CompanyProfileBuilder()
        generated_dir = REPO_ROOT / "data" / "generated"
        generated_dir.mkdir(parents=True, exist_ok=True)
        self.profile_builder.matcher.companies_file = generated_dir / "companies_runtime.json"

    def process_signal(self, signal: DemoSignal, index: int) -> dict[str, Any]:
        products = self.product_engine.infer_products(signal.full_text, top_k=3)
        score = self.lead_scorer.score_lead(
            text=signal.full_text,
            signal_date=signal.published_at,
            company_name=signal.company_name,
            location=signal.location,
            signal_type="tender" if signal.source_type == "tender" else None,
        )
        profile = self.profile_builder.build_profile(
            company_name=signal.company_name,
            industry=signal.industry,
            location=signal.location,
        )
        routing = self.territory_router.route_lead(
            location=signal.location,
            industry=signal.industry,
            nearest_depot=score.breakdown["proximity"]["nearest_depot"],
        )

        product_dicts = [product.to_dict() for product in products]
        top_product = product_dicts[0]["product_name"] if product_dicts else "Needs review"

        return {
            "lead_id": f"LEAD-DEMO-{index:04d}",
            "status": "NEW",
            "priority": score.priority,
            "company": profile,
            "signal": {
                "signal_id": signal.signal_id,
                "title": signal.title,
                "summary": signal.text,
                "source_type": signal.source_type,
                "source_name": signal.source_name,
                "source_url": signal.source_url,
                "published_at": signal.published_at.isoformat(),
            },
            "provenance": {
                "source_url": signal.source_url,
                "source_name": signal.source_name,
                "extracted_at": _utc_timestamp(),
                "trust_score": self._trust_score(signal.source_type),
                "legal_basis": "publicly_available_demo_data",
                "policy_note": "Demo seed data. Production ingestion must honor robots.txt, ToS, and rate limits.",
            },
            "products": product_dicts,
            "score": score.to_dict(),
            "routing": routing,
            "next_best_action": self._next_best_action(score.priority, top_product, signal.source_type),
            "feedback": {
                "status": "NEW",
                "notes": [],
                "updated_at": None,
            },
            "labels": {
                "expected_products": signal.expected_products,
                "expected_priority": signal.expected_priority,
            },
            "created_at": _utc_timestamp(),
        }

    def run_demo(self, signals: list[DemoSignal], limit: int | None = None) -> list[dict[str, Any]]:
        selected = signals[:limit] if limit else signals
        return [self.process_signal(signal, index + 1) for index, signal in enumerate(selected)]

    @staticmethod
    def _trust_score(source_type: str) -> float:
        return {
            "tender": 0.98,
            "news": 0.88,
            "company_page": 0.92,
            "directory": 0.72,
        }.get(source_type, 0.70)

    @staticmethod
    def _next_best_action(priority: str, product_name: str, source_type: str) -> str:
        if priority == "CRITICAL" or source_type == "tender":
            return f"Call procurement contact and share {product_name} quotation pack within 24 hours."
        if priority == "HIGH":
            return f"Assign sales officer to validate {product_name} demand this week."
        return "Monitor signal, verify facility details, and add notes after first outreach."


class LeadRepository:
    """Simple in-memory store for local demos and tests."""

    def __init__(self, leads: list[dict[str, Any]] | None = None) -> None:
        self._leads: dict[str, dict[str, Any]] = {}
        if leads:
            self.replace(leads)

    def replace(self, leads: list[dict[str, Any]]) -> None:
        self._leads = {lead["lead_id"]: lead for lead in leads}

    def list(self, status: str | None = None, priority: str | None = None) -> list[dict[str, Any]]:
        leads = list(self._leads.values())
        if status:
            leads = [lead for lead in leads if lead["status"] == status]
        if priority:
            leads = [lead for lead in leads if lead["priority"] == priority]
        return leads

    def get(self, lead_id: str) -> dict[str, Any] | None:
        return self._leads.get(lead_id)

    def update_status(self, lead_id: str, status: str, note: str = "") -> dict[str, Any]:
        lead = self._leads[lead_id]
        lead["status"] = status
        lead["feedback"]["status"] = status
        lead["feedback"]["updated_at"] = _utc_timestamp()
        if note:
            lead["feedback"]["notes"].append(
                {"note": note, "created_at": _utc_timestamp()}
            )
        return lead

    def analytics(self) -> dict[str, Any]:
        leads = self.list()
        by_priority = _count_by(leads, lambda lead: lead["priority"])
        by_status = _count_by(leads, lambda lead: lead["status"])
        by_region = _count_by(leads, lambda lead: lead["routing"]["region"])
        by_product = _count_by(
            leads,
            lambda lead: lead["products"][0]["product_code"] if lead["products"] else "REVIEW",
        )
        by_source = _count_by(leads, lambda lead: lead["signal"]["source_type"])
        return {
            "total_leads": len(leads),
            "by_priority": by_priority,
            "by_status": by_status,
            "by_region": by_region,
            "by_product": by_product,
            "by_source": by_source,
            "conversion_funnel": {
                "new": by_status.get("NEW", 0),
                "accepted": by_status.get("ACCEPTED", 0),
                "converted": by_status.get("CONVERTED", 0),
                "rejected": by_status.get("REJECTED", 0),
            },
        }


def load_demo_signals(path: Path | None = None) -> list[DemoSignal]:
    """Load deterministic demo signals from CSV."""

    seed_path = path or REPO_ROOT / "data" / "seed" / "demo_signals_250.csv"
    signals: list[DemoSignal] = []
    with seed_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            signals.append(
                DemoSignal(
                    signal_id=row["signal_id"],
                    source_type=row["source_type"],
                    source_name=row["source_name"],
                    source_url=row["source_url"],
                    title=row["title"],
                    text=row["text"],
                    company_name=row["company_name"],
                    location=row["location"],
                    industry=row["industry"],
                    published_at=parser.parse(row["published_at"]),
                    expected_products=[
                        product.strip()
                        for product in row.get("expected_products", "").split("|")
                        if product.strip()
                    ],
                    expected_priority=row.get("expected_priority", "MEDIUM"),
                )
            )
    return signals


def build_demo_repository(limit: int = 25) -> LeadRepository:
    pipeline = LeadIntelligencePipeline()
    leads = pipeline.run_demo(load_demo_signals(), limit=limit)
    return LeadRepository(leads)


def preview_notification(lead: dict[str, Any], channel: str = "whatsapp") -> dict[str, Any]:
    """Build a sandbox notification payload without contacting external services."""

    top_product = lead["products"][0] if lead["products"] else {"product_name": "Needs review"}
    officer = lead["routing"]
    message = (
        f"HPCL Lead Alert: {lead['company']['canonical_name']} | "
        f"{lead['priority']} priority | Product fit: {top_product['product_name']} | "
        f"Action: {lead['next_best_action']}"
    )
    return {
        "mode": "sandbox",
        "channel": channel,
        "recipient": {
            "name": officer["assigned_officer"],
            "email": officer["email"],
            "phone": officer["phone"],
        },
        "template_name": "hpcl_lead_alert_demo",
        "message": message,
        "dossier_link": f"/leads/{lead['lead_id']}",
        "policy_note": "Sandbox preview only. Production WhatsApp requires opt-in and approved templates.",
    }


def _count_by(leads: list[dict[str, Any]], key_fn) -> dict[str, int]:
    counts: dict[str, int] = {}
    for lead in leads:
        key = str(key_fn(lead))
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _utc_timestamp() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
