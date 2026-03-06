const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type HealthResponse = {
  status: string;
};

export type CoverageSnapshot = {
  snapshot_id: string;
  dataset_id: string | null;
  ruleset_id: string | null;
  computed_at: string | null;
  metrics_json: Record<string, unknown>;
};

export type RunSummary = {
  run_id: string;
  name: string;
  status: string;
};

export type AlertSummary = {
  alert_id: string;
  title: string;
  severity: string;
  status: string;
};

export async function getHealth(): Promise<HealthResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: "GET",
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      return { status: "unreachable" };
    }

    return (await response.json()) as HealthResponse;
  } catch {
    return { status: "unreachable" };
  }
}

export async function listCoverageSnapshots(datasetId?: string): Promise<CoverageSnapshot[]> {
  const search = datasetId ? `?dataset_id=${encodeURIComponent(datasetId)}` : "";
  const response = await fetch(`${API_BASE_URL}/api/coverage/snapshots${search}`, {
    method: "GET",
    cache: "no-store",
  });
  if (!response.ok) {
    return [];
  }
  const data = (await response.json()) as { items?: CoverageSnapshot[] };
  return data.items ?? [];
}

export async function listRuns(): Promise<RunSummary[]> {
  const response = await fetch(`${API_BASE_URL}/api/runs`, {
    method: "GET",
    cache: "no-store",
  });
  if (!response.ok) {
    return [];
  }
  const data = (await response.json()) as { items?: RunSummary[] };
  return data.items ?? [];
}

export async function listAlerts(): Promise<AlertSummary[]> {
  const response = await fetch(`${API_BASE_URL}/api/alerts`, {
    method: "GET",
    cache: "no-store",
  });
  if (!response.ok) {
    return [];
  }
  const data = (await response.json()) as { items?: AlertSummary[] };
  return data.items ?? [];
}
