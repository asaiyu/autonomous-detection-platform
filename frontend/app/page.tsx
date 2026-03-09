import Link from "next/link";
import { getHealth, listAlerts, listCoverageSnapshots, listRules, listRuns } from "../lib/api";

export default async function HomePage() {
  const [health, runs, alerts, snapshots, rules] = await Promise.all([
    getHealth(),
    listRuns(20),
    listAlerts(20),
    listCoverageSnapshots(),
    listRules(),
  ]);

  return (
    <section className="page-stack">
      <section className="card">
        <h2 className="page-title">Platform Overview</h2>
        <p className="page-subtitle">
          Live status and recent telemetry from the FastAPI backend.
        </p>
      </section>

      <section className="stat-grid">
        <article className="stat-card">
          <p className="stat-label">Backend Health</p>
          <p className="stat-value">{health.status}</p>
        </article>
        <article className="stat-card">
          <p className="stat-label">Recent Runs</p>
          <p className="stat-value">{runs.length}</p>
        </article>
        <article className="stat-card">
          <p className="stat-label">Recent Alerts</p>
          <p className="stat-value">{alerts.length}</p>
        </article>
        <article className="stat-card">
          <p className="stat-label">Coverage Snapshots</p>
          <p className="stat-value">{snapshots.length}</p>
        </article>
        <article className="stat-card">
          <p className="stat-label">Loaded Rules</p>
          <p className="stat-value">{rules.length}</p>
        </article>
      </section>

      <section className="card">
        <h3 className="page-title">Quick Navigation</h3>
        <div className="inline-links">
          <Link href="/coverage">Coverage Snapshots</Link>
          <Link href="/runs">Attack & Replay Runs</Link>
          <Link href="/alerts">Alert Investigations</Link>
          <Link href="/rules">Rule Library</Link>
        </div>
      </section>
    </section>
  );
}
