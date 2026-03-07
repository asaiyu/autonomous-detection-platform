import { notFound } from "next/navigation";
import { getRun, getRunFindings, getRunReport } from "../../../lib/api";

type RunDetailPageProps = {
  params: Promise<{ run_id: string }>;
};

export default async function RunDetailPage({ params }: RunDetailPageProps) {
  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
  const { run_id: runId } = await params;
  const [run, findings, report] = await Promise.all([
    getRun(runId),
    getRunFindings(runId, 1000),
    getRunReport(runId),
  ]);

  if (!run) {
    notFound();
  }

  return (
    <section className="page-stack">
      <section className="card">
        <h2 className="page-title">Run Detail</h2>
        <p className="page-subtitle">
          {run.name} · <span className="mono">{run.run_id}</span>
        </p>
      </section>

      <section className="split">
        <article className="card">
          <h3 className="page-title">Run Metadata</h3>
          <dl className="kv">
            <dt>Status</dt>
            <dd>{run.status}</dd>
            <dt>Dataset</dt>
            <dd>{run.dataset_id ?? "n/a"}</dd>
            <dt>Attack Source</dt>
            <dd>{run.attack_source ?? "n/a"}</dd>
            <dt>Target</dt>
            <dd>{run.target ?? "n/a"}</dd>
            <dt>Start</dt>
            <dd>{run.start_time ?? "n/a"}</dd>
            <dt>End</dt>
            <dd>{run.end_time ?? "n/a"}</dd>
          </dl>
        </article>

        <article className="card">
          <h3 className="page-title">Coverage Lifecycle</h3>
          <dl className="kv">
            <dt>Findings</dt>
            <dd>{findings.length}</dd>
            <dt>Evaluations</dt>
            <dd>{report?.coverage_evaluations.length ?? 0}</dd>
            <dt>Rule Proposals</dt>
            <dd>{report?.rule_proposals.length ?? 0}</dd>
            <dt>Replay Validations</dt>
            <dd>{report?.replay_validations.length ?? 0}</dd>
          </dl>
          <div className="inline-links">
            <a href={`${apiBase}/api/audit/runs/${runId}/report?format=markdown`} target="_blank">
              Open Markdown Report
            </a>
          </div>
        </article>
      </section>

      <section className="card">
        <h3 className="page-title">Findings</h3>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Finding</th>
                <th>Type</th>
                <th>Severity</th>
                <th>Technique</th>
                <th>Occurred</th>
              </tr>
            </thead>
            <tbody>
              {findings.length === 0 ? (
                <tr>
                  <td colSpan={5} className="muted">
                    No findings associated with this run.
                  </td>
                </tr>
              ) : (
                findings.map((finding) => (
                  <tr key={finding.finding_id}>
                    <td>
                      <div>{finding.title ?? "Untitled finding"}</div>
                      <div className="mono muted">{finding.finding_id}</div>
                    </td>
                    <td>{finding.finding_type}</td>
                    <td>{finding.severity ?? "n/a"}</td>
                    <td>{finding.technique ?? "n/a"}</td>
                    <td>{finding.occurred_at ?? "n/a"}</td>
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
