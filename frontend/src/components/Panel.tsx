export default function Panel({ children }) {
  return (
    <section className="panel-surface rounded-xl border border-border bg-card p-6 shadow-sm">
      {children}
    </section>
  );
}
