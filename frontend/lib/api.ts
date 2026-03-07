const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type ApiListResponse<T> = {
  count: number;
  items: T[];
};

type RequestOptions = {
  method?: "GET" | "POST" | "PATCH";
  body?: unknown;
  allowNotFound?: boolean;
};

export type HealthResponse = {
  status: string;
};

export type CoverageSnapshot = {
  snapshot_id: string;
  dataset_id: string | null;
  ruleset_id: string | null;
  computed_at: string | null;
  metrics_json: Record<string, unknown>;
};

export type CoverageDiff = {
  dataset_id: string;
  from_ruleset: string;
  to_ruleset: string;
  from_coverage_rate: number | null;
  to_coverage_rate: number | null;
  delta: number | null;
};

export type RunSummary = {
  run_id: string;
  name: string;
  attack_source: string | null;
  dataset_id: string | null;
  target: string | null;
  status: string;
  summary: string | null;
  config_json: Record<string, unknown> | null;
  config_hash: string | null;
  start_time: string | null;
  end_time: string | null;
  created_at: string;
};

export type RunFinding = {
  finding_id: string;
  run_id: string | null;
  finding_type: string;
  title: string | null;
  severity: string | null;
  technique: string | null;
  occurred_at: string | null;
  entrypoint_json: Record<string, unknown> | null;
  proof_json: Record<string, unknown> | null;
  tags_json: Record<string, unknown> | null;
};

export type RunReport = {
  run_id: string;
  run_metadata: Record<string, unknown>;
  findings: Array<Record<string, unknown>>;
  coverage_evaluations: Array<Record<string, unknown>>;
  rule_proposals: Array<Record<string, unknown>>;
  replay_validations: Array<Record<string, unknown>>;
  generated_at: string;
};

export type AlertSummary = {
  alert_id: string;
  event_id: string | null;
  rule_id: string | null;
  rule_version: number | null;
  severity: string;
  title: string;
  category: string | null;
  type: string | null;
  status: string;
  confidence: number | null;
  description: string | null;
  evidence_event_ids: string[];
  evidence_json: Record<string, unknown>;
  tags: string[];
  metadata: Record<string, unknown> | null;
  created_at: string;
};

export type AlertEvidence = {
  alert_id: string;
  evidence_event_ids: string[];
  evidence_json: Record<string, unknown>;
};

export type CaseRecord = {
  case_id: string;
  alert_id: string;
  notes_markdown: string | null;
  triage_json: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
};

export type RuleSummary = {
  id: string;
  name: string;
  severity: string;
  version: number;
  detect_type: string;
  enabled: boolean;
};

export type RuleDetail = {
  id: string;
  name: string;
  description: string;
  severity: string;
  enabled: boolean;
  log_sources: string[];
  tags: string[];
  version: number;
  detect: Record<string, unknown>;
  output: Record<string, unknown>;
  evidence_include_fields: string[];
};

async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T | null> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? "GET",
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
    },
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  });

  if (response.status === 404 && options.allowNotFound) {
    return null;
  }

  if (!response.ok) {
    throw new Error(`API request failed (${response.status}) for ${path}`);
  }

  return (await response.json()) as T;
}

function queryString(params: Record<string, string | number | undefined | null>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") {
      continue;
    }
    search.set(key, String(value));
  }

  const encoded = search.toString();
  return encoded ? `?${encoded}` : "";
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await apiRequest<HealthResponse>("/api/health");
  return response ?? { status: "unreachable" };
}

export async function listCoverageSnapshots(datasetId?: string): Promise<CoverageSnapshot[]> {
  const response = await apiRequest<ApiListResponse<CoverageSnapshot>>(
    `/api/coverage/snapshots${queryString({ dataset_id: datasetId, limit: 50 })}`,
  );
  return response?.items ?? [];
}

export async function getCoverageDiff(
  datasetId: string,
  fromRuleset: string,
  toRuleset: string,
): Promise<CoverageDiff | null> {
  return apiRequest<CoverageDiff>(
    `/api/coverage/diff${queryString({
      dataset_id: datasetId,
      from_ruleset: fromRuleset,
      to_ruleset: toRuleset,
    })}`,
    { allowNotFound: true },
  );
}

export async function listRuns(limit = 100): Promise<RunSummary[]> {
  const response = await apiRequest<ApiListResponse<RunSummary>>(
    `/api/runs${queryString({ limit })}`,
  );
  return response?.items ?? [];
}

export async function getRun(runId: string): Promise<RunSummary | null> {
  return apiRequest<RunSummary>(`/api/runs/${runId}`, { allowNotFound: true });
}

export async function getRunFindings(runId: string, limit = 500): Promise<RunFinding[]> {
  const response = await apiRequest<ApiListResponse<RunFinding>>(
    `/api/runs/${runId}/findings${queryString({ limit })}`,
  );
  return response?.items ?? [];
}

export async function getRunReport(runId: string): Promise<RunReport | null> {
  return apiRequest<RunReport>(`/api/audit/runs/${runId}/report`, { allowNotFound: true });
}

export async function listAlerts(limit = 100, query?: string): Promise<AlertSummary[]> {
  const response = await apiRequest<ApiListResponse<AlertSummary>>(
    `/api/alerts${queryString({ limit, query })}`,
  );
  return response?.items ?? [];
}

export async function getAlert(alertId: string): Promise<AlertSummary | null> {
  return apiRequest<AlertSummary>(`/api/alerts/${alertId}`, { allowNotFound: true });
}

export async function getAlertEvidence(alertId: string): Promise<AlertEvidence | null> {
  return apiRequest<AlertEvidence>(`/api/alerts/${alertId}/evidence`, { allowNotFound: true });
}

export async function getAlertCase(alertId: string): Promise<CaseRecord | null> {
  return apiRequest<CaseRecord>(`/api/alerts/${alertId}/case`, { allowNotFound: true });
}

export async function listRules(rulesetId?: string): Promise<RuleSummary[]> {
  const response = await apiRequest<RuleSummary[]>(
    `/api/rules${queryString({ ruleset_id: rulesetId })}`,
  );
  return response ?? [];
}

export async function getRule(ruleId: string, rulesetId?: string): Promise<RuleDetail | null> {
  return apiRequest<RuleDetail>(
    `/api/rules/${ruleId}${queryString({ ruleset_id: rulesetId })}`,
    { allowNotFound: true },
  );
}
