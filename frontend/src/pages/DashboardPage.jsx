import { useEffect, useState } from 'react';
import {
  getAnalyticsMetadata,
  getAnalyticsSummary,
  getSalaryAnalytics,
  getSalaryDistribution,
} from '../api';

import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState(null);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [distribution, setDistribution] = useState(null);

  const [loading, setLoading] = useState(true);
  const [distributionLoading, setDistributionLoading] = useState(false);
  const [error, setError] = useState(null);
  const [distributionError, setDistributionError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    Promise.all([
      getSalaryAnalytics(),
      getAnalyticsSummary(),
      getAnalyticsMetadata(),
    ])
      .then(([salary, summary, metadata]) => {
        if (cancelled) return;

        setAnalytics({
          salary,
          summary,
        });

        setCategories(metadata.categories || []);
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

  useEffect(() => {
    let cancelled = false;

    setDistributionLoading(true);
    setDistributionError(null);

    getSalaryDistribution(selectedCategory || null)
      .then((data) => {
        if (cancelled) return;

        setDistribution(data);
        setDistributionLoading(false);
      })
      .catch((loadError) => {
        if (cancelled) return;

        setDistributionError(loadError.message);
        setDistributionLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [selectedCategory]);

  return (
    <div>
      <PageIntro
        eyebrow="Market overview"
        title="Job market dashboard"
        description="A focused view of salary patterns and the latest technology job market snapshot."
      />

      {loading && <Panel>Loading analytics...</Panel>}

      {error && (
        <Panel>
          <h2 className="font-semibold">Unable to load analytics</h2>

          <p className="mt-1 text-sm text-muted-foreground">{error}</p>
        </Panel>
      )}

      {analytics && (
        <DashboardContent
          salary={analytics.salary}
          summary={analytics.summary}
          categories={categories}
          selectedCategory={selectedCategory}
          onCategoryChange={setSelectedCategory}
          distribution={distribution}
          distributionLoading={distributionLoading}
          distributionError={distributionError}
        />
      )}
    </div>
  );
}

function DashboardContent({
  salary,
  summary,
  categories,
  selectedCategory,
  onCategoryChange,
  distribution,
  distributionLoading,
  distributionError,
}) {
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

      <SalaryDistributionPanel
        categories={categories}
        selectedCategory={selectedCategory}
        onCategoryChange={onCategoryChange}
        distribution={distribution}
        loading={distributionLoading}
        error={distributionError}
      />

      <section className="grid gap-6 xl:grid-cols-2">
        <Panel>
          <h2 className="text-lg font-semibold">Salary statistics</h2>

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

            <Stat label="Q1" value={money(salary.distribution.q1, true)} />

            <Stat label="Q3" value={money(salary.distribution.q3, true)} />

            <Stat label="IQR" value={money(salary.distribution.iqr, true)} />

            <Stat
              label="Std. deviation"
              value={money(salary.distribution.standard_deviation, true)}
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

function SalaryDistributionPanel({
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
        <div className="mt-8 flex h-80 items-center justify-center rounded-lg bg-muted/40">
          <p className="text-sm text-muted-foreground">
            Loading salary distribution...
          </p>
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
                  top: 10,
                  right: 10,
                  left: 0,
                  bottom: 10,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" vertical={false} />

                <XAxis
                  dataKey="label"
                  tick={{ fontSize: 12 }}
                  tickLine={false}
                  axisLine={false}
                />

                <YAxis
                  allowDecimals={false}
                  tick={{ fontSize: 12 }}
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
