import { useEffect, useState } from 'react';
import { getJobs, getSalaryAnalytics, getAnalyticsSummary } from './api';
import ApplicationsPage from './components/ApplicationsPage';
import ApplicationTracker from './components/ApplicationTracker';
import JobApplicationActions from './components/JobApplicationActions';

const DEFAULT_PAGE_SIZE = parseInt(import.meta.env.VITE_DEFAULT_PAGE_SIZE, 10);

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

function getInitialFilters() {
  const params = new URLSearchParams(window.location.search);

  return {
    search: params.get('search') || '',
    category: params.get('category') || '',
    location: params.get('location') || '',
    contract_time: params.get('contract_time') || '',
    contract_type: params.get('contract_type') || '',
    min_salary: params.get('min_salary') || '',
    max_salary: params.get('max_salary') || '',
    salary_predicted: params.get('salary_predicted') || '',
    sort: params.get('sort') || 'created_desc',
    page: Number(params.get('page')) || 1,
    page_size: Number(params.get('page_size')) || DEFAULT_PAGE_SIZE,
  };
}

function updateUrl(filters) {
  const params = new URLSearchParams();

  const keys = [
    'search',
    'category',
    'location',
    'contract_time',
    'contract_type',
    'min_salary',
    'max_salary',
    'salary_predicted',
    'sort',
  ];

  keys.forEach((key) => {
    if (filters[key] !== '' && filters[key] != null) {
      params.set(key, filters[key]);
    }
  });

  if (filters.page > 1) {
    params.set('page', filters.page);
  }

  if (filters.page_size !== DEFAULT_PAGE_SIZE) {
    params.set('page_size', filters.page_size);
  }

  const query = params.toString();

  window.history.replaceState(
    {},
    '',
    query ? `${window.location.pathname}?${query}` : window.location.pathname
  );
}

