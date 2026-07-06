"""Generate a deterministic labelled demo dataset for the HPCL prototype."""

from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "seed" / "demo_signals_250.csv"


TEMPLATES = [
    {
        "source_type": "tender",
        "source_name": "GeM",
        "title": "Tender for Bitumen VG-30 for highway widening package",
        "text": "Supply of {qty} MT bitumen for road construction and paving works near {city}. Bid closing within 10 days.",
        "company": "National Highways Authority Demo Unit",
        "industry": "Infrastructure",
        "location": "{city}, {state}",
        "products": "BITUMEN",
        "priority": "CRITICAL",
    },
    {
        "source_type": "news",
        "source_name": "Business News RSS",
        "title": "Steel manufacturer announces new blast furnace capacity",
        "text": "{company} plans a {qty} MTPA expansion with boilers, furnace operations, and captive power needs.",
        "company": "{company}",
        "industry": "Steel",
        "location": "{city}, {state}",
        "products": "FO|LSHS|HSD",
        "priority": "HIGH",
    },
    {
        "source_type": "company_page",
        "source_name": "Company Website",
        "title": "Edible oil plant expansion with solvent extraction line",
        "text": "{company} is commissioning a solvent extraction plant and oil mill using hexane recovery systems.",
        "company": "{company}",
        "industry": "Edible Oil",
        "location": "{city}, {state}",
        "products": "HEXANE",
        "priority": "HIGH",
    },
    {
        "source_type": "tender",
        "source_name": "eProcure",
        "title": "Supply of High Speed Diesel for mining fleet and DG sets",
        "text": "Procurement requirement for {qty} KL HSD diesel for heavy vehicles, backup power, and mining operations.",
        "company": "{company}",
        "industry": "Mining",
        "location": "{city}, {state}",
        "products": "HSD",
        "priority": "CRITICAL",
    },
    {
        "source_type": "news",
        "source_name": "Industry RSS",
        "title": "Jute mill adds batching unit in eastern region",
        "text": "{company} has installed a new jute processing and fiber batching unit for higher production.",
        "company": "{company}",
        "industry": "Jute Manufacturing",
        "location": "{city}, {state}",
        "products": "JBO",
        "priority": "MEDIUM",
    },
    {
        "source_type": "tender",
        "source_name": "Port Tender Portal",
        "title": "Marine bunker fuel requirement for vessel refueling",
        "text": "Tender for bunker fuel, HSD, and vessel refueling support at port operations.",
        "company": "{company}",
        "industry": "Shipping",
        "location": "{city}, {state}",
        "products": "MARINE_BUNKERS|HSD",
        "priority": "CRITICAL",
    },
    {
        "source_type": "company_page",
        "source_name": "Company Website",
        "title": "Paint manufacturer opens new resin and thinner line",
        "text": "{company} requires mineral turpentine oil, solvent 1425, paint thinner, and cleaning solvent for manufacturing.",
        "company": "{company}",
        "industry": "Paints",
        "location": "{city}, {state}",
        "products": "MTO|SOLVENT_1425",
        "priority": "HIGH",
    },
    {
        "source_type": "news",
        "source_name": "Chemical Industry RSS",
        "title": "Fertilizer complex capacity expansion announced",
        "text": "{company} is expanding fertilizer production and sulfuric acid capacity with molten sulphur handling.",
        "company": "{company}",
        "industry": "Fertilizers",
        "location": "{city}, {state}",
        "products": "SULPHUR",
        "priority": "HIGH",
    },
    {
        "source_type": "company_page",
        "source_name": "Company Website",
        "title": "Polypropylene unit planned by petrochemical manufacturer",
        "text": "{company} disclosed a petrochemical expansion involving propylene and polymer production.",
        "company": "{company}",
        "industry": "Petrochemicals",
        "location": "{city}, {state}",
        "products": "PROPYLENE",
        "priority": "HIGH",
    },
    {
        "source_type": "tender",
        "source_name": "State Procurement Portal",
        "title": "Light diesel oil requirement for ceramic kilns",
        "text": "Tender notice for LDO supply to medium speed engines, kilns, and industrial heating units.",
        "company": "{company}",
        "industry": "Ceramics",
        "location": "{city}, {state}",
        "products": "LDO",
        "priority": "CRITICAL",
    },
]

LOCATIONS = [
    ("Vadodara", "Gujarat"),
    ("Jamshedpur", "Jharkhand"),
    ("Mumbai", "Maharashtra"),
    ("Kolkata", "West Bengal"),
    ("Chennai", "Tamil Nadu"),
    ("Hyderabad", "Telangana"),
    ("Jaipur", "Rajasthan"),
    ("Bengaluru", "Karnataka"),
    ("Pune", "Maharashtra"),
    ("Visakhapatnam", "Andhra Pradesh"),
]

COMPANIES = [
    "Aarav Industrial Works",
    "Bharat Process Industries",
    "Coromandel Demo Chemicals",
    "Dakshin Energy Systems",
    "Eastern Jute Mills",
    "Frontier Infra Projects",
    "Ganga Petrochem Demo",
    "Himalaya Minerals",
    "Indus Paints and Coatings",
    "Jai Bharat Foods",
]


def build_rows(total: int = 250) -> list[dict[str, str]]:
    rows = []
    start = date(2026, 7, 1)
    for index in range(total):
        template = TEMPLATES[index % len(TEMPLATES)]
        city, state = LOCATIONS[index % len(LOCATIONS)]
        company = COMPANIES[index % len(COMPANIES)]
        qty = 500 + (index % 40) * 250
        signal_id = f"SIG-DEMO-{index + 1:04d}"
        rows.append(
            {
                "signal_id": signal_id,
                "source_type": template["source_type"],
                "source_name": template["source_name"],
                "source_url": f"https://demo.example.com/signals/{signal_id.lower()}",
                "title": template["title"].format(company=company, city=city, state=state, qty=qty),
                "text": template["text"].format(company=company, city=city, state=state, qty=qty),
                "company_name": template["company"].format(company=company, city=city, state=state, qty=qty),
                "location": template["location"].format(company=company, city=city, state=state, qty=qty),
                "industry": template["industry"],
                "published_at": (start + timedelta(days=index % 14)).isoformat(),
                "expected_products": template["products"],
                "expected_priority": template["priority"],
            }
        )
    return rows


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rows = build_rows()
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} demo signals to {OUTPUT}")


if __name__ == "__main__":
    main()
