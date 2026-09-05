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

const DEFAULT_PROFILE = {
  target_titles: '',
  preferred_locations: '',
  preferred_categories: '',
  preferred_contract_types: '',
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

function readProfile() {
  try {
    return {
      ...DEFAULT_PROFILE,
      ...JSON.parse(localStorage.getItem('job-profile') || '{}'),
    };
  } catch {
    return DEFAULT_PROFILE;
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
  const [profile, setProfile] = useState(readProfile);

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

  function updateProfile(nextProfile) {
    setProfile(nextProfile);
    localStorage.setItem('job-profile', JSON.stringify(nextProfile));
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
        profile={profile}
        onProfileSave={updateProfile}
        onOpenJob={(job) => navigate(`/jobs/${encodeURIComponent(job.id)}`)}
      />
    ) : route.path === '/categories' ? (
      <CategoriesPage
        onOpenJob={(job) => navigate(`/jobs/${encodeURIComponent(job.id)}`)}
      />
    ) : route.path === '/companies' ? (
      <CompaniesPage />
    ) : route.path === '/follow-ups' ? (
      <FollowUpsPage reminderWindow={settings.reminderWindow} />
    ) : route.path === '/data-health' ? (
      <DataHealthPage />
    ) : route.path === '/settings' ? (
      <SettingsPage
        settings={settings}
        updateSettings={updateSettings}
        profile={profile}
        onProfileSave={updateProfile}
      />
    ) : route.path === '/jobs' ? (
      <JobExplorerPage
        onOpenJob={(job) => navigate(`/jobs/${encodeURIComponent(job.id)}`)}
      />
    ) : route.path === '/job-detail' ? (
      <JobDetailPage jobId={route.jobId} onBack={() => navigate('/jobs')} />
    ) : (
      <DashboardPage
        onNavigate={navigate}
        refreshOnLoad={settings.refreshOnLoad}
      />
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
