import { useEffect, useState } from 'react';
import { getJobs } from '../api';
import PageIntro from '../components/PageIntro';

const DEFAULT_PAGE_SIZE =
  parseInt(import.meta.env.VITE_DEFAULT_PAGE_SIZE, 10) || 25;
const initialFilters = {
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
};

export default function JobExplorerPage({ onOpenJob }) {
  const [filters, setFilters] = useState(() => ({
    ...initialFilters,
    ...readFilters(),
  }));
  const [result, setResult] = useState({
    items: [],
    pagination: {
      page: 1,
      page_size: DEFAULT_PAGE_SIZE,
      total: 0,
      total_pages: 1,
    },
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    updateUrl(filters);
    let cancelled = false;
    getJobs(filters)
      .then((response) => {
        if (!cancelled) setResult(response);
      })
      .catch((loadError) => {
        if (!cancelled) setError(loadError.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [filters]);
  const updateFilter = (name, value) =>
    setFilters((current) => ({ ...current, [name]: value, page: 1 }));
  const clear = () => setFilters({ ...initialFilters });
  const hasFilters =
    Object.entries(filters).some(
      ([key, value]) =>
        key !== 'page' && key !== 'page_size' && key !== 'sort' && value
    ) || filters.sort !== 'created_desc';

  return (
    <div>
      <PageIntro
        eyebrow="Explore opportunities"
        title="Job explorer"
        description="Search, filter, and compare the jobs stored in your analytics database."
      />
      <FilterPanel
        filters={filters}
        onChange={updateFilter}
        onClear={clear}
        hasFilters={hasFilters}
      />
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-muted-foreground">
          {loading
            ? 'Loading jobs...'
            : `Showing ${result.items?.length || 0} of ${result.pagination?.total || 0} jobs`}
        </p>
        <label className="flex items-center gap-2 text-sm text-muted-foreground">
          Per page
          <select
            value={filters.page_size}
            onChange={(event) =>
              setFilters((current) => ({
                ...current,
                page_size: Number(event.target.value),
                page: 1,
              }))
            }
            className="rounded-lg border border-border bg-background px-3 py-2 text-sm"
          >
            <option>10</option>
            <option>25</option>
            <option>50</option>
            <option>100</option>
          </select>
        </label>
      </div>
      {error && (
        <div className="mb-6 rounded-xl border border-destructive/30 bg-card p-6">
          <h2 className="font-semibold">Unable to load jobs</h2>
          <p className="mt-1 text-sm text-muted-foreground">{error}</p>
        </div>
      )}
      {loading && !error && (
        <div className="rounded-xl border border-border bg-card p-10 text-center text-sm text-muted-foreground">
          Loading jobs...
        </div>
      )}
      {!loading && !error && !result.items?.length && (
        <div className="rounded-xl border border-border bg-card p-10 text-center">
          <h2 className="font-semibold">No jobs found</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Try changing or clearing your search filters.
          </p>
        </div>
      )}
      {!loading && !error && result.items?.length > 0 && (
        <>
          <JobTable jobs={result.items} onOpenJob={onOpenJob} />
          <Pagination
            page={result.pagination?.page || filters.page}
            totalPages={result.pagination?.total_pages || 1}
            onChange={(page) => setFilters((current) => ({ ...current, page }))}
          />
        </>
      )}
    </div>
  );
}

function FilterPanel({ filters, onChange, onClear, hasFilters }) {
  const select = (label, name, options) => (
    <label className="text-sm font-medium">
      {label}
      <select
        value={filters[name]}
        onChange={(event) => onChange(name, event.target.value)}
        className="mt-2 w-full rounded-lg border border-border bg-background px-3 py-2.5 font-normal outline-none focus:border-primary"
      >
        {options.map(([value, text]) => (
          <option key={value} value={value}>
            {text}
          </option>
        ))}
      </select>
    </label>
  );
  return (
    <section className="mb-6 rounded-xl border border-border bg-card p-5 shadow-sm">
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <label className="text-sm font-medium md:col-span-2 xl:col-span-3">
          Search
          <input
            value={filters.search}
            onChange={(event) => onChange('search', event.target.value)}
            placeholder="Search title, company, description..."
            className="mt-2 w-full rounded-lg border border-border bg-background px-3 py-2.5 font-normal outline-none focus:border-primary"
          />
        </label>
        <Field
          label="Category"
          name="category"
          filters={filters}
          onChange={onChange}
          placeholder="e.g. IT jobs"
        />
        <Field
          label="Location"
          name="location"
          filters={filters}
          onChange={onChange}
          placeholder="e.g. London"
        />
        {select('Contract time', 'contract_time', [
          ['', 'All contract times'],
          ['full_time', 'Full time'],
          ['part_time', 'Part time'],
        ])}
        {select('Contract type', 'contract_type', [
          ['', 'All contract types'],
          ['permanent', 'Permanent'],
          ['contract', 'Contract'],
        ])}
        {select('Salary prediction', 'salary_predicted', [
          ['', 'All salary records'],
          ['true', 'Predicted salary'],
          ['false', 'Non-predicted salary'],
        ])}
        <Field
          label="Minimum salary"
          name="min_salary"
          type="number"
          filters={filters}
          onChange={onChange}
          placeholder="e.g. 40000"
        />
        <Field
          label="Maximum salary"
          name="max_salary"
          type="number"
          filters={filters}
          onChange={onChange}
          placeholder="e.g. 100000"
        />
        {select('Sort by', 'sort', [
          ['created_desc', 'Newest jobs'],
          ['created_asc', 'Oldest jobs'],
          ['salary_desc', 'Highest salary'],
          ['salary_asc', 'Lowest salary'],
          ['title_asc', 'Title A-Z'],
          ['title_desc', 'Title Z-A'],
        ])}
      </div>
      {hasFilters && (
        <div className="mt-5 flex items-center justify-between border-t border-border pt-4">
          <span className="text-sm text-muted-foreground">
            Filters are active.
          </span>
          <button
            type="button"
            onClick={onClear}
            className="rounded-lg border border-border px-4 py-2 text-sm font-medium hover:bg-muted"
          >
            Clear filters
          </button>
        </div>
      )}
    </section>
  );
}
function Field({ label, name, type = 'text', filters, onChange, placeholder }) {
  return (
    <label className="text-sm font-medium">
      {label}
      <input
        type={type}
        min={type === 'number' ? 0 : undefined}
        value={filters[name]}
        onChange={(event) => onChange(name, event.target.value)}
        placeholder={placeholder}
        className="mt-2 w-full rounded-lg border border-border bg-background px-3 py-2.5 font-normal outline-none focus:border-primary"
      />
    </label>
  );
}
function JobTable({ jobs, onOpenJob }) {
  return (
    <div className="overflow-hidden rounded-xl border border-border bg-card shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[900px] text-left text-sm">
          <thead className="border-b border-border bg-muted/50">
            <tr>
              {[
                'Job',
                'Company',
                'Location',
                'Contract',
                'Salary',
                'Status',
                '',
              ].map((heading) => (
                <th key={heading} className="px-5 py-4 font-medium">
                  {heading}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {jobs.map((job) => (
              <tr key={job.id} className="hover:bg-muted/30">
                <td className="max-w-[280px] px-5 py-4">
                  <p className="font-semibold">{job.title}</p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {job.category_label || 'Uncategorized'}
                  </p>
                </td>
                <td className="px-5 py-4">
                  {job.company_name || 'Unknown company'}
                </td>
                <td className="px-5 py-4">
                  {job.location_name || job.city || 'Unknown'}
                </td>
                <td className="px-5 py-4">
                  {[format(job.contract_time), format(job.contract_type)]
                    .filter(Boolean)
                    .join(' · ') || '—'}
                </td>
                <td className="px-5 py-4">{salary(job)}</td>
                <td className="px-5 py-4">
                  <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">
                    {job.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td className="px-5 py-4 text-right">
                  <button
                    type="button"
                    onClick={() => onOpenJob(job)}
                    className="rounded-lg border border-border px-3 py-2 text-sm font-medium hover:bg-muted"
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
  );
}
function Pagination({ page, totalPages, onChange }) {
  if (totalPages <= 1) return null;
  return (
    <div className="mt-5 flex justify-between gap-3">
      <button
        type="button"
        disabled={page === 1}
        onClick={() => onChange(page - 1)}
        className="rounded-lg border border-border px-4 py-2 text-sm disabled:opacity-40"
      >
        Previous
      </button>
      <span className="py-2 text-sm text-muted-foreground">
        Page {page} of {totalPages}
      </span>
      <button
        type="button"
        disabled={page === totalPages}
        onClick={() => onChange(page + 1)}
        className="rounded-lg border border-border px-4 py-2 text-sm disabled:opacity-40"
      >
        Next
      </button>
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
function salary(job) {
  if (job.salary_min == null && job.salary_max == null) return 'Not specified';
  if (job.salary_min != null && job.salary_max != null)
    return `£${Number(job.salary_min).toLocaleString()} – £${Number(job.salary_max).toLocaleString()}`;
  return job.salary_min != null
    ? `From £${Number(job.salary_min).toLocaleString()}`
    : `Up to £${Number(job.salary_max).toLocaleString()}`;
}
function readFilters() {
  const params = new URLSearchParams(window.location.search);
  return Object.fromEntries(
    Object.keys(initialFilters)
      .filter((key) => params.has(key))
      .map((key) => [
        key,
        key === 'page' || key === 'page_size'
          ? Number(params.get(key))
          : params.get(key),
      ])
  );
}
function updateUrl(filters) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (
      value &&
      value !== initialFilters[key] &&
      key !== 'page' &&
      key !== 'page_size'
    )
      params.set(key, value);
  });
  if (filters.page > 1) params.set('page', filters.page);
  if (filters.page_size !== DEFAULT_PAGE_SIZE)
    params.set('page_size', filters.page_size);
  window.history.replaceState(
    {},
    '',
    params.toString() ? `/jobs?${params}` : '/jobs'
  );
}
