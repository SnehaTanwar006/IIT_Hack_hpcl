import { Bell, CheckCircle2, Filter, MapPinned, RefreshCw, XCircle } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

type Product = {
  product_code: string;
  product_name: string;
  confidence: number;
  reason_codes: string[];
};

type Lead = {
  lead_id: string;
  status: string;
  priority: string;
  company: {
    canonical_name: string;
    industry: string;
    geography: { headquarters: string };
  };
  signal: {
    title: string;
    summary: string;
    source_type: string;
    source_name: string;
    source_url: string;
  };
  products: Product[];
  score: {
    total_score: number;
    breakdown: Record<string, { score: number; evidence?: string; type?: string; level?: string }>;
  };
  routing: {
    assigned_officer: string;
    region: string;
    depot: string;
    match_reason: string;
  };
  next_best_action: string;
};

type Analytics = {
  total_leads: number;
  by_priority: Record<string, number>;
  by_region: Record<string, number>;
  by_product: Record<string, number>;
  conversion_funnel: Record<string, number>;
};

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

const fallbackLeads: Lead[] = [
  {
    lead_id: "LEAD-DEMO-0001",
    status: "NEW",
    priority: "CRITICAL",
    company: {
      canonical_name: "National Highways Authority Demo Unit",
      industry: "Infrastructure",
      geography: { headquarters: "Vadodara, Gujarat" },
    },
    signal: {
      title: "Tender for Bitumen VG-30 for highway widening package",
      summary: "Supply of 15,000 MT bitumen for road construction and paving works.",
      source_type: "tender",
      source_name: "GeM",
      source_url: "https://demo.example.com/signals/sig-demo-0001",
    },
    products: [
      {
        product_code: "BITUMEN",
        product_name: "Bitumen",
        confidence: 0.6,
        reason_codes: ["Matched: bitumen requirement", "Operational cue: road construction"],
      },
    ],
    score: {
      total_score: 88,
      breakdown: {
        intent: { score: 40, type: "tender", evidence: "Pre-classified as tender" },
        freshness: { score: 15, level: "FRESH" },
        company_size: { score: 20, evidence: "Capacity: 15000 MT" },
        proximity: { score: 7, evidence: "Same region: Gujarat" },
      },
    },
    routing: {
      assigned_officer: "Demo Officer West Infra",
      region: "West",
      depot: "Ahmedabad",
      match_reason: "Specialization match: Infrastructure",
    },
    next_best_action: "Call procurement contact and share Bitumen quotation pack within 24 hours.",
  },
];

