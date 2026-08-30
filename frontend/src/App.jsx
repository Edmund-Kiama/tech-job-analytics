import { useEffect, useState } from "react";
import {
  getAnalyticsSummary,
  getJobs,
  getSalaryAnalytics,
} from "./api";
import "./App.css";

function formatCurrency(value) {
  if (value === null || value === undefined) {
    return "N/A";
  }

  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "GBP",
    maximumFractionDigits: 0,
  }).format(value);
}

function App() {
  const [jobs, setJobs] = useState([]);
  const [salary, setSalary] = useState(null);
  const [summary, setSummary] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setLoading(true);
        setError(null);

        const [jobsData, salaryData, summaryData] = await Promise.all([
          getJobs(),
          getSalaryAnalytics(),
          getAnalyticsSummary(),
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

    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <main className="app">
        <div className="state-card">
          <div className="loading-spinner" />
          <h2>Loading analytics...</h2>
          <p>Fetching jobs and salary data from the API.</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="app">
        <div className="state-card error-card">
          <h1>Unable to load dashboard</h1>
          <p>{error}</p>
          <p className="state-help">
            Make sure the FastAPI server is running on port 8000.
          </p>
        </div>
      </main>
    );
  }

  if (!jobs.length && !salary && !summary) {
    return (
      <main className="app">
        <div className="state-card">
          <h1>No analytics available</h1>
          <p>The API returned no dashboard data.</p>
        </div>
      </main>
    );
  }

  return (
    <main className="app">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">TECH JOB ANALYTICS</p>
          <h1>Job Market Dashboard</h1>
          <p className="header-description">
            Salary and job-market analytics powered by Adzuna data.
          </p>
        </div>

        {summary && (
          <div className="analysis-badge">
            <span>Analysis</span>
            <strong>{summary.analysis_version}</strong>
          </div>
        )}
      </header>

      {summary && (
        <section className="summary-grid">
          <article className="metric-card">
            <span className="metric-label">Jobs</span>
            <strong className="metric-value">{summary.job_count}</strong>
          </article>

          <article className="metric-card">
            <span className="metric-label">Salary Records</span>
            <strong className="metric-value">{summary.salary_count}</strong>
          </article>

          <article className="metric-card">
            <span className="metric-label">Average Salary</span>
            <strong className="metric-value">
              {formatCurrency(summary.mean_salary)}
            </strong>
          </article>

          <article className="metric-card">
            <span className="metric-label">Median Salary</span>
            <strong className="metric-value">
              {formatCurrency(summary.median_salary)}
            </strong>
          </article>
        </section>
      )}

      {salary && (
        <section className="dashboard-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">SALARY ANALYTICS</p>
              <h2>Salary Distribution</h2>
            </div>
          </div>

          <div className="analytics-grid">
            <article className="analytics-card">
              <span>Minimum</span>
              <strong>{formatCurrency(salary.distribution.minimum)}</strong>
            </article>

            <article className="analytics-card">
              <span>Maximum</span>
              <strong>{formatCurrency(salary.distribution.maximum)}</strong>
            </article>

            <article className="analytics-card">
              <span>Mean</span>
              <strong>{formatCurrency(salary.distribution.mean)}</strong>
            </article>

            <article className="analytics-card">
              <span>Median</span>
              <strong>{formatCurrency(salary.distribution.median)}</strong>
            </article>

            <article className="analytics-card">
              <span>25th Percentile</span>
              <strong>{formatCurrency(salary.distribution.p25)}</strong>
            </article>

            <article className="analytics-card">
              <span>75th Percentile</span>
              <strong>{formatCurrency(salary.distribution.p75)}</strong>
            </article>
          </div>

          <div className="analytics-detail-grid">
            <article className="detail-card">
              <h3>Standard Deviation</h3>

              <div className="detail-row">
                <span>Standard deviation</span>
                <strong>
                  {formatCurrency(
                    salary.distribution.standard_deviation,
                  )}
                </strong>
              </div>

              <div className="detail-row">
                <span>1σ range</span>
                <strong>
                  {formatCurrency(
                    salary.standard_deviation_ranges.lower_1_std,
                  )}{" "}
                  –{" "}
                  {formatCurrency(
                    salary.standard_deviation_ranges.upper_1_std,
                  )}
                </strong>
              </div>

              <div className="detail-row">
                <span>2σ range</span>
                <strong>
                  {formatCurrency(
                    salary.standard_deviation_ranges.lower_2_std,
                  )}{" "}
                  –{" "}
                  {formatCurrency(
                    salary.standard_deviation_ranges.upper_2_std,
                  )}
                </strong>
              </div>
            </article>

            <article className="detail-card">
              <h3>Salary Coverage</h3>

              <div className="detail-row">
                <span>With minimum salary</span>
                <strong>{salary.salary_coverage.with_min_salary}</strong>
              </div>

              <div className="detail-row">
                <span>With maximum salary</span>
                <strong>{salary.salary_coverage.with_max_salary}</strong>
              </div>

              <div className="detail-row">
                <span>With midpoint salary</span>
                <strong>{salary.salary_coverage.with_midpoint_salary}</strong>
              </div>

              <div className="detail-row">
                <span>Complete salary range</span>
                <strong>{salary.salary_coverage.with_complete_range}</strong>
              </div>
            </article>

            <article className="detail-card">
              <h3>Outliers</h3>

              <div className="detail-row">
                <span>Total</span>
                <strong>{salary.outliers.total}</strong>
              </div>

              <div className="detail-row">
                <span>Lower</span>
                <strong>{salary.outliers.lower}</strong>
              </div>

              <div className="detail-row">
                <span>Upper</span>
                <strong>{salary.outliers.upper}</strong>
              </div>
            </article>
          </div>
        </section>
      )}

      <section className="dashboard-section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">JOB LISTINGS</p>
            <h2>Latest Jobs</h2>
          </div>

          <span className="section-count">{jobs.length} jobs</span>
        </div>

        {!jobs.length ? (
          <div className="empty-card">
            <p>No job listings were returned by the API.</p>
          </div>
        ) : (
          <div className="jobs-grid">
            {jobs.map((job) => (
              <article className="job-card" key={job.id}>
                <div className="job-card-header">
                  <div>
                    <h3>{job.title}</h3>
                    <p className="company">{job.company_name || "Unknown company"}</p>
                  </div>

                  {job.contract_time && (
                    <span className="job-tag">{job.contract_time}</span>
                  )}
                </div>

                <div className="job-meta">
                  <span>
                    {job.city || job.location_name || "Location unavailable"}
                  </span>

                  {job.category_label && (
                    <span>{job.category_label}</span>
                  )}
                </div>

                <div className="job-salary">
                  {job.normalized_salary_midpoint !== null &&
                  job.normalized_salary_midpoint !== undefined
                    ? formatCurrency(job.normalized_salary_midpoint)
                    : "Salary unavailable"}
                </div>

                <p className="job-description">
                  {job.description || "No description available."}
                </p>

                {job.redirect_url && (
                  <a
                    className="job-link"
                    href={job.redirect_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    View listing →
                  </a>
                )}
              </article>
            ))}
          </div>
        )}
      </section>

      <footer className="dashboard-footer">
        <span>Tech Job Analytics</span>

        {summary?.created_at && (
          <span>
            Analysis generated{" "}
            {new Date(summary.created_at).toLocaleString()}
          </span>
        )}
      </footer>
    </main>
  );
}

export default App;