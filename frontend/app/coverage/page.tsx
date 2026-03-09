import { CoverageSnapshot, getCoverageDiff, listCoverageSnapshots } from "../../lib/api";

function getCoverageRate(snapshot: CoverageSnapshot): number | null {
  const value = snapshot.metrics_json.coverage_rate;
  if (typeof value === "number") {
    return value;
  }
  return null;
}

function fmtRate(value: number | null): string {
  if (value === null) {
    return "n/a";
  }
  return `${(value * 100).toFixed(1)}%`;
}

export default async function CoveragePage() {
  const snapshots = await listCoverageSnapshots();
  const latestDatasetId = snapshots.find((item) => item.dataset_id)?.dataset_id ?? null;
  const datasetSnapshots = latestDatasetId
    ? snapshots.filter((item) => item.dataset_id === latestDatasetId)
    : snapshots;
  const uniqueRulesets = [...new Set(datasetSnapshots.map((item) => item.ruleset_id).filter(Boolean))] as string[];

  const diff =
    latestDatasetId && uniqueRulesets.length >= 2
      ? await getCoverageDiff(latestDatasetId, uniqueRulesets[1], uniqueRulesets[0])
      : null;

  return (
    <section className="page-stack">
      <section className="card">
        <h2 className="page-title">Coverage Dashboard</h2>
        <p className="page-subtitle">
          Dataset-scoped coverage snapshots and ruleset deltas.
        </p>
      </section>

      <section className="stat-grid">
        <article className="stat-card">
          <p className="stat-label">Total Snapshots</p>
          <p className="stat-value">{snapshots.length}</p>
        </article>
        <article className="stat-card">
          <p className="stat-label">Active Dataset</p>
          <p className="stat-value">{latestDatasetId ?? "n/a"}</p>
        </article>
        <article className="stat-card">
          <p className="stat-label">Latest Coverage Rate</p>
          <p className="stat-value">
            {datasetSnapshots.length > 0 ? fmtRate(getCoverageRate(datasetSnapshots[0])) : "n/a"}
          </p>
        </article>
        <article className="stat-card">
          <p className="stat-label">Coverage Delta</p>
          <p className="stat-value">{diff ? fmtRate(diff.delta) : "n/a"}</p>
        </article>
      </section>

      {diff ? (
        <section className="card">
          <h3 className="page-title">Latest Ruleset Diff</h3>
          <dl className="kv">
            <dt>Dataset</dt>
            <dd>{diff.dataset_id}</dd>
            <dt>From Ruleset</dt>
            <dd>{diff.from_ruleset}</dd>
            <dt>To Ruleset</dt>
            <dd>{diff.to_ruleset}</dd>
            <dt>From Coverage</dt>
            <dd>{fmtRate(diff.from_coverage_rate)}</dd>
            <dt>To Coverage</dt>
            <dd>{fmtRate(diff.to_coverage_rate)}</dd>
            <dt>Delta</dt>
            <dd>{fmtRate(diff.delta)}</dd>
          </dl>
        </section>
      ) : null}

      <section className="card">
        <h3 className="page-title">Snapshot History</h3>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Snapshot ID</th>
                <th>Dataset</th>
                <th>Ruleset</th>
                <th>Computed</th>
                <th>Coverage Rate</th>
                <th>TP</th>
                <th>FP</th>
              </tr>
            </thead>
            <tbody>
              {snapshots.length === 0 ? (
                <tr>
                  <td colSpan={7} className="muted">
                    No snapshots available yet. Run `/api/replay` to generate one.
                  </td>
                </tr>
              ) : (
                snapshots.map((snapshot) => (
                  <tr key={snapshot.snapshot_id}>
                    <td className="mono">{snapshot.snapshot_id}</td>
                    <td>{snapshot.dataset_id ?? "n/a"}</td>
                    <td>{snapshot.ruleset_id ?? "n/a"}</td>
                    <td>{snapshot.computed_at ?? "n/a"}</td>
                    <td>{fmtRate(getCoverageRate(snapshot))}</td>
                    <td>{toInteger(snapshot.metrics_json.attack_tp_count)}</td>
                    <td>{toInteger(snapshot.metrics_json.baseline_fp_count)}</td>
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

function toInteger(value: unknown): string {
  if (typeof value === "number") {
    return String(Math.trunc(value));
  }
  return "n/a";
}
