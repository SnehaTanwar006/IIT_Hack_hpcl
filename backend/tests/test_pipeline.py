from datetime import datetime

from backend.app.core.pipeline import (
    DemoSignal,
    LeadIntelligencePipeline,
    LeadRepository,
    preview_notification,
)


def test_product_inference_recommends_bitumen_for_highway_tender():
    signal = DemoSignal(
        signal_id="TEST-001",
        source_type="tender",
        source_name="GeM",
        source_url="https://example.test/tender/1",
        title="Tender for Bitumen VG-30 for NH highway project",
        text="Supply of 15,000 MT bitumen for road construction and highway widening.",
        company_name="National Highways Authority",
        location="Vadodara, Gujarat",
        industry="Infrastructure",
        published_at=datetime.now(),
        expected_products=["BITUMEN"],
        expected_priority="CRITICAL",
    )
    lead = LeadIntelligencePipeline().process_signal(signal, index=1)

    assert lead["products"][0]["product_code"] == "BITUMEN"
    assert lead["priority"] == "CRITICAL"
    assert lead["provenance"]["source_url"] == "https://example.test/tender/1"


def test_feedback_loop_updates_status_and_notes():
    repository = LeadRepository(
        [
            {
                "lead_id": "LEAD-DEMO-0001",
                "status": "NEW",
                "priority": "HIGH",
                "feedback": {"status": "NEW", "notes": [], "updated_at": None},
                "routing": {"region": "West"},
                "products": [{"product_code": "HSD"}],
                "signal": {"source_type": "tender"},
            }
        ]
    )

    updated = repository.update_status("LEAD-DEMO-0001", "ACCEPTED", "Sales officer accepted")

    assert updated["status"] == "ACCEPTED"
    assert updated["feedback"]["notes"][0]["note"] == "Sales officer accepted"
    assert repository.analytics()["conversion_funnel"]["accepted"] == 1


def test_notification_preview_is_sandboxed():
    lead = {
        "lead_id": "LEAD-DEMO-0002",
        "priority": "HIGH",
        "company": {"canonical_name": "Tata Steel Limited"},
        "products": [{"product_name": "Furnace Oil"}],
        "next_best_action": "Validate fuel demand this week.",
        "routing": {
            "assigned_officer": "Demo Officer West",
            "email": "demo.west@example.com",
            "phone": "+91-9000000000",
        },
    }

    preview = preview_notification(lead)

    assert preview["mode"] == "sandbox"
    assert "Production WhatsApp requires opt-in" in preview["policy_note"]
