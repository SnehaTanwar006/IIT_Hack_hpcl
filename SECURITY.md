# Security And Responsible Data Use

This project is a recruiter-facing prototype and uses synthetic demo data by default.

Production deployments must:

- Prefer official APIs, RSS feeds, public datasets, and permitted crawling.
- Respect robots.txt, source terms, rate limits, and source-specific governance rules.
- Store provenance for every extracted fact: source URL, timestamp, access method, and trust score.
- Avoid personal data unless it is lawful, necessary, documented, and protected.
- Use WhatsApp only for opted-in employee notifications with approved templates.
- Keep provider tokens and API keys in environment variables, never in Git.

Please report security issues privately to the repository owner instead of opening a public issue.
