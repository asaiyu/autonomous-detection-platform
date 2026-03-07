import Link from "next/link";
import { listRuns } from "../../lib/api";

function statusBadge(status: string): string {
  const normalized = status.toLowerCase();
  if (normalized === "completed" || normalized === "pass" || normalized === "passed") {
    return "badge badge-good";
  }
  if (normalized === "running" || normalized === "pending") {
    return "badge badge-warn";
  }
  if (normalized === "failed" || normalized === "error") {
    return "badge badge-bad";
  }
  return "badge badge-neutral";
}

export default async function RunsPage() {
  const runs = await listRuns(100);

  return (
    <section className="page-stack">
      <section className="card">
        <h2 className="page-title">Runs</h2>
        <p className="page-subtitle">
          Attack and replay executions with links to findings and validation detail.
        </p>
      </section>

      <section className="card">
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Run</th>
                <th>Status</th>
                <th>Dataset</th>
                <th>Source</th>
                <th>Start</th>
                <th>End</th>
              </tr>
            </thead>
            <tbody>
              {runs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="muted">
                    No runs yet. Trigger replay or attack generation to populate this list.
                  </td>
                </tr>
              ) : (
                runs.map((run) => (
                  <tr key={run.run_id}>
                    <td>
                      <div className="inline-links">
                        <Link href={`/runs/${run.run_id}`}>{run.name}</Link>
                      </div>
                      <div className="mono muted">{run.run_id}</div>
                    </td>
                    <td>
                      <span className={statusBadge(run.status)}>{run.status}</span>
                    </td>
                    <td>{run.dataset_id ?? "n/a"}</td>
                    <td>{run.attack_source ?? "n/a"}</td>
                    <td>{run.start_time ?? "n/a"}</td>
                    <td>{run.end_time ?? "n/a"}</td>
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
