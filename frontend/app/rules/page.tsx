import { getRule, listRules } from "../../lib/api";

export default async function RulesPage() {
  const rules = await listRules();
  const highlighted = rules.length > 0 ? await getRule(rules[0].id) : null;

  return (
    <section className="page-stack">
      <section className="card">
        <h2 className="page-title">Rule Library</h2>
        <p className="page-subtitle">
          Deterministic detection rules loaded from the backend rules directory.
        </p>
      </section>

      <section className="card">
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Rule ID</th>
                <th>Name</th>
                <th>Severity</th>
                <th>Version</th>
                <th>Detect Type</th>
                <th>Enabled</th>
              </tr>
            </thead>
            <tbody>
              {rules.length === 0 ? (
                <tr>
                  <td colSpan={6} className="muted">
                    No rule YAML files found.
                  </td>
                </tr>
              ) : (
                rules.map((rule) => (
                  <tr key={rule.id}>
                    <td className="mono">{rule.id}</td>
                    <td>{rule.name}</td>
                    <td>{rule.severity}</td>
                    <td>{rule.version}</td>
                    <td>{rule.detect_type}</td>
                    <td>{rule.enabled ? "yes" : "no"}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>

      {highlighted ? (
        <section className="card">
          <h3 className="page-title">Highlighted Rule</h3>
          <dl className="kv">
            <dt>ID</dt>
            <dd className="mono">{highlighted.id}</dd>
            <dt>Description</dt>
            <dd>{highlighted.description || "n/a"}</dd>
            <dt>Log Sources</dt>
            <dd>{highlighted.log_sources.join(", ") || "n/a"}</dd>
            <dt>Tags</dt>
            <dd>{highlighted.tags.join(", ") || "n/a"}</dd>
          </dl>
          <h4 className="page-subtitle">Detect Block</h4>
          <pre className="pre">{JSON.stringify(highlighted.detect, null, 2)}</pre>
        </section>
      ) : null}
    </section>
  );
}
