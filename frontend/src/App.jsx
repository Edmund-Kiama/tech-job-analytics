import { useEffect, useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

function useTheme() {
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem('theme');

    return savedTheme === 'light' ||
      savedTheme === 'dark' ||
      savedTheme === 'system'
      ? savedTheme
      : 'system';
  });

  useEffect(() => {
    const root = document.documentElement;

    function updateTheme() {
      const isDark =
        theme === 'dark' ||
        (theme === 'system' &&
          window.matchMedia('(prefers-color-scheme: dark)').matches);

      root.classList.toggle('dark', isDark);
      root.classList.toggle('light', !isDark);
    }

    updateTheme();

    localStorage.setItem('theme', theme);

    if (theme !== 'system') {
      return;
    }

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleSystemThemeChange = () => {
      updateTheme();
    };

    mediaQuery.addEventListener('change', handleSystemThemeChange);

    return () => {
      mediaQuery.removeEventListener('change', handleSystemThemeChange);
    };
  }, [theme]);

  return [theme, setTheme];
}

function App() {
  const [theme, setTheme] = useTheme();
  const [jobs, setJobs] = useState([]);
  const [salary, setSalary] = useState(null);
  const [summary, setSummary] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchAnalytics() {
      try {
        setLoading(true);
        setError(null);

        const [jobsResponse, salaryResponse, summaryResponse] =
          await Promise.all([
            fetch(`${API_BASE_URL}/jobs`),
            fetch(`${API_BASE_URL}/analytics/salary`),
            fetch(`${API_BASE_URL}/analytics/summary`),
          ]);

        if (!jobsResponse.ok) {
          throw new Error(`Jobs API error: ${jobsResponse.status}`);
        }

        if (!salaryResponse.ok) {
          throw new Error(`Salary API error: ${salaryResponse.status}`);
        }

        if (!summaryResponse.ok) {
          throw new Error(`Summary API error: ${summaryResponse.status}`);
        }

        const [jobsData, salaryData, summaryData] = await Promise.all([
          jobsResponse.json(),
          salaryResponse.json(),
          summaryResponse.json(),
        ]);

        setJobs(jobsData);
        setSalary(salaryData);
        setSummary(summaryData);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    }

    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background text-foreground">
        <div className="text-center">
          <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-4 border-primary/20 border-t-primary" />

          <p className="text-sm text-muted-foreground">Loading analytics...</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background px-6 text-foreground">
        <div className="w-full max-w-md rounded-xl border border-destructive/30 bg-card p-6 text-center shadow-sm">
          <h1 className="mb-2 text-xl font-semibold">
            Unable to load analytics
          </h1>

          <p className="text-sm text-muted-foreground">{error}</p>
        </div>
      </main>
    );
  }

  if (!jobs.length && !salary && !summary) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background px-6 text-foreground">
        <div className="text-center">
          <h1 className="text-xl font-semibold">No analytics available</h1>

          <p className="mt-2 text-sm text-muted-foreground">
            The API returned no analytics data.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="mx-auto max-w-7xl px-6 py-8 lg:px-8">
        <header className="mb-8">
          <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="mb-2 text-sm font-medium text-primary">
                TECH JOB ANALYTICS
              </p>

              <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
                Job Market Dashboard
              </h1>

              <p className="mt-2 max-w-2xl text-muted-foreground">
                Salary and job-market analytics derived from the latest Adzuna
                dataset.
              </p>
            </div>

            <ThemeSwitcher theme={theme} setTheme={setTheme} />
          </div>
        </header>

        {summary && (
          <section className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard label="Jobs" value={summary.job_count} />

            <MetricCard label="Salary Records" value={summary.salary_count} />

            <MetricCard
              label="Mean Salary"
              value={`£${Math.round(summary.mean_salary).toLocaleString()}`}
            />

            <MetricCard
              label="Median Salary"
              value={`£${Math.round(summary.median_salary).toLocaleString()}`}
            />
          </section>
        )}

        {salary && (
          <section className="mb-8 grid gap-6 lg:grid-cols-2">
            <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
              <h2 className="text-lg font-semibold">Salary Distribution</h2>

              <p className="mt-1 text-sm text-muted-foreground">
                Distribution statistics from the latest analytical snapshot.
              </p>

              <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
                <Stat
                  label="Minimum"
                  value={`£${salary.distribution.minimum.toLocaleString()}`}
                />

                <Stat
                  label="Maximum"
                  value={`£${salary.distribution.maximum.toLocaleString()}`}
                />

                <Stat
                  label="Mean"
                  value={`£${Math.round(
                    salary.distribution.mean
                  ).toLocaleString()}`}
                />

                <Stat
                  label="Median"
                  value={`£${salary.distribution.median.toLocaleString()}`}
                />
              </div>
            </div>

            <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
              <h2 className="text-lg font-semibold">Salary Coverage</h2>

              <p className="mt-1 text-sm text-muted-foreground">
                Availability of salary information across job listings.
              </p>

              <div className="mt-6 space-y-4">
                <CoverageRow
                  label="With minimum salary"
                  value={salary.salary_coverage.with_min_salary}
                />

                <CoverageRow
                  label="With maximum salary"
                  value={salary.salary_coverage.with_max_salary}
                />

                <CoverageRow
                  label="With midpoint salary"
                  value={salary.salary_coverage.with_midpoint_salary}
                />

                <CoverageRow
                  label="Complete salary range"
                  value={salary.salary_coverage.with_complete_range}
                />
              </div>
            </div>
          </section>
        )}

        <section>
          <div className="mb-4">
            <h2 className="text-xl font-semibold">Job Listings</h2>

            <p className="text-sm text-muted-foreground">
              {jobs.length} jobs currently stored in the analytics database.
            </p>
          </div>

          {!jobs.length ? (
            <div className="rounded-xl border border-border bg-card p-8 text-center">
              <p className="text-sm text-muted-foreground">
                No job listings are available.
              </p>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {jobs.map((job) => (
                <article
                  key={job.id}
                  className="rounded-xl border border-border bg-card p-5 shadow-sm transition hover:border-primary/40 hover:shadow-md"
                >
                  <div className="mb-4">
                    <h3 className="font-semibold text-card-foreground">
                      {job.title}
                    </h3>

                    <p className="mt-1 text-sm text-muted-foreground">
                      {job.company_name || 'Unknown company'}
                    </p>
                  </div>

                  <div className="mb-4 flex flex-wrap gap-2">
                    {job.location_name && (
                      <span className="rounded-full bg-muted px-3 py-1 text-xs text-muted-foreground">
                        {job.location_name}
                      </span>
                    )}

                    {job.contract_time && (
                      <span className="rounded-full bg-accent px-3 py-1 text-xs text-accent-foreground">
                        {job.contract_time}
                      </span>
                    )}
                  </div>

                  <p className="line-clamp-3 text-sm leading-6 text-muted-foreground">
                    {job.description || 'No description available.'}
                  </p>

                  <div className="mt-5 border-t border-border pt-4">
                    <p className="text-sm font-medium">
                      {job.salary_min || job.salary_max
                        ? `£${(
                            job.salary_min || job.salary_max
                          ).toLocaleString()}${
                            job.salary_min && job.salary_max
                              ? ` – £${job.salary_max.toLocaleString()}`
                              : ''
                          }`
                        : 'Salary not specified'}
                    </p>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  );
}

function ThemeSwitcher({ theme, setTheme }) {
  return (
    <div className="flex items-center rounded-lg border border-border bg-card p-1 shadow-sm">
      <ThemeButton
        value="light"
        label="Light"
        active={theme === 'light'}
        onClick={() => setTheme('light')}
      />

      <ThemeButton
        value="dark"
        label="Dark"
        active={theme === 'dark'}
        onClick={() => setTheme('dark')}
      />

      <ThemeButton
        value="system"
        label="System"
        active={theme === 'system'}
        onClick={() => setTheme('system')}
      />
    </div>
  );
}

function ThemeButton({ value, label, active, onClick }) {
  console.log(value);
  return (
    <button
      type="button"
      aria-pressed={active}
      onClick={onClick}
      className={[
        'rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
        'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring',
        active
          ? 'bg-primary text-primary-foreground'
          : 'text-muted-foreground hover:bg-muted hover:text-foreground',
      ].join(' ')}
    >
      {label}
    </button>
  );
}

function MetricCard({ label, value }) {
  return (
    <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
      <p className="text-sm text-muted-foreground">{label}</p>

      <p className="mt-2 text-2xl font-bold tracking-tight">{value}</p>
    </div>
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

function CoverageRow({ label, value }) {
  return (
    <div className="flex items-center justify-between border-b border-border pb-3 last:border-0 last:pb-0">
      <span className="text-sm text-muted-foreground">{label}</span>

      <span className="font-semibold">{value}</span>
    </div>
  );
}

export default App;
