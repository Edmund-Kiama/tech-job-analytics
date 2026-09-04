import { useEffect, useState } from 'react';
import { getApplications } from '../api';

const STATUSES = [
  'ALL',
  'SAVED',
  'APPLIED',
  'INTERVIEW',
  'OFFER',
  'REJECTED',
  'ARCHIVED',
];

const PRIORITIES = [
  { value: '', label: 'All priorities' },
  { value: '3', label: 'High' },
  { value: '2', label: 'Medium' },
  { value: '1', label: 'Low' },
];

function formatDate(value) {
  if (!value) {
    return '—';
  }

  return new Date(value).toLocaleDateString();
}

function statusClass(status) {
  const classes = {
    SAVED: 'bg-blue-500/10 text-blue-700 dark:text-blue-300',
    APPLIED: 'bg-purple-500/10 text-purple-700 dark:text-purple-300',
    INTERVIEW: 'bg-amber-500/10 text-amber-700 dark:text-amber-300',
    OFFER: 'bg-green-500/10 text-green-700 dark:text-green-300',
    REJECTED: 'bg-red-500/10 text-red-700 dark:text-red-300',
    ARCHIVED: 'bg-muted text-muted-foreground',
  };

  return classes[status] || 'bg-muted text-muted-foreground';
}

function priorityLabel(priority) {
  if (priority === 3) {
    return 'High';
  }

  if (priority === 2) {
    return 'Medium';
  }

  if (priority === 1) {
    return 'Low';
  }

  return '—';
}

export default function ApplicationsPage() {
  const [applications, setApplications] = useState([]);
  const [status, setStatus] = useState('ALL');
  const [priority, setPriority] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadApplications() {
      try {
        setLoading(true);
        setError(null);

        const data = await getApplications(
          status === 'ALL' ? null : status,
          priority ? Number(priority) : null
        );

        setApplications(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadApplications();
  }, [status, priority]);

  return (
    <section className="">
      <div className="mb-6">
        <p className="text-sm font-medium text-primary">APPLICATION TRACKER</p>

        <h2 className="mt-1 text-2xl font-semibold">My Applications</h2>

        <p className="mt-2 text-sm text-muted-foreground">
          Track saved jobs, applications, interviews, offers and rejected
          applications.
        </p>
      </div>

      <div className="mb-6 flex flex-col gap-3 sm:flex-row">
        <select
          value={status}
          onChange={(event) => setStatus(event.target.value)}
          className="rounded-lg border bg-background px-3 py-2 text-sm"
        >
          {STATUSES.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>

        <select
          value={priority}
          onChange={(event) => setPriority(event.target.value)}
          className="rounded-lg border bg-background px-3 py-2 text-sm"
        >
          {PRIORITIES.map((item) => (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          ))}
        </select>
      </div>

      {loading && (
        <div className="rounded-xl border bg-card p-6">
          Loading applications...
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-destructive/30 bg-destructive/5 p-6 text-sm text-destructive">
          {error}
        </div>
      )}

      {!loading && !error && applications.length === 0 && (
        <div className="rounded-xl border bg-card p-8 text-center">
          <h3 className="font-semibold">No applications found</h3>

          <p className="mt-2 text-sm text-muted-foreground">
            Save a job or mark one as applied to start tracking it.
          </p>
        </div>
      )}

      <div className="space-y-4">
        {applications.map((job) => (
          <article key={job.id} className="rounded-xl border bg-card p-5">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <h3 className="text-lg font-semibold">{job.title}</h3>

                <p className="mt-1 text-sm text-muted-foreground">
                  {job.company_name || 'Unknown company'}
                </p>

                <p className="mt-1 text-sm text-muted-foreground">
                  {job.location_name || 'Location not specified'}
                </p>
              </div>

              <div className="flex flex-wrap gap-2">
                <span
                  className={`rounded-full px-3 py-1 text-xs font-medium ${statusClass(
                    job.application_status
                  )}`}
                >
                  {job.application_status}
                </span>

                {job.user_priority && (
                  <span className="rounded-full bg-muted px-3 py-1 text-xs font-medium">
                    {priorityLabel(job.user_priority)}
                  </span>
                )}
              </div>
            </div>

            <div className="mt-5 grid gap-3 text-sm sm:grid-cols-3">
              <div>
                <span className="text-muted-foreground">Saved</span>

                <p className="font-medium">{formatDate(job.saved_at)}</p>
              </div>

              <div>
                <span className="text-muted-foreground">Applied</span>

                <p className="font-medium">{formatDate(job.applied_at)}</p>
              </div>

              <div>
                <span className="text-muted-foreground">Follow-up</span>

                <p className="font-medium">{formatDate(job.follow_up_at)}</p>
              </div>
            </div>

            {job.application_notes && (
              <div className="mt-4 rounded-lg bg-muted/50 p-3">
                <p className="text-xs font-medium text-muted-foreground">
                  Notes
                </p>

                <p className="mt-1 text-sm">{job.application_notes}</p>
              </div>
            )}

            {job.redirect_url && (
              <div className="mt-4">
                <a
                  href={job.redirect_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-sm font-medium text-primary hover:underline"
                >
                  Open application →
                </a>
              </div>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}
