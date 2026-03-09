import Link from "next/link";
import { listAlerts } from "../../lib/api";

function severityClass(severity: string): string {
  const normalized = severity.toLowerCase();
  if (normalized === "critical" || normalized === "high") {
    return "badge badge-bad";
  }
  if (normalized === "medium") {
    return "badge badge-warn";
  }
  return "badge badge-neutral";
}

function statusClass(status: string): string {
  const normalized = status.toLowerCase();
  if (normalized === "closed" || normalized === "resolved") {
    return "badge badge-good";
  }
  if (normalized === "open" || normalized === "triage") {
    return "badge badge-warn";
  }
  return "badge badge-neutral";
}

export default async function AlertsPage() {
  const alerts = await listAlerts(200);

  return (
    <section className="page-stack">
      <section className="card">
        <h2 className="page-title">Alerts</h2>
        <p className="page-subtitle">
          Alert list with severity, status, evidence counts, and investigation links.
        </p>
      </section>

      <section className="card">
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Alert</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Rule</th>
                <th>Evidence Events</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {alerts.length === 0 ? (
                <tr>
                  <td colSpan={6} className="muted">
                    No alerts found. Replays or rules must fire before this list is populated.
                  </td>
                </tr>
              ) : (
                alerts.map((alert) => (
                  <tr key={alert.alert_id}>
                    <td>
                      <div className="inline-links">
                        <Link href={`/alerts/${alert.alert_id}`}>{alert.title}</Link>
                      </div>
                      <div className="mono muted">{alert.alert_id}</div>
                    </td>
                    <td>
                      <span className={severityClass(alert.severity)}>{alert.severity}</span>
                    </td>
                    <td>
                      <span className={statusClass(alert.status)}>{alert.status}</span>
                    </td>
                    <td>
                      <div>{alert.rule_id ?? "n/a"}</div>
                      <div className="muted">v{alert.rule_version ?? "n/a"}</div>
                    </td>
                    <td>{alert.evidence_event_ids.length}</td>
                    <td>{alert.created_at}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}
