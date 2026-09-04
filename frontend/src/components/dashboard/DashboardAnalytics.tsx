import { useEffect, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import {
  getAnalyticsBreakdown,
  getAnalyticsSummary,
  getSalaryAnalytics,
} from '../../api';
import PageIntro from '../PageIntro';
import Loader from '../Loader';
import Panel from '../Panel';

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    Promise.all([
      getSalaryAnalytics(),
      getAnalyticsSummary(),
      getAnalyticsBreakdown(),
    ])
      .then(([salary, summary, breakdown]) => {
        if (cancelled) return;

        setAnalytics({
          salary,
          summary,
          breakdown,
        });
        setLoading(false);
      })
      .catch((loadError) => {
        if (cancelled) return;

        setError(loadError.message);
        setLoading(false);
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
        description="A focused analytical view of salary patterns, job-market composition, compensation, and market activity."
      />

      {loading && (
        <Panel>
          <Loader label="Loading analytics..." />
        </Panel>
      )}

      {error && (
        <Panel>
          <h2 className="font-semibold">Unable to load analytics</h2>

          <p className="mt-1 text-sm text-muted-foreground">{error}</p>
        </Panel>
      )}

      {analytics && <DashboardContent analytics={analytics} />}
    </div>
  );
}

function DashboardContent({ analytics }) {
  const { summary, breakdown } = analytics;

  const activeJobs = breakdown.job_status?.active ?? 0;

  const inactiveJobs = breakdown.job_status?.inactive ?? 0;

  return (
    <div className="space-y-6">
      {/* ================================================= */}
      {/* KPI OVERVIEW */}
      {/* ================================================= */}

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
        <Metric label="Total jobs" value={summary.job_count} />

        <Metric label="Salary records" value={summary.salary_count} />

        <Metric label="Active jobs" value={activeJobs} />

        <Metric label="Inactive jobs" value={inactiveJobs} />

        <Metric label="Mean salary" value={money(summary.mean_salary, true)} />

        <Metric
          label="Median salary"
          value={money(summary.median_salary, true)}
        />
      </section>

      <Panel>
        <h2 className="text-lg font-semibold">Your analytics workspace</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Use the analytics pages in the sidebar to explore salary, market
          structure, and activity in detail.
        </p>
      </Panel>
    </div>
  );
}

/* =========================================================
   SALARY DISTRIBUTION
   ========================================================= */

export function SalaryDistributionPanel({
  categories,
  selectedCategory,
  onCategoryChange,
  distribution,
  loading,
  error,
}) {
  return (
    <Panel>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold">Salary distribution</h2>

          <p className="mt-1 text-sm text-muted-foreground">
            Distribution of normalized salary midpoint values.
          </p>
        </div>

        <div className="sm:min-w-56">
          <label
            htmlFor="salary-category"
            className="mb-2 block text-sm font-medium"
          >
            Dataset
          </label>

          <select
            id="salary-category"
            value={selectedCategory}
            onChange={(event) => onCategoryChange(event.target.value)}
            className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">All Jobs</option>

            {categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading && (
        <div className="mt-8 rounded-lg bg-muted/40">
          <Loader label="Loading salary distribution..." className="h-80" />
        </div>
      )}

      {error && !loading && (
        <div className="mt-8 rounded-lg border border-border p-6">
          <p className="text-sm font-medium">Unable to load distribution</p>

          <p className="mt-1 text-sm text-muted-foreground">{error}</p>
        </div>
      )}

      {distribution && !loading && !error && (
        <>
          <div className="mt-8 h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={distribution.bins}
                margin={{
                  top: 20,
                  right: 10,
                  left: 0,
                  bottom: 10,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" vertical={false} />

                <XAxis
                  dataKey="label"
                  tick={{
                    fontSize: 12,
                  }}
                  tickLine={false}
                  axisLine={false}
                />

                <YAxis
                  allowDecimals={false}
                  tick={{
                    fontSize: 12,
                  }}
                  tickLine={false}
                  axisLine={false}
                />

                <Tooltip
                  formatter={(value) => [value, 'Jobs']}
                  labelFormatter={(label) => `Salary: ${label}`}
                />

                <ReferenceLine
                  x={findBinLabel(
                    distribution.bins,
                    distribution.statistics.mean
                  )}
                  strokeDasharray="5 5"
                  label={{
                    value: 'Mean',
                    position: 'top',
                  }}
                />

                <ReferenceLine
                  x={findBinLabel(
                    distribution.bins,
                    distribution.statistics.median
                  )}
                  strokeDasharray="5 5"
                  label={{
                    value: 'Median',
                    position: 'insideTopRight',
                  }}
                />

                <Bar dataKey="count" name="Jobs" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-8">
            <Stat
              label="Minimum"
              value={money(distribution.statistics.minimum, true)}
            />

            <Stat label="Q1" value={money(distribution.statistics.q1, true)} />

            <Stat
              label="Median"
              value={money(distribution.statistics.median, true)}
            />

            <Stat
              label="Mean"
              value={money(distribution.statistics.mean, true)}
            />

            <Stat label="Q3" value={money(distribution.statistics.q3, true)} />

            <Stat
              label="Maximum"
              value={money(distribution.statistics.maximum, true)}
            />

            <Stat
              label="IQR"
              value={money(distribution.statistics.iqr, true)}
            />

            <Stat label="Outliers" value={distribution.outliers.total} />
          </div>

          <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-sm text-muted-foreground">
            <span>
              Jobs analyzed:{' '}
              <strong className="text-foreground">
                {distribution.job_count}
              </strong>
            </span>

            <span>
              Lower outliers:{' '}
              <strong className="text-foreground">
                {distribution.outliers.lower}
              </strong>
            </span>

            <span>
              Upper outliers:{' '}
              <strong className="text-foreground">
                {distribution.outliers.upper}
              </strong>
            </span>
          </div>
        </>
      )}
    </Panel>
  );
}

/* =========================================================
   SALARY STATISTICS
   ========================================================= */

export function SalaryStatistics({ salary }) {
  return (
    <Panel>
      <h2 className="text-lg font-semibold">Salary statistics</h2>

      <p className="mt-1 text-sm text-muted-foreground">
        Statistical summary of the latest salary dataset.
      </p>

      <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Stat
          label="Minimum"
          value={money(salary.distribution.minimum, true)}
        />

        <Stat label="Q1" value={money(salary.distribution.q1, true)} />

        <Stat label="Median" value={money(salary.distribution.median, true)} />

        <Stat label="Mean" value={money(salary.distribution.mean, true)} />

        <Stat label="Q3" value={money(salary.distribution.q3, true)} />

        <Stat
          label="Maximum"
          value={money(salary.distribution.maximum, true)}
        />

        <Stat label="IQR" value={money(salary.distribution.iqr, true)} />

        <Stat
          label="Std. deviation"
          value={money(salary.distribution.standard_deviation, true)}
        />
      </div>

      <div className="mt-6 rounded-lg bg-muted p-4">
        <p className="text-xs text-muted-foreground">
          Standard deviation range
        </p>

        <p className="mt-2 text-sm font-medium">
          1σ: {money(salary.standard_deviation_ranges.lower_1_std, true)} –{' '}
          {money(salary.standard_deviation_ranges.upper_1_std, true)}
        </p>

        <p className="mt-1 text-sm font-medium">
          2σ: {money(salary.standard_deviation_ranges.lower_2_std, true)} –{' '}
          {money(salary.standard_deviation_ranges.upper_2_std, true)}
        </p>
      </div>
    </Panel>
  );
}

/* =========================================================
   SALARY COVERAGE
   ========================================================= */

export function SalaryCoverage({ salary, totalJobs }) {
  const midpointCount = salary.salary_coverage.with_midpoint_salary;

  const coveragePercentage =
    totalJobs > 0 ? Math.round((midpointCount / totalJobs) * 100) : 0;

  return (
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

      <div className="mt-6 rounded-lg bg-muted p-4">
        <p className="text-xs text-muted-foreground">
          Midpoint salary coverage
        </p>

        <p className="mt-2 text-2xl font-bold">{coveragePercentage}%</p>

        <p className="mt-1 text-xs text-muted-foreground">
          {midpointCount} of {totalJobs} listings contain a normalized midpoint
          salary.
        </p>
      </div>
    </Panel>
  );
}

/* =========================================================
   CATEGORY ANALYTICS
   ========================================================= */

export function CategoryAnalytics({ categories }) {
  return (
    <section className="grid gap-6 xl:grid-cols-2">
      <Panel>
        <h2 className="text-lg font-semibold">Jobs by category</h2>

        <p className="mt-1 text-sm text-muted-foreground">
          Categories with the highest number of listings.
        </p>

        <div className="mt-6 h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={categories}
              layout="vertical"
              margin={{
                top: 5,
                right: 20,
                left: 10,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />

              <XAxis type="number" allowDecimals={false} />

              <YAxis
                type="category"
                dataKey="category"
                width={120}
                tick={{
                  fontSize: 11,
                }}
              />

              <Tooltip />

              <Bar dataKey="job_count" name="Jobs" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Panel>

      <Panel>
        <h2 className="text-lg font-semibold">Salary by category</h2>

        <p className="mt-1 text-sm text-muted-foreground">
          Mean and median normalized salary by category.
        </p>

        <div className="mt-6 h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={categories}
              layout="vertical"
              margin={{
                top: 5,
                right: 20,
                left: 10,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />

              <XAxis
                type="number"
                tickFormatter={(value) => `£${Math.round(value / 1000)}k`}
              />

              <YAxis
                type="category"
                dataKey="category"
                width={120}
                tick={{
                  fontSize: 11,
                }}
              />

              <Tooltip formatter={(value) => money(value, true)} />

              <Bar
                dataKey="mean_salary"
                name="Mean salary"
                radius={[0, 4, 4, 0]}
              />

              <Bar
                dataKey="median_salary"
                name="Median salary"
                radius={[0, 4, 4, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Panel>
    </section>
  );
}

/* =========================================================
   LOCATION ANALYTICS
   ========================================================= */

export function LocationAnalytics({ locations }) {
  return (
    <section className="grid gap-6 xl:grid-cols-2">
      <Panel>
        <h2 className="text-lg font-semibold">Jobs by location</h2>

        <p className="mt-1 text-sm text-muted-foreground">
          Locations with the highest number of listings.
        </p>

        <div className="mt-6 h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={locations}
              layout="vertical"
              margin={{
                top: 5,
                right: 20,
                left: 10,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />

              <XAxis type="number" allowDecimals={false} />

              <YAxis
                type="category"
                dataKey="location"
                width={120}
                tick={{
                  fontSize: 11,
                }}
              />

              <Tooltip />

              <Bar dataKey="job_count" name="Jobs" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Panel>

      <Panel>
        <h2 className="text-lg font-semibold">Salary by location</h2>

        <p className="mt-1 text-sm text-muted-foreground">
          Mean and median normalized salary by location.
        </p>

        <div className="mt-6 h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={locations}
              layout="vertical"
              margin={{
                top: 5,
                right: 20,
                left: 10,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />

              <XAxis
                type="number"
                tickFormatter={(value) => `£${Math.round(value / 1000)}k`}
              />

              <YAxis
                type="category"
                dataKey="location"
                width={120}
                tick={{
                  fontSize: 11,
                }}
              />

              <Tooltip formatter={(value) => money(value, true)} />

              <Bar
                dataKey="mean_salary"
                name="Mean salary"
                radius={[0, 4, 4, 0]}
              />

              <Bar
                dataKey="median_salary"
                name="Median salary"
                radius={[0, 4, 4, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Panel>
    </section>
  );
}

/* =========================================================
   CONTRACT TIME
   ========================================================= */

export function ContractTimeAnalytics({ data }) {
  return (
    <DistributionPanel
      title="Contract time"
      description="Distribution of permanent versus temporary and other contract durations."
      data={data}
      labelKey="contract_time"
    />
  );
}

/* =========================================================
   CONTRACT TYPE
   ========================================================= */

export function ContractTypeAnalytics({ data }) {
  return (
    <DistributionPanel
      title="Contract type"
      description="Distribution of available contract types."
      data={data}
      labelKey="contract_type"
    />
  );
}

/* =========================================================
   SALARY PREDICTION
   ========================================================= */

export function SalaryPredictionAnalytics({ data }) {
  const normalizedData = data.map((item) => ({
    ...item,
    label: item.salary_predicted ? 'Predicted' : 'Not predicted',
  }));

  return (
    <DistributionPanel
      title="Salary prediction"
      description="Whether salary values are predicted by the source."
      data={normalizedData}
      labelKey="label"
    />
  );
}

function DistributionPanel({ title, description, data, labelKey }) {
  return (
    <Panel>
      <h2 className="text-lg font-semibold">{title}</h2>

      <p className="mt-1 text-sm text-muted-foreground">{description}</p>

      <div className="mt-6 h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            margin={{
              top: 5,
              right: 10,
              left: 0,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} />

            <XAxis
              dataKey={labelKey}
              tick={{
                fontSize: 11,
              }}
            />

            <YAxis allowDecimals={false} />

            <Tooltip />

            <Bar dataKey="job_count" name="Jobs" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Panel>
  );
}

/* =========================================================
   TOP SALARY JOBS
   ========================================================= */

export function TopSalaryJobs({ jobs }) {
  return (
    <Panel>
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-lg font-semibold">Highest paying jobs</h2>

          <p className="mt-1 text-sm text-muted-foreground">
            Top listings ranked by normalized salary midpoint.
          </p>
        </div>

        <span className="rounded-full bg-muted px-3 py-1 text-xs font-medium">
          Top 10
        </span>
      </div>

      <div className="mt-6 overflow-x-auto">
        <table className="w-full min-w-[700px] text-sm">
          <thead>
            <tr className="border-b border-border text-left">
              <th className="px-3 py-3 font-medium text-muted-foreground">#</th>

              <th className="px-3 py-3 font-medium text-muted-foreground">
                Job
              </th>

              <th className="px-3 py-3 font-medium text-muted-foreground">
                Company
              </th>

              <th className="px-3 py-3 font-medium text-muted-foreground">
                Location
              </th>

              <th className="px-3 py-3 text-right font-medium text-muted-foreground">
                Salary
              </th>
            </tr>
          </thead>

          <tbody>
            {jobs.map((job) => (
              <tr key={job.id} className="border-b border-border last:border-0">
                <td className="px-3 py-3 font-semibold">{job.rank}</td>

                <td className="px-3 py-3">
                  <p className="max-w-xs truncate font-medium">{job.title}</p>
                </td>

                <td className="px-3 py-3 text-muted-foreground">
                  {job.company_name || '—'}
                </td>

                <td className="px-3 py-3 text-muted-foreground">
                  {job.location_name || '—'}
                </td>

                <td className="px-3 py-3 text-right font-semibold">
                  {money(job.salary, true)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}

/* =========================================================
   MARKET TRENDS
   ========================================================= */

export function MarketTrends({ data }) {
  if (!data.length) {
    return null;
  }

  return (
    <Panel>
      <h2 className="text-lg font-semibold">Market activity</h2>

      <p className="mt-1 text-sm text-muted-foreground">
        Job additions, inactivations, and the resulting active-job count over
        time.
      </p>

      <div className="mt-6 h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{
              top: 10,
              right: 10,
              left: 0,
              bottom: 10,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} />

            <XAxis
              dataKey="date"
              tick={{
                fontSize: 11,
              }}
            />

            <YAxis allowDecimals={false} />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="jobs_added"
              name="Jobs added"
              strokeWidth={2}
              dot={false}
            />

            <Line
              type="monotone"
              dataKey="jobs_inactivated"
              name="Jobs inactivated"
              strokeWidth={2}
              dot={false}
            />

            <Line
              type="monotone"
              dataKey="active_jobs"
              name="Active jobs"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Panel>
  );
}

/* =========================================================
   SHARED UI
   ========================================================= */

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

function findBinLabel(bins, value) {
  if (!bins || value == null) {
    return undefined;
  }

  const matchingBin = bins.find((bin, index) => {
    const isLast = index === bins.length - 1;

    return (
      value >= bin.min && (value < bin.max || (isLast && value <= bin.max))
    );
  });

  return matchingBin?.label;
}

function money(value, rounded = false) {
  return value == null
    ? '—'
    : `£${(rounded ? Math.round(value) : value).toLocaleString()}`;
}