export function App() {
  const [leads, setLeads] = useState<Lead[]>(fallbackLeads);
  const [selectedId, setSelectedId] = useState(fallbackLeads[0].lead_id);
  const [priority, setPriority] = useState("ALL");
  const [alertPreview, setAlertPreview] = useState("");

  async function loadLeads() {
    try {
      const response = await fetch(`${API_BASE}/leads`);
      if (!response.ok) throw new Error("API unavailable");
      const data = await response.json();
      setLeads(data);
      setSelectedId(data[0]?.lead_id ?? fallbackLeads[0].lead_id);
    } catch {
      setLeads(fallbackLeads);
    }
  }

  useEffect(() => {
    loadLeads();
  }, []);

  const filtered = useMemo(
    () => leads.filter((lead) => priority === "ALL" || lead.priority === priority),
    [leads, priority]
  );
  const selected = leads.find((lead) => lead.lead_id === selectedId) ?? filtered[0] ?? leads[0];
  const analytics = buildAnalytics(leads);

  async function updateStatus(status: "ACCEPTED" | "REJECTED" | "CONVERTED") {
    try {
      const response = await fetch(`${API_BASE}/leads/${selected.lead_id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status, note: `Updated from dashboard to ${status}` }),
      });
      if (!response.ok) throw new Error("Status update failed");
      await loadLeads();
    } catch {
      setLeads((current) =>
        current.map((lead) => (lead.lead_id === selected.lead_id ? { ...lead, status } : lead))
      );
    }
  }

  async function previewAlert() {
    try {
      const response = await fetch(`${API_BASE}/leads/${selected.lead_id}/notifications/preview`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ channel: "whatsapp" }),
      });
      const data = await response.json();
      setAlertPreview(data.message);
    } catch {
      setAlertPreview(`HPCL Lead Alert: ${selected.company.canonical_name} | ${selected.priority}`);
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">HPCL Direct Sales</p>
          <h1>B2B Lead Intelligence</h1>
        </div>
        <nav>
          <button className="nav-item active">
            <MapPinned size={18} /> Lead Queue
          </button>
          <button className="nav-item">
            <Bell size={18} /> Alerts
          </button>
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Recruiter demo mode</p>
            <h2>Explainable dossiers from public B2B signals</h2>
          </div>
          <button className="icon-button" onClick={loadLeads} title="Refresh leads">
            <RefreshCw size={18} />
          </button>
        </header>

        <section className="metrics-grid">
          <Metric label="Total leads" value={analytics.total_leads} tone="ink" />
          <Metric label="Critical" value={analytics.by_priority.CRITICAL ?? 0} tone="red" />
          <Metric label="Accepted" value={analytics.conversion_funnel.accepted ?? 0} tone="green" />
          <Metric label="Regions" value={Object.keys(analytics.by_region).length} tone="blue" />
        </section>

        <section className="content-grid">
          <section className="queue-panel">
            <div className="panel-header">
              <h3>New Leads</h3>
              <label className="filter">
                <Filter size={16} />
                <select value={priority} onChange={(event) => setPriority(event.target.value)}>
                  <option value="ALL">All priorities</option>
                  <option value="CRITICAL">Critical</option>
                  <option value="HIGH">High</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="LOW">Low</option>
                </select>
              </label>
            </div>
            <div className="lead-list">
              {filtered.map((lead) => (
                <button
                  key={lead.lead_id}
                  className={`lead-row ${lead.lead_id === selected.lead_id ? "selected" : ""}`}
                  onClick={() => setSelectedId(lead.lead_id)}
                >
                  <span className={`priority ${lead.priority.toLowerCase()}`}>{lead.priority}</span>
                  <strong>{lead.company.canonical_name}</strong>
                  <span>{lead.signal.title}</span>
                </button>
              ))}
            </div>
          </section>

          <section className="dossier-panel">
            <div className="dossier-title">
              <div>
                <p className="eyebrow">{selected.signal.source_name}</p>
                <h3>{selected.company.canonical_name}</h3>
              </div>
              <span className={`status ${selected.status.toLowerCase()}`}>{selected.status}</span>
            </div>

            <div className="dossier-grid">
              <InfoBlock label="Industry" value={selected.company.industry || "Needs enrichment"} />
              <InfoBlock label="Location" value={selected.company.geography.headquarters} />
              <InfoBlock label="Assigned" value={selected.routing.assigned_officer} />
              <InfoBlock label="Score" value={`${selected.score.total_score}/90`} />
            </div>

            <article className="signal-box">
              <h4>{selected.signal.title}</h4>
              <p>{selected.signal.summary}</p>
              <a href={selected.signal.source_url} target="_blank" rel="noreferrer">
                View source
              </a>
            </article>

            <section>
              <h4>Top Product Fit</h4>
              <div className="product-list">
                {selected.products.map((product) => (
                  <div className="product-item" key={product.product_code}>
                    <div>
                      <strong>{product.product_name}</strong>
                      <span>{product.reason_codes.join(" | ")}</span>
                    </div>
                    <meter value={product.confidence} min="0" max="1" />
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h4>Next Best Action</h4>
              <p className="action-text">{selected.next_best_action}</p>
            </section>

            <div className="actions">
              <button onClick={() => updateStatus("ACCEPTED")}>
                <CheckCircle2 size={16} /> Accept
              </button>
              <button onClick={() => updateStatus("CONVERTED")}>
                <CheckCircle2 size={16} /> Converted
              </button>
              <button className="danger" onClick={() => updateStatus("REJECTED")}>
                <XCircle size={16} /> Reject
              </button>
              <button className="secondary" onClick={previewAlert}>
                <Bell size={16} /> Preview alert
              </button>
            </div>

            {alertPreview && <p className="alert-preview">{alertPreview}</p>}
          </section>
        </section>
      </section>
    </main>
  );
}

function Metric({ label, value, tone }: { label: string; value: number; tone: string }) {
  return (
    <div className={`metric ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function InfoBlock({ label, value }: { label: string; value: string }) {
  return (
    <div className="info-block">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function buildAnalytics(leads: Lead[]): Analytics {
  return {
    total_leads: leads.length,
    by_priority: countBy(leads, (lead) => lead.priority),
    by_region: countBy(leads, (lead) => lead.routing.region),
    by_product: countBy(leads, (lead) => lead.products[0]?.product_code ?? "REVIEW"),
    conversion_funnel: countBy(leads, (lead) => lead.status.toLowerCase()),
  };
}

function countBy<T>(items: T[], keyFn: (item: T) => string): Record<string, number> {
  return items.reduce<Record<string, number>>((counts, item) => {
    const key = keyFn(item);
    counts[key] = (counts[key] ?? 0) + 1;
    return counts;
  }, {});
}
