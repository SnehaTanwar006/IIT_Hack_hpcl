# Contributing

This repository is organized as a portfolio-grade product prototype. Contributions should keep the project easy to run, explain, and review.

## Local Setup

```bash
pip install -e .[dev]
python scripts/seed_demo_data.py
pytest
```

For the dashboard:

```bash
cd frontend
npm install
npm run dev
```

## Development Guidelines

- Keep generated files out of Git.
- Add tests for inference, scoring, routing, feedback, and API behavior.
- Keep source governance and data provenance visible in every ingestion-related change.
- Use synthetic data unless a source is explicitly public, lawful, and documented.
- Update the README and docs when product behavior changes.
