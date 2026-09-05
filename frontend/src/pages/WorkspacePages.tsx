import { useEffect, useState } from 'react';
import {
  getAnalyticsBreakdown,
  getHealth,
  getIngestionRuns,
  getIngestionStatus,
  getApplications,
} from '../api';
import Loader from '../components/Loader';
import PageIntro from '../components/PageIntro';
import Panel from '../components/Panel';

function money(value) {
  return value == null ? 'Not available' : `£${Number(value).toLocaleString()}`;
}

function date(value) {
  return value ? new Date(value).toLocaleString() : 'Not available';
}

export function CompaniesPage() {
  const [companies, setCompanies] = useState([]);
  const [error, setError] = useState(null);
  useEffect(() => {
    getAnalyticsBreakdown()
      .then((data) => setCompanies(data.top_companies || []))
      .catch((loadError) => setError(loadError.message));
  }, []);
  return (
    <div>
      <PageIntro
        eyebrow="Employer landscape"
        title="Companies"
        description="See which employers have the strongest presence in the current job dataset."
      />
      {error && (
        <Panel>
          <p className="text-sm text-destructive">{error}</p>
        </Panel>
      )}{' '}
      {!error && !companies.length && (
        <Panel>
          <Loader label="Loading companies..." />
        </Panel>
      )}{' '}
      {companies.length > 0 && (
        <div className="space-y-6">
          <section className="grid gap-4 sm:grid-cols-3">
            <CompanyMetric
              label="Employers represented"
              value={companies.length}
            />
            <CompanyMetric
              label="Most active employer"
              value={companies[0]?.job_count ?? companies[0]?.count ?? '—'}
              detail={companies[0]?.company || companies[0]?.company_name}
            />
            <CompanyMetric
              label="Highest mean salary"
              value={money(
                companies.reduce(
                  (highest, company) =>
                    Math.max(highest, Number(company.mean_salary) || 0),
                  0
                )
              )}
            />
          </section>
          <Panel>
            <p className="mb-4 text-sm text-muted-foreground">
              Compare employer presence and compensation at a glance. Salary
              spread shows how far the typical mean sits above or below the
              median.
            </p>
            <div className="overflow-x-auto">
              <table className="w-full min-w-155 text-left text-sm">
                <thead className="border-b border-border">
                  <tr>
                    <th className="px-3 py-3 font-medium text-muted-foreground">
                      Company
                    </th>
                    <th className="px-3 py-3 text-right font-medium text-muted-foreground">
                      Jobs
                    </th>
                    <th className="px-3 py-3 text-right font-medium text-muted-foreground">
                      Mean salary
                    </th>
                    <th className="px-3 py-3 text-right font-medium text-muted-foreground">
                      Median salary
                    </th>
                    <th className="px-3 py-3 text-right font-medium text-muted-foreground">
                      Mean vs median
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {companies.map((company, index) => (
                    <tr key={company.company || index}>
                      <td className="px-3 py-4 font-medium">
                        {company.company ||
                          company.company_name ||
                          'Unknown company'}
                      </td>
                      <td className="px-3 py-4 text-right">
                        {company.job_count ?? company.count ?? '—'}
                      </td>
                      <td className="px-3 py-4 text-right">
                        {money(company.mean_salary)}
                      </td>
                      <td className="px-3 py-4 text-right">
                        {money(company.median_salary)}
                      </td>
                      <td className="px-3 py-4 text-right">
                        {salarySpread(company) || '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>
        </div>
      )}
    </div>
  );
}

function CompanyMetric({ label, value, detail = null }) {
  return (
    <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="mt-2 text-2xl font-bold">{value}</p>
      {detail && (
        <p className="mt-1 truncate text-xs text-muted-foreground">{detail}</p>
      )}
    </div>
  );
}

function salarySpread(company) {
  if (company.mean_salary == null || company.median_salary == null) {
    return null;
  }
  const spread = Number(company.mean_salary) - Number(company.median_salary);
  return `${spread >= 0 ? '+' : ''}£${Math.round(spread).toLocaleString()}`;
}

export function FollowUpsPage({ reminderWindow }) {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  useEffect(() => {
    getApplications()
      .then(setApplications)
      .catch((loadError) => setError(loadError.message))
      .finally(() => setLoading(false));
  }, []);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const reminderEnd = new Date(today);
  reminderEnd.setDate(today.getDate() + Number(reminderWindow || 3));
  const followUps = applications
    .filter((job) => job.follow_up_at)
    .filter((job) => {
      const followUpDate = new Date(job.follow_up_at);
      return followUpDate < today || followUpDate <= reminderEnd;
    })
    .sort(
      (a, b) =>
        new Date(a.follow_up_at).getTime() - new Date(b.follow_up_at).getTime()
    );
  return (
    <div>
      <PageIntro
        eyebrow="Application momentum"
        title="Follow-ups"
        description="Keep upcoming and overdue application actions visible."
      />
      {loading && (
        <Panel>
          <Loader label="Loading follow-ups..." />
        </Panel>
      )}
      {error && (
        <Panel>
          <p className="text-sm text-destructive">{error}</p>
        </Panel>
      )}
      {!loading && !error && !followUps.length && (
        <Panel>
          <p className="text-sm text-muted-foreground">
            No follow-up dates are currently set.
          </p>
        </Panel>
      )}{' '}
      {!loading && !error && (
        <div className="space-y-3">
          {followUps.map((job) => {
            const followUp = new Date(job.follow_up_at);
            const overdue = followUp < today;
            return (
              <article
                key={job.id}
                className="rounded-xl border border-border bg-card p-5 shadow-sm"
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h2 className="font-semibold">{job.title}</h2>
                    <p className="mt-1 text-sm text-muted-foreground">
                      {job.company_name || 'Unknown company'} ·{' '}
                      {job.application_status}
                    </p>
                  </div>
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-medium ${overdue ? 'bg-red-500/10 text-red-700 dark:text-red-300' : 'bg-green-500/10 text-green-700 dark:text-green-300'}`}
                  >
                    {overdue ? 'Overdue' : 'Upcoming'}
                  </span>
                </div>
                <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-sm">
                  <span>
                    <span className="text-muted-foreground">Follow-up</span>
                    <br />
                    <strong>{date(job.follow_up_at)}</strong>
                  </span>
                  <span>
                    <span className="text-muted-foreground">Priority</span>
                    <br />
                    <strong>
                      {job.user_priority
                        ? ['Low', 'Medium', 'High'][job.user_priority - 1]
                        : 'Not set'}
                    </strong>
                  </span>
                  {job.application_notes && (
                    <span className="max-w-xl">
                      <span className="text-muted-foreground">Notes</span>
                      <br />
                      <strong className="font-medium">
                        {job.application_notes}
                      </strong>
                    </span>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}

export function DataHealthPage() {
  const [status, setStatus] = useState(null);
  const [health, setHealth] = useState(null);
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  useEffect(() => {
    Promise.all([getHealth(), getIngestionStatus(), getIngestionRuns()])
      .then(([healthData, statusData, runsData]) => {
        setHealth(healthData);
        setStatus(statusData);
        setRuns(runsData.runs || []);
      })
      .catch((loadError) => setError(loadError.message))
      .finally(() => setLoading(false));
  }, []);
  return (
    <div>
      <PageIntro
        eyebrow="Pipeline observability"
        title="Data health"
        description="Check whether the data behind your analytics is current, complete, and processing cleanly."
      />
      {loading && (
        <Panel>
          <Loader label="Checking data health..." />
        </Panel>
      )}
      {error && (
        <Panel>
          <p className="text-sm text-destructive">{error}</p>
        </Panel>
      )}
      {!loading && !error && (
        <div className="space-y-6">
          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <Metric
              label="Database"
              value={health?.database || health?.status || 'Unknown'}
            />
            <Metric label="Listings" value={health?.listings ?? '—'} />
            <Metric label="Active jobs" value={status?.jobs?.active ?? '—'} />
            <Metric
              label="Last ingestion"
              value={date(health?.latest_ingestion || status?.last_run)}
            />
          </section>
          <Panel>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold">Latest ingestion</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  Status: {status?.status || 'Unknown'} · completed{' '}
                  {date(status?.completed_at)}
                </p>
              </div>
              {status?.error_message && (
                <span className="rounded-full bg-red-500/10 px-3 py-1 text-xs font-medium text-red-700 dark:text-red-300">
                  Pipeline error
                </span>
              )}
            </div>
            {status?.error_message && (
              <p className="mt-4 rounded-lg bg-red-500/5 p-4 text-sm text-destructive">
                {status.error_message}
              </p>
            )}
            <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <Metric
                label="Rows fetched"
                value={status?.rows_fetched ?? '—'}
              />
              <Metric label="Inserted" value={status?.jobs_inserted ?? '—'} />
              <Metric label="Updated" value={status?.jobs_updated ?? '—'} />
              <Metric
                label="Inactivated"
                value={status?.jobs_inactivated ?? '—'}
              />
            </div>
          </Panel>
          <Panel>
            <h2 className="text-lg font-semibold">Ingestion history</h2>
            <div className="mt-5 overflow-x-auto">
              <table className="w-full min-w-170 text-left text-sm">
                <thead className="border-b border-border">
                  <tr>
                    <th className="px-3 py-3 font-medium text-muted-foreground">
                      Started
                    </th>
                    <th className="px-3 py-3 font-medium text-muted-foreground">
                      Status
                    </th>
                    <th className="px-3 py-3 text-right font-medium text-muted-foreground">
                      Fetched
                    </th>
                    <th className="px-3 py-3 text-right font-medium text-muted-foreground">
                      Inserted
                    </th>
                    <th className="px-3 py-3 text-right font-medium text-muted-foreground">
                      Updated
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {runs.map((run) => (
                    <tr key={run.id}>
                      <td className="px-3 py-4">{date(run.started_at)}</td>
                      <td className="px-3 py-4 font-medium">{run.status}</td>
                      <td className="px-3 py-4 text-right">
                        {run.rows_fetched ?? '—'}
                      </td>
                      <td className="px-3 py-4 text-right">
                        {run.jobs_inserted ?? '—'}
                      </td>
                      <td className="px-3 py-4 text-right">
                        {run.jobs_updated ?? '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>
        </div>
      )}
    </div>
  );
}

export function SettingsPage({
  settings,
  updateSettings,
  profile,
  onProfileSave,
}) {
  const [profileDraft, setProfileDraft] = useState(profile);
  const [profileSaved, setProfileSaved] = useState(false);
  const fields: Array<[string, string, string[]]> = [
    ['defaultPageSize', 'Default jobs per page', ['10', '25', '50', '100']],
    [
      'defaultSort',
      'Default job sort',
      ['created_desc', 'salary_desc', 'title_asc', 'company_asc'],
    ],
  ];

  const profileFields = [
    ['target_titles', 'Target roles', 'e.g. Data Analyst, Python Developer'],
    ['preferred_locations', 'Preferred locations', 'e.g. London, Manchester'],
    ['preferred_categories', 'Preferred categories', 'e.g. IT jobs, Software'],
    ['preferred_contract_types', 'Contract types', 'e.g. permanent, contract'],
  ];

  function saveProfile(event) {
    event.preventDefault();
    onProfileSave({ ...profileDraft });
    setProfileSaved(true);
  }
  return (
    <div>
      <PageIntro
        eyebrow="Workspace preferences"
        title="Settings"
        description="Tune the workspace for the way you search, compare, and follow up on jobs."
      />
      <div className="space-y-6">
        <Panel>
          <form onSubmit={saveProfile}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold">Job profile</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  These preferences power Recommended Jobs and job match scores.
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
              {profileFields.map(([name, label, placeholder]) => (
                <label key={name} className="text-sm font-medium">
                  {label}
                  <input
                    value={profileDraft[name] || ''}
                    onChange={(event) => {
                      setProfileSaved(false);
                      setProfileDraft((current) => ({
                        ...current,
                        [name]: event.target.value,
                      }));
                    }}
                    placeholder={placeholder}
                    className="mt-2 w-full rounded-lg border border-border bg-background px-3 py-2.5 font-normal outline-none focus:border-primary"
                  />
                </label>
              ))}
            </div>
            {profileSaved && (
              <p className="mt-3 text-sm text-emerald-600 dark:text-emerald-400">
                Job profile saved and synced with Recommended Jobs.
              </p>
            )}
          </form>
        </Panel>
        <Panel>
          <h2 className="text-lg font-semibold">Job explorer defaults</h2>
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            {fields.map(([name, label, options]) => (
              <label key={name} className="text-sm font-medium">
                {label}
                <select
                  value={settings[name]}
                  onChange={(event) => updateSettings(name, event.target.value)}
                  className="mt-2 w-full rounded-lg border border-border bg-background px-3 py-2.5"
                >
                  <option value="">Choose</option>
                  {options.map((option) => (
                    <option key={option} value={option}>
                      {option.replace('_', ' ')}
                    </option>
                  ))}
                </select>
              </label>
            ))}
          </div>
        </Panel>
        <Panel>
          <h2 className="text-lg font-semibold">Salary and listing display</h2>
          <div className="mt-5 space-y-4">
            <label className="flex items-center justify-between gap-4 text-sm">
              <span>
                <strong className="block">Show predicted salaries</strong>
                <span className="text-muted-foreground">
                  Keep source-estimated salaries visible in job results.
                </span>
              </span>
              <input
                type="checkbox"
                checked={settings.showPredicted}
                onChange={(event) =>
                  updateSettings('showPredicted', event.target.checked)
                }
                className="h-4 w-4 accent-primary"
              />
            </label>
            <label className="flex items-center justify-between gap-4 text-sm">
              <span>
                <strong className="block">
                  Refresh data on dashboard load
                </strong>
                <span className="text-muted-foreground">
                  Use the latest API response whenever the dashboard opens.
                </span>
              </span>
              <input
                type="checkbox"
                checked={settings.refreshOnLoad}
                onChange={(event) =>
                  updateSettings('refreshOnLoad', event.target.checked)
                }
                className="h-4 w-4 accent-primary"
              />
            </label>
          </div>
        </Panel>
        <Panel>
          <h2 className="text-lg font-semibold">Follow-up reminders</h2>
          <label className="mt-5  block text-sm font-medium">
            Reminder window
            <select
              value={settings.reminderWindow}
              onChange={(event) =>
                updateSettings('reminderWindow', event.target.value)
              }
              className="mt-2 ml-2 w-full rounded-lg border border-border bg-background px-3 py-2.5 sm:max-w-sm"
            >
              <option value="0">Due today</option>
              <option value="3">Next 3 days</option>
              <option value="7">Next 7 days</option>
            </select>
          </label>
        </Panel>
      </div>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-lg bg-muted p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 truncate font-semibold">{value}</p>
    </div>
  );
}
