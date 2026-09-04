import { useEffect, useState } from 'react';
import { getJob } from '../api';
import ApplicationTracker from '../components/ApplicationTracker';
import JobApplicationActions from '../components/JobApplicationActions';
import Loader from '../components/Loader';

export default function JobDetailPage({ jobId, onBack }) {
  const [job, setJob] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    getJob(jobId)
      .then((data) => {
        if (!cancelled) setJob(data);
      })
      .catch((loadError) => {
        if (!cancelled) setError(loadError.message);
      });
    return () => {
      cancelled = true;
    };
  }, [jobId]);

  if (!job && !error) return <Loader label="Loading job..." />;
  if (error)
    return (
      <>
        <BackButton onBack={onBack} />
        <div className="rounded-xl border border-destructive/30 bg-card p-8">
          <h1 className="text-xl font-semibold">Unable to load this job</h1>
          <p className="mt-2 text-sm text-muted-foreground">{error}</p>
        </div>
      </>
    );

  return (
    <div>
      <BackButton onBack={onBack} />
      <header className="mb-6 overflow-hidden rounded-xl border border-border bg-card shadow-sm">
        <div className="bg-primary px-6 py-8 text-primary-foreground sm:px-8">
          <p className="text-sm opacity-80">
            {job.category_label || 'Technology'} /{' '}
            {job.is_active ? 'Currently active' : 'No longer active'}
          </p>
          <h1 className="mt-3 text-3xl font-bold tracking-tight">
            {job.title}
          </h1>
          <p className="mt-2 text-lg opacity-90">
            {job.company_name || 'Unknown company'}
          </p>
        </div>
        <div className="grid gap-5 px-6 py-6 sm:grid-cols-3 sm:px-8">
          <Detail
            label="Location"
            value={job.location_name || job.city || 'Not specified'}
          />
          <Detail label="Salary" value={formatSalary(job) || 'Not specified'} />
          <Detail
            label="Contract"
            value={
              [format(job.contract_time), format(job.contract_type)]
                .filter(Boolean)
                .join(' · ') || 'Not specified'
            }
          />
        </div>
      </header>
      <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1.6fr)_minmax(300px,0.9fr)]">
        <div className="space-y-6">
          <section className="rounded-xl border border-border bg-card p-6">
            <h2 className="text-xl font-semibold">Role description</h2>
            <div className="mt-5 whitespace-pre-line text-sm leading-7 text-muted-foreground">
              {job.description || 'No description available.'}
            </div>
          </section>
          <section className="rounded-xl border border-border bg-card p-6">
            <h2 className="text-xl font-semibold">Listing details</h2>
            <div className="mt-5 grid gap-5 sm:grid-cols-2">
              <Detail label="First seen" value={date(job.first_seen_at)} />
              <Detail label="Last seen" value={date(job.last_seen_at)} />
              <Detail label="Adzuna ID" value={job.id} />
            </div>
          </section>
        </div>
        <aside className="space-y-6 lg:sticky lg:top-6">
          <section className="rounded-xl border border-border bg-card p-6">
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
              Your application
            </p>
            <h2 className="mt-2 text-xl font-semibold">Take the next step</h2>
            <div className="mt-5">
              <JobApplicationActions
                job={job}
                onUpdated={(updated) =>
                  setJob((current) => ({ ...current, ...updated }))
                }
              />
            </div>
          </section>
          <ApplicationTracker job={job} onUpdated={() => undefined} />
        </aside>
      </div>
    </div>
  );
}

function BackButton({ onBack }) {
  return (
    <button
      type="button"
      onClick={onBack}
      className="mb-6 inline-flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground"
    >
      <span aria-hidden="true">←</span> Back to job explorer
    </button>
  );
}

function Detail({ label, value }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-sm font-medium">{value}</p>
    </div>
  );
}

function format(value) {
  return value
    ? value
        .replaceAll('_', ' ')
        .replace(/\b\w/g, (letter) => letter.toUpperCase())
    : '';
}

function formatSalary(job) {
  if (job.salary_min != null && job.salary_max != null)
    return `£${Number(job.salary_min).toLocaleString()} – £${Number(job.salary_max).toLocaleString()}`;
  if (job.salary_min != null)
    return `From £${Number(job.salary_min).toLocaleString()}`;
  if (job.salary_max != null)
    return `Up to £${Number(job.salary_max).toLocaleString()}`;
  return null;
}
function date(value) {
  return value ? new Date(value).toLocaleString() : 'Not available';
}
