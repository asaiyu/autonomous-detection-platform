type RunDetailPageProps = {
  params: { run_id: string };
};

export default function RunDetailPage({ params }: RunDetailPageProps) {
  const { run_id } = params;
  return (
    <section className="card">
      <h2>Run Detail</h2>
      <p>Run ID: {run_id}</p>
      <p>Findings and coverage details will be rendered here.</p>
    </section>
  );
}
