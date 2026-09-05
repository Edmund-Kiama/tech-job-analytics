import { useEffect, useState } from 'react';
import AppLayout from './components/AppLayout';
import useTheme from './hooks/useTheme';
import AnalyticsPage from './pages/AnalyticsPage';
import ApplicationsPage from './pages/ApplicationsPage';
import DashboardPage from './pages/DashboardPage';
import JobDetailPage from './pages/JobDetailPage';
import JobExplorerPage from './pages/JobExplorerPage';
import RecommendedJobsPage from './pages/RecommendedJobsPage';
import CategoriesPage from './pages/CategoriesPage';
import {
  CompaniesPage,
  DataHealthPage,
  FollowUpsPage,
  SettingsPage,
} from './pages/WorkspacePages';

const DEFAULT_SETTINGS = {
  defaultPageSize: '25',
  defaultSort: 'created_desc',
  showPredicted: true,
  refreshOnLoad: true,
  reminderWindow: '3',
};

function readSettings() {
  try {
    return {
      ...DEFAULT_SETTINGS,
      ...JSON.parse(localStorage.getItem('workspace-settings') || '{}'),
    };
  } catch {
    return DEFAULT_SETTINGS;
  }
}

function getRoute() {
  if (window.location.pathname === '/') {
    window.history.replaceState({}, '', '/dashboard');
  }

  const match = window.location.pathname.match(/^\/jobs\/([^/]+)\/?$/);
  return match
    ? { path: '/job-detail', jobId: decodeURIComponent(match[1]) }
    : { path: window.location.pathname || '/dashboard' };
}

export default function App() {
  const [theme, setTheme] = useTheme();
  const [route, setRoute] = useState(getRoute);
  const [settings, setSettings] = useState(readSettings);

  useEffect(() => {
    const handlePopState = () => setRoute(getRoute());
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  function navigate(path) {
    window.history.pushState({}, '', path);
    setRoute(getRoute());
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function updateSettings(name, value) {
    setSettings((current) => {
      const next = { ...current, [name]: value };
      localStorage.setItem('workspace-settings', JSON.stringify(next));
      return next;
    });
  }

  const activePath = route.path === '/job-detail' ? '/jobs' : route.path;
  const page =
    route.path === '/analytics/salary' ? (
      <AnalyticsPage key={route.path} section="salary" />
    ) : route.path === '/analytics/market' ? (
      <AnalyticsPage key={route.path} section="market" />
    ) : route.path === '/analytics/trends' ? (
      <AnalyticsPage key={route.path} section="trends" />
    ) : route.path === '/applications' ? (
      <ApplicationsPage />
    ) : route.path === '/recommended' ? (
      <RecommendedJobsPage
        onOpenJob={(job) => navigate(`/jobs/${encodeURIComponent(job.id)}`)}
      />
    ) : route.path === '/categories' ? (
      <CategoriesPage
        onOpenJob={(job) => navigate(`/jobs/${encodeURIComponent(job.id)}`)}
      />
    ) : route.path === '/companies' ? (
      <CompaniesPage />
    ) : route.path === '/follow-ups' ? (
      <FollowUpsPage />
    ) : route.path === '/data-health' ? (
      <DataHealthPage />
    ) : route.path === '/settings' ? (
      <SettingsPage settings={settings} updateSettings={updateSettings} />
    ) : route.path === '/jobs' ? (
      <JobExplorerPage
        onOpenJob={(job) => navigate(`/jobs/${encodeURIComponent(job.id)}`)}
      />
    ) : route.path === '/job-detail' ? (
      <JobDetailPage jobId={route.jobId} onBack={() => navigate('/jobs')} />
    ) : (
      <DashboardPage />
    );

  return (
    <AppLayout
      activePath={activePath}
      theme={theme}
      setTheme={setTheme}
      onNavigate={navigate}
    >
      {page}
    </AppLayout>
  );
}
