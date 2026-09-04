import { useEffect, useState } from 'react';
import {
  getAnalyticsBreakdown,
  getAnalyticsMetadata,
  getAnalyticsSummary,
  getAnalyticsTrends,
  getSalaryAnalytics,
  getSalaryDistribution,
} from '../api';
import PageIntro from '../components/PageIntro';
import Loader from '../components/Loader';
import Panel from '../components/Panel';
import {
  CategoryAnalytics,
  ContractTimeAnalytics,
  ContractTypeAnalytics,
  MarketTrends,
  LocationAnalytics,
  SalaryCoverage,
  SalaryDistributionPanel,
  SalaryPredictionAnalytics,
  SalaryStatistics,
  TopSalaryJobs,
} from '../components/dashboard/DashboardAnalytics';

const SECTION_DETAILS = {
  salary: {
    eyebrow: 'Compensation intelligence',
    title: 'Salary analytics',
    description:
      'Explore salary distributions, coverage, and the highest-paying listings.',
  },
  market: {
    eyebrow: 'Market structure',
    title: 'Market analysis',
    description:
      'Compare the categories, locations, and contract patterns shaping the market.',
  },
  trends: {
    eyebrow: 'Market activity',
    title: 'Market trends',
    description:
      'Track job additions, inactivations, and active listings over time.',
  },
};

export default function AnalyticsPage({ section }) {
  const [data, setData] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [distribution, setDistribution] = useState(null);
  const [loading, setLoading] = useState(true);
  const [distributionLoading, setDistributionLoading] = useState(false);
  const [error, setError] = useState(null);
  const [distributionError, setDistributionError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    const requests =
      section === 'salary'
        ? [
            getSalaryAnalytics(),
            getAnalyticsSummary(),
            getAnalyticsMetadata(),
            getAnalyticsBreakdown(),
          ]
        : section === 'market'
          ? [getAnalyticsBreakdown()]
          : [getAnalyticsTrends()];

    Promise.all(requests)
      .then((responses) => {
        if (cancelled) return;
        setData(
          section === 'salary'
            ? {
                salary: responses[0],
                summary: responses[1],
                metadata: responses[2],
                breakdown: responses[3],
              }
            : section === 'market'
              ? { breakdown: responses[0] }
              : { trends: responses[0] }
        );
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
  }, [section]);

  useEffect(() => {
    if (section !== 'salary') return undefined;
    let cancelled = false;
    getSalaryDistribution(selectedCategory || null)
      .then((result) => {
        if (cancelled) return;
        setDistributionError(null);
        setDistribution(result);
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
  }, [section, selectedCategory]);

  const details = SECTION_DETAILS[section] || SECTION_DETAILS.salary;

  return (
    <div>
      <PageIntro {...details} />
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
      {data &&
        !error &&
        (section === 'salary' ? (
          <SalaryContent
            data={data}
            selectedCategory={selectedCategory}
            onCategoryChange={setSelectedCategory}
            distribution={distribution}
            distributionLoading={distributionLoading}
            distributionError={distributionError}
          />
        ) : section === 'market' ? (
          <MarketContent breakdown={data.breakdown} />
        ) : (
          <MarketTrends data={data.trends.daily || []} />
        ))}
    </div>
  );
}

function SalaryContent({
  data,
  selectedCategory,
  onCategoryChange,
  distribution,
  distributionLoading,
  distributionError,
}) {
  const { salary, summary, metadata, breakdown } = data;
  return (
    <div className="space-y-6">
      <SalaryDistributionPanel
        categories={metadata.categories || []}
        selectedCategory={selectedCategory}
        onCategoryChange={onCategoryChange}
        distribution={distribution}
        loading={distributionLoading}
        error={distributionError}
      />
      <section className="grid gap-6 xl:grid-cols-2">
        <SalaryStatistics salary={salary} />
        <SalaryCoverage salary={salary} totalJobs={summary.job_count} />
      </section>
      <TopSalaryJobs jobs={breakdown.top_salary_jobs || []} />
    </div>
  );
}

function MarketContent({ breakdown }) {
  return (
    <div className="space-y-6">
      <CategoryAnalytics categories={breakdown.top_categories || []} />
      <LocationAnalytics locations={breakdown.top_locations || []} />
      <section className="grid gap-6 xl:grid-cols-3">
        <ContractTimeAnalytics data={breakdown.contract_time || []} />
        <ContractTypeAnalytics data={breakdown.contract_type || []} />
        <SalaryPredictionAnalytics data={breakdown.salary_prediction || []} />
      </section>
    </div>
  );
}
