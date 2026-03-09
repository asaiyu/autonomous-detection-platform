import { notFound } from "next/navigation";
import { getAlert, getAlertCase, getAlertEvidence } from "../../../lib/api";

type AlertDetailPageProps = {
  params: Promise<{ alert_id: string }>;
};

export default async function AlertDetailPage({ params }: AlertDetailPageProps) {
  const { alert_id: alertId } = await params;
  const [alert, evidence, caseRecord] = await Promise.all([
    getAlert(alertId),
    getAlertEvidence(alertId),
    getAlertCase(alertId),
  ]);

  if (!alert) {
    notFound();
  }

  return (
    <section className="page-stack">
      <section className="card">
        <h2 className="page-title">Alert Detail</h2>
        <p className="page-subtitle">
          {alert.title} · <span className="mono">{alert.alert_id}</span>
        </p>
      </section>

      <section className="split">
        <article className="card">
          <h3 className="page-title">Alert Metadata</h3>
          <dl className="kv">
            <dt>Severity</dt>
            <dd>{alert.severity}</dd>
            <dt>Status</dt>
            <dd>{alert.status}</dd>
            <dt>Category</dt>
            <dd>{alert.category ?? "n/a"}</dd>
            <dt>Type</dt>
            <dd>{alert.type ?? "n/a"}</dd>
            <dt>Rule ID</dt>
            <dd>{alert.rule_id ?? "n/a"}</dd>
            <dt>Rule Version</dt>
            <dd>{alert.rule_version ?? "n/a"}</dd>
            <dt>Confidence</dt>
            <dd>{alert.confidence ?? "n/a"}</dd>
            <dt>Created</dt>
            <dd>{alert.created_at}</dd>
          </dl>
        </article>

        <article className="card">
          <h3 className="page-title">Case & Triage</h3>
          {caseRecord ? (
            <>
              <dl className="kv">
                <dt>Case ID</dt>
                <dd className="mono">{caseRecord.case_id}</dd>
                <dt>Updated</dt>
                <dd>{caseRecord.updated_at}</dd>
              </dl>
              <h4 className="page-subtitle">Case Notes</h4>
              <pre className="pre">{caseRecord.notes_markdown ?? "No notes recorded."}</pre>
              <h4 className="page-subtitle">Triage JSON</h4>
              <pre className="pre">{JSON.stringify(caseRecord.triage_json ?? {}, null, 2)}</pre>
            </>
          ) : (
            <p className="muted">No case record yet. Trigger triage from API to create one.</p>
          )}
        </article>
      </section>

      <section className="card">
        <h3 className="page-title">Evidence Event IDs</h3>
        {evidence && evidence.evidence_event_ids.length > 0 ? (
          <ul>
            {evidence.evidence_event_ids.map((eventId) => (
              <li key={eventId} className="mono">
                {eventId}
              </li>
            ))}
          </ul>
        ) : (
          <p className="muted">No evidence event IDs found.</p>
        )}
      </section>

      <section className="card">
        <h3 className="page-title">Evidence JSON</h3>
        <pre className="pre">
          {JSON.stringify(evidence?.evidence_json ?? alert.evidence_json ?? {}, null, 2)}
        </pre>
      </section>
    </section>
  );
}
