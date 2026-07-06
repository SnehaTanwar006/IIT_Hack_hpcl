# Model Card

## Model Name

HPCL Direct Sales Product-Need Inference Baseline

## Version

0.2.0

## Intended Use

Recommend likely HPCL Direct Sales product families from public B2B signals such as tender text, expansion announcements, company pages, and allowed RSS/news sources.

## Inputs

- Signal title and body text.
- Company name.
- Industry.
- Location.
- Source type.
- Published date.

## Outputs

- Top product recommendations.
- Confidence score.
- Reason codes.
- Evidence counts.
- Uncertainty flag.

## Current Method

The baseline is deterministic and explainable:

- Product keywords.
- Strong indicators.
- Operational cues such as boilers, furnaces, gensets, road construction, shipping operations, jute processing, solvent extraction, and petrochemical production.
- Quantity mentions.
- Urgency terms such as tender, bid, RFQ, deadline, and closing.

## Limitations

- It may miss implicit demand when no known keyword or cue is present.
- It may over-score ambiguous abbreviations such as FO or MS.
- Geography extraction is simple and should be replaced with structured geocoding for production.
- Company size is inferred from rough text cues and known demo names.
- It does not currently learn from feedback automatically.

## Bias And Risk

- Public web signals may over-represent large companies and government tenders.
- Smaller businesses with limited web presence may be under-discovered.
- Contact enrichment must avoid unlawful or unnecessary personal data collection.

## Evaluation Plan

Use `data/seed/demo_signals_250.csv` and future manually labelled samples to track:

- Top-1 product accuracy.
- Top-3 product recall.
- Priority agreement.
- Routing accuracy by region.
- Dossier completeness.
- Provenance coverage.
