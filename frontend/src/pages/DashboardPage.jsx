import { useEffect, useState } from 'react';
import { getAnalyticsSummary, getSalaryAnalytics } from '../api';

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([getSalaryAnalytics(), getAnalyticsSummary()])
      .then(([salary, summary]) => {
        if (!cancelled) setAnalytics({ salary, summary });
      })
      .catch((loadError) => {
        if (!cancelled) setError(loadError.message);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div>
      <PageIntro
        eyebrow="Market overview"
        title="Job market dashboard"
        description="A focused view of salary patterns and the latest technology job market snapshot."
      />
      {!analytics && !error && <Panel>Loading analytics...</Panel>}
      {error && (
        <Panel>
          <h2 className="font-semibold">Unable to load analytics</h2>
          <p className="mt-1 text-sm text-muted-foreground">{error}</p>
        </Panel>
      )}
      {analytics && <DashboardContent {...analytics} />}
    </div>
  );
}

function DashboardContent({ salary, summary }) {
  return (
    <div className="space-y-6">
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Metric label="Jobs" value={summary.job_count} />
        <Metric label="Salary records" value={summary.salary_count} />
        <Metric label="Mean salary" value={money(summary.mean_salary, true)} />
        <Metric
          label="Median salary"
          value={money(summary.median_salary, true)}
        />
      </section>
      <section className="grid gap-6 xl:grid-cols-2">
        <Panel>
          <h2 className="text-lg font-semibold">Salary distribution</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Statistics from the latest analytical snapshot.
          </p>
          <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
            <Stat label="Minimum" value={money(salary.distribution.minimum)} />
            <Stat label="Maximum" value={money(salary.distribution.maximum)} />
            <Stat label="Mean" value={money(salary.distribution.mean, true)} />
            <Stat
              label="Median"
              value={money(salary.distribution.median, true)}
            />
          </div>
        </Panel>
        <Panel>
          <h2 className="text-lg font-semibold">Salary coverage</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Availability of salary information across listings.
          </p>
          <div className="mt-6 space-y-4">
            <Coverage
              label="With minimum salary"
              value={salary.salary_coverage.with_min_salary}
            />
            <Coverage
              label="With maximum salary"
              value={salary.salary_coverage.with_max_salary}
            />
            <Coverage
              label="With midpoint salary"
              value={salary.salary_coverage.with_midpoint_salary}
            />
            <Coverage
              label="Complete salary range"
              value={salary.salary_coverage.with_complete_range}
            />
          </div>
        </Panel>
      </section>
    </div>
  );
}

export function PageIntro({ eyebrow, title, description }) {
  return (
    <header className="mb-8">
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-primary">
        {eyebrow}
      </p>
      <h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">
        {title}
      </h1>
      <p className="mt-3 max-w-2xl text-muted-foreground">{description}</p>
    </header>
  );
}
function Panel({ children }) {
  return (
    <section className="rounded-xl border border-border bg-card p-6 shadow-sm">
      {children}
    </section>
  );
}
function Metric({ label, value }) {
  return (
    <Panel>
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="mt-2 text-2xl font-bold tracking-tight">{value}</p>
    </Panel>
  );
}
function Stat({ label, value }) {
  return (
    <div className="rounded-lg bg-muted p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 font-semibold">{value}</p>
    </div>
  );
}
function Coverage({ label, value }) {
  return (
    <div className="flex items-center justify-between border-b border-border pb-3 last:border-0 last:pb-0">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="font-semibold">{value}</span>
    </div>
  );
}
function money(value, rounded = false) {
  return value == null
    ? '—'
    : `£${(rounded ? Math.round(value) : value).toLocaleString()}`;
}
