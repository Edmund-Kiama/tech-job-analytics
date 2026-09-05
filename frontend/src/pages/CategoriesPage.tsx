import { useEffect, useState } from 'react';
import { getCategories, getCategoryAnalytics } from '../api';
import Loader from '../components/Loader';
import PageIntro from '../components/PageIntro';
import Panel from '../components/Panel';

function money(value) {
  return value == null ? 'Not available' : `£${Number(value).toLocaleString()}`;
}

function salary(job) {
  if (job.salary_min != null && job.salary_max != null)
    return `${money(job.salary_min)} – ${money(job.salary_max)}`;
  return money(job.salary);
}

export default function CategoriesPage({ onOpenJob }) {
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    getCategories()
      .then((response) => {
        const values = response.categories || [];
        setCategories(values);
        if (values.length) setSelectedCategory(values[0]);
      })
      .catch((loadError) => setError(loadError.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedCategory) return undefined;
    let cancelled = false;
    async function loadCategory() {
      setDetailLoading(true);
      setError(null);
      try {
        const response = await getCategoryAnalytics(selectedCategory);
        if (!cancelled) setData(response);
      } catch (loadError) {
        if (!cancelled) setError(loadError.message);
      } finally {
        if (!cancelled) setDetailLoading(false);
      }
    }
    loadCategory();
    return () => {
      cancelled = true;
    };
  }, [selectedCategory]);

  return (
    <div>
      <PageIntro
        eyebrow="Market segments"
        title="Categories"
        description="Compare the size and compensation of active job categories, then inspect their strongest listings."
      />
      {loading && (
        <Panel>
          <Loader label="Loading categories..." />
        </Panel>
      )}
      {error && (
        <Panel>
          <p className="text-sm text-destructive">{error}</p>
        </Panel>
      )}
      {!loading && !error && (
        <div className="grid gap-6 lg:grid-cols-[260px_minmax(0,1fr)]">
          <Panel>
            <h2 className="text-lg font-semibold">Browse categories</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              {categories.length} categories found
            </p>
            <div className="mt-5 max-h-128 space-y-1 overflow-y-auto">
              {categories.map((category) => (
                <button
                  key={category}
                  type="button"
                  onClick={() => setSelectedCategory(category)}
                  className={`w-full rounded-lg px-3 py-2.5 text-left text-sm font-medium ${selectedCategory === category ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}`}
                >
                  {category}
                </button>
              ))}
            </div>
          </Panel>
          <div className="space-y-6">
            {detailLoading && (
              <Panel>
                <Loader label="Loading category analysis..." />
              </Panel>
            )}
            {data && !detailLoading && (
              <CategoryContent data={data} onOpenJob={onOpenJob} />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function CategoryContent({ data, onOpenJob }) {
  return (
    <>
      <Panel>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">
              Active listings
            </p>
            <h2 className="mt-2 text-2xl font-semibold">{data.category}</h2>
          </div>
          <p className="text-3xl font-bold">{data.job_count}</p>
        </div>
        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Stat label="Median salary" value={data.salary?.median} />
          <Stat label="Mean salary" value={data.salary?.mean} />
          <Stat label="Lowest salary" value={data.salary?.minimum} />
          <Stat label="Highest salary" value={data.salary?.maximum} />
        </div>
      </Panel>
      <Panel>
        <div>
          <h2 className="text-lg font-semibold">Top jobs in {data.category}</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Ranked by normalized salary midpoint.
          </p>
        </div>
        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-170 text-left text-sm">
            <thead className="border-b border-border">
              <tr>
                <th className="px-3 py-3 font-medium text-muted-foreground">
                  #
                </th>
                <th className="px-3 py-3 font-medium text-muted-foreground">
                  Role
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
                <th />
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {data.top_jobs.map((job) => (
                <tr key={job.id}>
                  <td className="px-3 py-3 font-semibold">{job.rank}</td>
                  <td className="px-3 py-3 font-medium">{job.title}</td>
                  <td className="px-3 py-3 text-muted-foreground">
                    {job.company_name || 'Unknown company'}
                  </td>
                  <td className="px-3 py-3 text-muted-foreground">
                    {job.location_name || 'Not specified'}
                  </td>
                  <td className="px-3 py-3 text-right font-semibold">
                    {salary(job)}
                  </td>
                  <td className="px-3 py-3 text-right">
                    <button
                      type="button"
                      onClick={() => onOpenJob(job)}
                      className="rounded-lg border border-border px-3 py-2 text-xs font-medium hover:bg-muted"
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </>
  );
}

function Stat({ label, value }) {
  return (
    <div className="rounded-lg bg-muted p-4">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 font-semibold">{money(value)}</p>
    </div>
  );
}
