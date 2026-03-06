type AlertDetailPageProps = {
  params: { alert_id: string };
};

export default function AlertDetailPage({ params }: AlertDetailPageProps) {
  const { alert_id } = params;

  return (
    <section className="card">
      <h2>Alert Detail</h2>
      <p>Alert ID: {alert_id}</p>
      <p>Evidence bundle and triage notes will be rendered here.</p>
    </section>
  );
}
