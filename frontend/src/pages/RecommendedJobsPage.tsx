import { useEffect, useState } from 'react';
import { getPrioritizedJobs } from '../api';
import Loader from '../components/Loader';
import PageIntro from '../components/PageIntro';
import Panel from '../components/Panel';

const PROFILE_FIELDS = [
  ['target_titles', 'Target roles', 'e.g. Data Analyst, Python Developer'],
  ['preferred_locations', 'Preferred locations', 'e.g. London, Manchester'],
  ['preferred_categories', 'Preferred categories', 'e.g. IT jobs, Software'],
  ['preferred_contract_types', 'Contract types', 'e.g. permanent, contract'],
];

function readProfile() {
  try {
    return JSON.parse(localStorage.getItem('job-profile') || '{}');
  } catch {
    return {};
  }
}

function money(value) {
  return value == null
    ? 'Salary not listed'
    : `£${Number(value).toLocaleString()}`;
}

function format(value) {
  return value
    ? value
        .replaceAll('_', ' ')
        .replace(/\b\w/g, (letter) => letter.toUpperCase())
    : 'Not specified';
}

function priorityClass(priority) {
  return priority === 'HIGH'
    ? 'bg-green-500/10 text-green-700 dark:text-green-300'
    : priority === 'MEDIUM'
      ? 'bg-amber-500/10 text-amber-700 dark:text-amber-300'
      : 'bg-muted text-muted-foreground';
}

export default function RecommendedJobsPage({ onOpenJob }) {
  const [profile, setProfile] = useState(readProfile);
  const [jobs, setJobs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function loadRecommendations() {
      setLoading(true);
      setError(null);
      try {
        const response = await getPrioritizedJobs(profile);
        if (cancelled) return;
        setJobs(response.jobs || []);
        setTotal(response.total || 0);
      } catch (loadError) {
        if (!cancelled) setError(loadError.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    loadRecommendations();
    return () => {
      cancelled = true;
    };
  }, [profile]);

  function updateProfile(name, value) {
    setProfile((current) => ({ ...current, [name]: value }));
  }

  function saveProfile(event) {
    event.preventDefault();
    localStorage.setItem('job-profile', JSON.stringify(profile));
    setProfile({ ...profile });
  }

  return (
    <div>
      <PageIntro
        eyebrow="Personalised discovery"
        title="Recommended jobs"
        description="Rank active listings against your role, location, category, and contract preferences."
      />
      <Panel>
        <form onSubmit={saveProfile}>
          <div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-lg font-semibold">Your job profile</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Use comma-separated values for multiple preferences.
              </p>
            </div>
            <button
              type="submit"
              className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90"
            >
              Save profile
            </button>
          </div>
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            {PROFILE_FIELDS.map(([name, label, placeholder]) => (
              <label key={name} className="text-sm font-medium">
                {label}
                <input
                  value={profile[name] || ''}
                  onChange={(event) => updateProfile(name, event.target.value)}
                  placeholder={placeholder}
                  className="mt-2 w-full rounded-lg border border-border bg-background px-3 py-2.5 font-normal outline-none focus:border-primary"
                />
              </label>
            ))}
          </div>
        </form>
      </Panel>

      <div className="mt-6 flex items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold">Top matches</h2>
          <p className="text-sm text-muted-foreground">
            {total} active listings scored
          </p>
        </div>
      </div>
      {loading && (
        <Panel>
          <Loader label="Scoring active jobs..." />
        </Panel>
      )}
      {error && (
        <Panel>
          <p className="text-sm text-destructive">{error}</p>
        </Panel>
      )}
      {!loading && !error && jobs.length === 0 && (
        <Panel>
          <p className="text-sm text-muted-foreground">
            No active jobs are available to score.
          </p>
        </Panel>
      )}
      <div className="mt-4 grid gap-4 xl:grid-cols-2">
        {!loading &&
          jobs.map((job) => (
            <article
              key={job.id}
              className="rounded-xl border border-border bg-card p-5 shadow-sm"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
                    Rank #{job.rank}
                  </p>
                  <h3 className="mt-2 text-lg font-semibold">{job.title}</h3>
                  <p className="mt-1 text-sm text-muted-foreground">
                    {job.company_name || 'Unknown company'} ·{' '}
                    {job.location_name || 'Location not specified'}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-primary">
                    {Math.round(job.priority_score)}
                  </p>
                  <span
                    className={`mt-1 inline-block rounded-full px-2.5 py-1 text-xs font-medium ${priorityClass(job.priority)}`}
                  >
                    {job.priority}
                  </span>
                </div>
              </div>
              <div className="mt-5 grid grid-cols-2 gap-3 text-sm sm:grid-cols-3">
                <Metric label="Salary" value={money(job.salary)} />
                <Metric
                  label="Category"
                  value={job.category_label || 'Not specified'}
                />
                <Metric label="Contract" value={format(job.contract_type)} />
              </div>
              <div className="mt-5 rounded-lg bg-muted/60 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">
                  Why it ranks here
                </p>
                <ul className="mt-2 space-y-1 text-sm text-muted-foreground">
                  {(job.explanation || []).slice(0, 3).map((reason) => (
                    <li key={reason}>· {reason}</li>
                  ))}
                </ul>
              </div>
              <div className="mt-5 flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => onOpenJob(job)}
                  className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90"
                >
                  View job
                </button>
                {job.redirect_url && (
                  <a
                    href={job.redirect_url}
                    target="_blank"
                    rel="noreferrer"
                    className="rounded-lg border border-border px-4 py-2 text-sm font-medium hover:bg-muted"
                  >
                    Open listing
                  </a>
                )}
              </div>
            </article>
          ))}
      </div>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 truncate font-medium">{value}</p>
    </div>
  );
}