function App() {
  const [theme, setTheme] = useTheme();

  const [filters, setFilters] = useState(getInitialFilters);

  const [jobs, setJobs] = useState([]);
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: DEFAULT_PAGE_SIZE,
    total: 0,
    total_pages: 1,
  });

  const [salary, setSalary] = useState(null);
  const [summary, setSummary] = useState(null);

  const [loadingJobs, setLoadingJobs] = useState(true);
  const [loadingAnalytics, setLoadingAnalytics] = useState(true);

  const [jobsError, setJobsError] = useState(null);
  const [analyticsError, setAnalyticsError] = useState(null);

  const [selectedJob, setSelectedJob] = useState(null);

  /*
   * Keep the URL synchronized with the current explorer state.
   */
  useEffect(() => {
    updateUrl(filters);
  }, [filters]);

  /*
   * Load jobs whenever search/filter/sort/page state changes.
   */
  useEffect(() => {
    let cancelled = false;

    async function loadJobs() {
      try {
        setLoadingJobs(true);
        setJobsError(null);

        const response = await getJobs(filters);

        if (cancelled) {
          return;
        }

        /*
         * Backend returns:
         * {
         *   items,
         *   total,
         *   page,
         *   page_size,
         *   total_pages
         * }
         */

        setJobs(response.items || []);

        setPagination({
          page: response.page || filters.page,
          page_size: response.page_size || filters.page_size,
          total: response.total || 0,
          total_pages: response.total_pages || 1,
        });
      } catch (error) {
        if (!cancelled) {
          setJobsError(error.message);
        }
      } finally {
        if (!cancelled) {
          setLoadingJobs(false);
        }
      }
    }

    loadJobs();

    return () => {
      cancelled = true;
    };
  }, [filters]);

  /*
   * Analytics are independent of explorer filters.
   * Load them once.
   */
  useEffect(() => {
    let cancelled = false;

    async function loadAnalytics() {
      try {
        setLoadingAnalytics(true);
        setAnalyticsError(null);

        const [salaryResponse, summaryResponse] = await Promise.all([
          getSalaryAnalytics(),
          getAnalyticsSummary(),
        ]);

        if (cancelled) {
          return;
        }

        setSalary(salaryResponse);
        setSummary(summaryResponse);
      } catch (error) {
        if (!cancelled) {
          setAnalyticsError(error.message);
        }
      } finally {
        if (!cancelled) {
          setLoadingAnalytics(false);
        }
      }
    }

    loadAnalytics();

    return () => {
      cancelled = true;
    };
  }, []);

  function updateFilter(name, value) {
    setFilters((current) => ({
      ...current,
      [name]: value,
      page: 1,
    }));
  }

  function changePage(page) {
    setFilters((current) => ({
      ...current,
      page,
    }));

    window.scrollTo({
      top: document.getElementById('job-explorer')?.offsetTop || 0,
      behavior: 'smooth',
    });
  }

  function clearFilters() {
    setFilters({
      search: '',
      category: '',
      location: '',
      contract_time: '',
      contract_type: '',
      min_salary: '',
      max_salary: '',
      salary_predicted: '',
      sort: 'created_desc',
      page: 1,
      page_size: DEFAULT_PAGE_SIZE,
    });
  }

  const hasFilters =
    filters.search ||
    filters.category ||
    filters.location ||
    filters.contract_time ||
    filters.contract_type ||
    filters.min_salary ||
    filters.max_salary ||
    filters.salary_predicted ||
    filters.sort !== 'created_desc';

  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="mx-auto max-w-7xl px-6 py-8 lg:px-8">
        {/* =====================================================
            HEADER
        ====================================================== */}

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
        {/* =====================================================
            APPLICATIONS TRACKER
        ====================================================== */}

        <ApplicationsPage />
        <JobApplicationActions
          job={job}
          onUpdated={(updated) => {
            setJobs((currentJobs) =>
              currentJobs.map((item) =>
                item.id === job.id
                  ? {
                      ...item,
                      ...updated,
                    }
                  : item
              )
            );
          }}
        />
        <ApplicationTracker
          job={job}
          onUpdated={(updated) => {
            setJob((current) => ({
              ...current,
              ...updated,
            }));
          }}
        />

        {/* =====================================================
            ANALYTICS
        ====================================================== */}

        {loadingAnalytics ? (
          <section className="mb-8">
            <div className="rounded-xl border border-border bg-card p-6">
              <p className="text-sm text-muted-foreground">
                Loading analytics...
              </p>
            </div>
          </section>
        ) : analyticsError ? (
          <section className="mb-8">
            <div className="rounded-xl border border-destructive/30 bg-card p-6">
              <h2 className="font-semibold">Unable to load analytics</h2>

              <p className="mt-1 text-sm text-muted-foreground">
                {analyticsError}
              </p>
            </div>
          </section>
        ) : (
          <>
            {summary && (
              <section className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <MetricCard label="Jobs" value={summary.job_count} />

                <MetricCard
                  label="Salary Records"
                  value={summary.salary_count}
                />

                <MetricCard
                  label="Mean Salary"
                  value={
                    summary.mean_salary != null
                      ? `£${Math.round(summary.mean_salary).toLocaleString()}`
                      : '—'
                  }
                />

                <MetricCard
                  label="Median Salary"
                  value={
                    summary.median_salary != null
                      ? `£${Math.round(summary.median_salary).toLocaleString()}`
                      : '—'
                  }
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
                      value={
                        salary.distribution.minimum != null
                          ? `£${salary.distribution.minimum.toLocaleString()}`
                          : '—'
                      }
                    />

                    <Stat
                      label="Maximum"
                      value={
                        salary.distribution.maximum != null
                          ? `£${salary.distribution.maximum.toLocaleString()}`
                          : '—'
                      }
                    />

                    <Stat
                      label="Mean"
                      value={
                        salary.distribution.mean != null
                          ? `£${Math.round(
                              salary.distribution.mean
                            ).toLocaleString()}`
                          : '—'
                      }
                    />

                    <Stat
                      label="Median"
                      value={
                        salary.distribution.median != null
                          ? `£${Math.round(
                              salary.distribution.median
                            ).toLocaleString()}`
                          : '—'
                      }
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
          </>
        )}

        {/* =====================================================
            JOB EXPLORER
        ====================================================== */}

        <section id="job-explorer">
          <div className="mb-5">
            <h2 className="text-xl font-semibold">Job Explorer</h2>

            <p className="mt-1 text-sm text-muted-foreground">
              Search, filter, sort, and explore the jobs stored in the analytics
              database.
            </p>
          </div>

          {/* =================================================
              FILTERS
          ================================================== */}

          <div className="mb-6 rounded-xl border border-border bg-card p-5 shadow-sm">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {/* Search */}

              <div className="lg:col-span-3">
                <label className="mb-2 block text-sm font-medium">Search</label>

                <input
                  type="text"
                  value={filters.search}
                  onChange={(event) =>
                    updateFilter('search', event.target.value)
                  }
                  placeholder="Search job title, company, description..."
                  className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
              </div>

              {/* Category */}

              <FilterInput
                label="Category"
                value={filters.category}
                onChange={(value) => updateFilter('category', value)}
                placeholder="e.g. IT jobs"
              />

              {/* Location */}

              <FilterInput
                label="Location"
                value={filters.location}
                onChange={(value) => updateFilter('location', value)}
                placeholder="e.g. London"
              />

              {/* Contract time */}

              <SelectInput
                label="Contract time"
                value={filters.contract_time}
                onChange={(value) => updateFilter('contract_time', value)}
                options={[
                  {
                    value: '',
                    label: 'All contract times',
                  },
                  {
                    value: 'full_time',
                    label: 'Full time',
                  },
                  {
                    value: 'part_time',
                    label: 'Part time',
                  },
                ]}
              />

              {/* Contract type */}

              <SelectInput
                label="Contract type"
                value={filters.contract_type}
                onChange={(value) => updateFilter('contract_type', value)}
                options={[
                  {
                    value: '',
                    label: 'All contract types',
                  },
                  {
                    value: 'permanent',
                    label: 'Permanent',
                  },
                  {
                    value: 'contract',
                    label: 'Contract',
                  },
                ]}
              />

              {/* Salary predicted */}

              <SelectInput
                label="Salary prediction"
                value={filters.salary_predicted}
                onChange={(value) => updateFilter('salary_predicted', value)}
                options={[
                  {
                    value: '',
                    label: 'All salary records',
                  },
                  {
                    value: 'true',
                    label: 'Predicted salary',
                  },
                  {
                    value: 'false',
                    label: 'Non-predicted salary',
                  },
                ]}
              />

              {/* Minimum salary */}

              <div>
                <label className="mb-2 block text-sm font-medium">
                  Minimum salary
                </label>

                <input
                  type="number"
                  min="0"
                  value={filters.min_salary}
                  onChange={(event) =>
                    updateFilter('min_salary', event.target.value)
                  }
                  placeholder="e.g. 40000"
                  className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
              </div>

              {/* Maximum salary */}

              <div>
                <label className="mb-2 block text-sm font-medium">
                  Maximum salary
                </label>

                <input
                  type="number"
                  min="0"
                  value={filters.max_salary}
                  onChange={(event) =>
                    updateFilter('max_salary', event.target.value)
                  }
                  placeholder="e.g. 100000"
                  className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
              </div>

              {/* Sort */}

              <SelectInput
                label="Sort by"
                value={filters.sort}
                onChange={(value) => updateFilter('sort', value)}
                options={[
                  {
                    value: 'created_desc',
                    label: 'Newest jobs',
                  },
                  {
                    value: 'created_asc',
                    label: 'Oldest jobs',
                  },
                  {
                    value: 'salary_desc',
                    label: 'Highest salary',
                  },
                  {
                    value: 'salary_asc',
                    label: 'Lowest salary',
                  },
                  {
                    value: 'title_asc',
                    label: 'Title A–Z',
                  },
                  {
                    value: 'title_desc',
                    label: 'Title Z–A',
                  },
                ]}
              />
            </div>

            {hasFilters && (
              <div className="mt-5 flex items-center justify-between border-t border-border pt-4">
                <p className="text-sm text-muted-foreground">
                  Filters are active.
                </p>

                <button
                  type="button"
                  onClick={clearFilters}
                  className="rounded-lg border border-border px-4 py-2 text-sm font-medium transition hover:bg-muted"
                >
                  Clear filters
                </button>
              </div>
            )}
          </div>

          {/* =================================================
              RESULTS HEADER
          ================================================== */}

          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              {loadingJobs ? (
                <p className="text-sm text-muted-foreground">Loading jobs...</p>
              ) : (
                <p className="text-sm text-muted-foreground">
                  Showing{' '}
                  <span className="font-medium text-foreground">
                    {jobs.length}
                  </span>{' '}
                  of{' '}
                  <span className="font-medium text-foreground">
                    {pagination.total}
                  </span>{' '}
                  jobs
                </p>
              )}
            </div>

            <div className="flex items-center gap-2">
              <label
                htmlFor="page-size"
                className="text-sm text-muted-foreground"
              >
                Per page
              </label>

              <select
                id="page-size"
                value={filters.page_size}
                onChange={(event) => {
                  setFilters((current) => ({
                    ...current,
                    page_size: Number(event.target.value),
                    page: 1,
                  }));
                }}
                className="rounded-lg border border-border bg-background px-3 py-2 text-sm"
              >
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
              </select>
            </div>
          </div>

          {/* =================================================
              ERROR
          ================================================== */}

          {jobsError && (
            <div className="mb-6 rounded-xl border border-destructive/30 bg-card p-6">
              <h3 className="font-semibold">Unable to load jobs</h3>

              <p className="mt-1 text-sm text-muted-foreground">{jobsError}</p>
            </div>
          )}

          {/* =================================================
              LOADING
          ================================================== */}

          {loadingJobs && !jobsError && (
            <div className="rounded-xl border border-border bg-card p-10 text-center">
              <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-4 border-primary/20 border-t-primary" />

              <p className="text-sm text-muted-foreground">Loading jobs...</p>
            </div>
          )}

          {/* =================================================
              EMPTY
          ================================================== */}

          {!loadingJobs && !jobsError && jobs.length === 0 && (
            <div className="rounded-xl border border-border bg-card p-10 text-center">
              <h3 className="font-semibold">No jobs found</h3>

              <p className="mt-2 text-sm text-muted-foreground">
                Try changing or clearing your search filters.
              </p>

              {hasFilters && (
                <button
                  type="button"
                  onClick={clearFilters}
                  className="mt-5 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
                >
                  Clear filters
                </button>
              )}
            </div>
          )}

          {/* =================================================
              TABLE
          ================================================== */}

          {!loadingJobs && !jobsError && jobs.length > 0 && (
            <>
              <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[1000px] text-left text-sm">
                    <thead className="border-b border-border bg-muted/50">
                      <tr>
                        <th className="px-5 py-4 font-medium">Job</th>

                        <th className="px-5 py-4 font-medium">Company</th>

                        <th className="px-5 py-4 font-medium">Location</th>

                        <th className="px-5 py-4 font-medium">Contract</th>

                        <th className="px-5 py-4 font-medium">Salary</th>

                        <th className="px-5 py-4 font-medium">Status</th>

                        <th className="px-5 py-4 text-right font-medium">
                          Action
                        </th>
                      </tr>
                    </thead>

                    <tbody className="divide-y divide-border">
                      {jobs.map((job) => (
                        <tr
                          key={job.id}
                          className="transition hover:bg-muted/30"
                        >
                          <td className="px-5 py-4">
                            <div className="max-w-[280px]">
                              <p className="font-semibold">{job.title}</p>

                              <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
                                {job.category_label || 'Uncategorized'}
                              </p>
                            </div>
                          </td>

                          <td className="px-5 py-4">
                            {job.company_name || 'Unknown company'}
                          </td>

                          <td className="px-5 py-4">
                            {job.location_name || job.city || 'Unknown'}
                          </td>

                          <td className="px-5 py-4">
                            <div className="flex flex-col gap-1">
                              {job.contract_time && (
                                <span>
                                  {formatContractTime(job.contract_time)}
                                </span>
                              )}

                              {job.contract_type && (
                                <span className="text-xs text-muted-foreground">
                                  {formatContractType(job.contract_type)}
                                </span>
                              )}

                              {!job.contract_time && !job.contract_type && (
                                <span className="text-muted-foreground">—</span>
                              )}
                            </div>
                          </td>

                          <td className="px-5 py-4">
                            <SalaryDisplay job={job} />
                          </td>

                          <td className="px-5 py-4">
                            <StatusBadge active={job.is_active} />
                          </td>

                          <td className="px-5 py-4 text-right">
                            <button
                              type="button"
                              onClick={() => setSelectedJob(job)}
                              className="rounded-lg border border-border px-3 py-2 text-sm font-medium transition hover:bg-muted"
                            >
                              View
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* =================================================
                    PAGINATION
                ================================================== */}

              <Pagination
                page={pagination.page}
                totalPages={pagination.total_pages}
                onPageChange={changePage}
              />
            </>
          )}
        </section>
      </div>

      {/* =======================================================
          JOB DETAIL MODAL
      ======================================================== */}

      {selectedJob && (
        <JobDetail job={selectedJob} onClose={() => setSelectedJob(null)} />
      )}
    </main>
  );
}

/* ============================================================
   FILTER COMPONENTS
============================================================ */

function FilterInput({ label, value, onChange, placeholder }) {
  return (
    <div>
      <label className="mb-2 block text-sm font-medium">{label}</label>

      <input
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
      />
    </div>
  );
}

function SelectInput({ label, value, onChange, options }) {
  return (
    <div>
      <label className="mb-2 block text-sm font-medium">{label}</label>

      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-lg border border-border bg-background px-3 py-2.5 text-sm outline-none focus:border-primary focus:ring-2 focus:ring-primary/20"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}

/* ============================================================
   PAGINATION
============================================================ */

function Pagination({ page, totalPages, onPageChange }) {
  if (totalPages <= 1) {
    return null;
  }

  const pages = [];

  const start = Math.max(1, page - 2);
  const end = Math.min(totalPages, page + 2);

  for (let current = start; current <= end; current++) {
    pages.push(current);
  }

  return (
    <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
      <button
        type="button"
        disabled={page === 1}
        onClick={() => onPageChange(page - 1)}
        className="rounded-lg border border-border px-4 py-2 text-sm font-medium transition hover:bg-muted disabled:cursor-not-allowed disabled:opacity-40"
      >
        Previous
      </button>

      <div className="flex items-center gap-1">
        {start > 1 && (
          <>
            <button
              type="button"
              onClick={() => onPageChange(1)}
              className="rounded-lg px-3 py-2 text-sm hover:bg-muted"
            >
              1
            </button>

            {start > 2 && (
              <span className="px-1 text-muted-foreground">...</span>
            )}
          </>
        )}

        {pages.map((current) => (
          <button
            key={current}
            type="button"
            onClick={() => onPageChange(current)}
            className={[
              'rounded-lg px-3 py-2 text-sm font-medium transition',
              current === page
                ? 'bg-primary text-primary-foreground'
                : 'hover:bg-muted',
            ].join(' ')}
          >
            {current}
          </button>
        ))}

        {end < totalPages && (
          <>
            {end < totalPages - 1 && (
              <span className="px-1 text-muted-foreground">...</span>
            )}

            <button
              type="button"
              onClick={() => onPageChange(totalPages)}
              className="rounded-lg px-3 py-2 text-sm hover:bg-muted"
            >
              {totalPages}
            </button>
          </>
        )}
      </div>

      <button
        type="button"
        disabled={page === totalPages}
        onClick={() => onPageChange(page + 1)}
        className="rounded-lg border border-border px-4 py-2 text-sm font-medium transition hover:bg-muted disabled:cursor-not-allowed disabled:opacity-40"
      >
        Next
      </button>
    </div>
  );
}

/* ============================================================
   JOB DETAIL
============================================================ */

function JobDetail({ job, onClose }) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          onClose();
        }
      }}
    >
      <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-xl border border-border bg-card shadow-xl">
        <div className="sticky top-0 flex items-start justify-between border-b border-border bg-card p-6">
          <div className="pr-6">
            <h2 className="text-xl font-bold">{job.title}</h2>

            <p className="mt-1 text-sm text-muted-foreground">
              {job.company_name || 'Unknown company'}
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-border px-3 py-2 text-sm hover:bg-muted"
          >
            Close
          </button>
        </div>

        <div className="space-y-6 p-6">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <DetailItem
              label="Location"
              value={job.location_name || job.city || 'Not specified'}
            />

            <DetailItem
              label="Category"
              value={job.category_label || 'Not specified'}
            />

            <DetailItem
              label="Contract time"
              value={formatContractTime(job.contract_time) || 'Not specified'}
            />

            <DetailItem
              label="Contract type"
              value={formatContractType(job.contract_type) || 'Not specified'}
            />

            <DetailItem
              label="Salary"
              value={formatSalary(job) || 'Not specified'}
            />

            <DetailItem
              label="Status"
              value={job.is_active ? 'Active' : 'Inactive'}
            />
          </div>

          <div>
            <h3 className="mb-2 font-semibold">Description</h3>

            <div className="rounded-lg bg-muted p-4 text-sm leading-6 whitespace-pre-line">
              {job.description || 'No description available.'}
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <DetailItem
              label="First seen"
              value={formatDate(job.first_seen_at)}
            />

            <DetailItem
              label="Last seen"
              value={formatDate(job.last_seen_at)}
            />

            {job.inactive_at && (
              <DetailItem
                label="Inactive since"
                value={formatDate(job.inactive_at)}
              />
            )}

            <DetailItem label="Adzuna ID" value={job.id} />
          </div>

          {job.redirect_url && (
            <div className="border-t border-border pt-5">
              <a
                href={job.redirect_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground transition hover:opacity-90"
              >
                View original Adzuna listing
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function DetailItem({ label, value }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>

      <p className="mt-1 text-sm font-medium">{value}</p>
    </div>
  );
}

/* ============================================================
   DISPLAY HELPERS
============================================================ */

function SalaryDisplay({ job }) {
  if (job.salary_min == null && job.salary_max == null) {
    return <span className="text-muted-foreground">Not specified</span>;
  }

  return (
    <div>
      <p className="font-medium">{formatSalary(job)}</p>

      {job.salary_is_predicted && (
        <p className="mt-1 text-xs text-muted-foreground">Predicted</p>
      )}
    </div>
  );
}

function formatSalary(job) {
  if (job.salary_min != null && job.salary_max != null) {
    return `£${Number(job.salary_min).toLocaleString()} – £${Number(
      job.salary_max
    ).toLocaleString()}`;
  }

  if (job.salary_min != null) {
    return `From £${Number(job.salary_min).toLocaleString()}`;
  }

  if (job.salary_max != null) {
    return `Up to £${Number(job.salary_max).toLocaleString()}`;
  }

  return null;
}

function formatContractTime(value) {
  if (!value) {
    return '';
  }

  return value
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatContractType(value) {
  if (!value) {
    return '';
  }

  return value
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatDate(value) {
  if (!value) {
    return 'Not available';
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

/* ============================================================
   STATUS
============================================================ */

function StatusBadge({ active }) {
  return (
    <span
      className={[
        'inline-flex rounded-full px-2.5 py-1 text-xs font-medium',
        active
          ? 'bg-primary/10 text-primary'
          : 'bg-muted text-muted-foreground',
      ].join(' ')}
    >
      {active ? 'Active' : 'Inactive'}
    </span>
  );
}

/* ============================================================
   DASHBOARD COMPONENTS
============================================================ */

function ThemeSwitcher({ theme, setTheme }) {
  return (
    <div className="flex items-center rounded-lg border border-border bg-card p-1 shadow-sm">
      <ThemeButton
        label="Light"
        active={theme === 'light'}
        onClick={() => setTheme('light')}
      />

      <ThemeButton
        label="Dark"
        active={theme === 'dark'}
        onClick={() => setTheme('dark')}
      />

      <ThemeButton
        label="System"
        active={theme === 'system'}
        onClick={() => setTheme('system')}
      />
    </div>
  );
}

function ThemeButton({ label, active, onClick }) {
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
