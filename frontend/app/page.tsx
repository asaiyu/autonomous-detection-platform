import { getHealth } from "../lib/api";

export default async function HomePage() {
  const health = await getHealth();

  return (
    <section className="card">
      <h2>MVP Dashboard</h2>
      <p>Backend health: {health.status}</p>
      <p>Use the top navigation to access Coverage, Runs, Alerts, and Rules placeholders.</p>
    </section>
  );
}
