import { useEffect, useState } from 'react';
import AppLayout from './components/AppLayout';
import useTheme from './hooks/useTheme';
import AnalyticsPage from './pages/AnalyticsPage';
import ApplicationsPage from './pages/ApplicationsPage';
import DashboardPage from './pages/DashboardPage';
import JobDetailPage from './pages/JobDetailPage';
import JobExplorerPage from './pages/JobExplorerPage';

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

  const activePath = route.path === '/job-detail' ? '/jobs' : route.path;
  const page =
    route.path === '/analytics/salary' ? (
      <AnalyticsPage section="salary" />
    ) : route.path === '/analytics/market' ? (
      <AnalyticsPage section="market" />
    ) : route.path === '/analytics/trends' ? (
      <AnalyticsPage section="trends" />
    ) : route.path === '/applications' ? (
      <ApplicationsPage />
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
