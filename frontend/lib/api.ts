const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type HealthResponse = {
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
