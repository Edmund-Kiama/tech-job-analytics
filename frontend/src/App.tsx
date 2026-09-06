import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
} from 'react-router-dom';
import { Component, type ReactNode, useEffect, useState } from 'react';
import AppLayout from './components/AppLayout';
import BootLoader from './components/BootLoader';
import useTheme from './hooks/useTheme';
import { getHealth } from './api';
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

export default function App() {
  if (window.location.pathname === '/') {
    window.location.replace('/uk/dashboard');
    return null;
  }

  return (
    <BrowserRouter basename="/uk">
      <ErrorBoundary>
        <AppContent />
      </ErrorBoundary>
    </BrowserRouter>
  );
}

function AppContent() {
  const { jobId = '' } = useParams();
  const routerNavigate = useNavigate();
  const location = useLocation();
  const [theme, setTheme] = useTheme();
  const [backendReady, setBackendReady] = useState(false);
  const [backendError, setBackendError] = useState<string | null>(null);
  const [settings, setSettings] = useState(readSettings);
  const [profile, setProfile] = useState(readProfile);

  useEffect(() => {
    let cancelled = false;

    getHealth()
      .then(() => {
        if (!cancelled) {
          setBackendReady(true);
        }
      })
      .catch((loadError: unknown) => {
        if (!cancelled) {
          setBackendError(
            loadError instanceof Error
              ? loadError.message
              : 'The backend could not be reached.'
          );
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  if (!backendReady) {
    return <BootLoader error={backendError} />;
  }

  function navigate(path) {
    navigateTo(path);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function navigateTo(path) {
    routerNavigate(path);
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

  const routePath = location.pathname.replace(/^\/uk(?=\/|$)/, '') || '/';
  const activePath = routePath;

  return (
    <AppLayout
      activePath={activePath}
      theme={theme}
      setTheme={setTheme}
      onNavigate={navigate}
    >
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route
          path="/dashboard"
          element={
            <DashboardPage
              onNavigate={navigate}
              refreshOnLoad={settings.refreshOnLoad}
            />
          }
        />
        <Route
          path="/analytics/salary"
          element={<AnalyticsPage section="salary" />}
        />
        <Route
          path="/analytics/market"
          element={<AnalyticsPage section="market" />}
        />
        <Route
          path="/analytics/trends"
          element={<AnalyticsPage section="trends" />}
        />
        <Route
          path="/job/analytics/trends"
          element={<AnalyticsPage section="trends" />}
        />
        <Route path="/applications" element={<ApplicationsPage />} />
        <Route
          path="/recommended"
          element={
            <RecommendedJobsPage
              profile={profile}
              onProfileSave={updateProfile}
              onOpenJob={(job) =>
                navigate(`/jobs/${encodeURIComponent(job.id)}`)
              }
            />
          }
        />
        <Route
          path="/categories"
          element={
            <CategoriesPage
              onOpenJob={(job) =>
                navigate(`/jobs/${encodeURIComponent(job.id)}`)
              }
            />
          }
        />
        <Route path="/companies" element={<CompaniesPage />} />
        <Route
          path="/follow-ups"
          element={<FollowUpsPage reminderWindow={settings.reminderWindow} />}
        />
        <Route path="/data-health" element={<DataHealthPage />} />
        <Route
          path="/settings"
          element={
            <SettingsPage
              settings={settings}
              updateSettings={updateSettings}
              profile={profile}
              onProfileSave={updateProfile}
            />
          }
        />
        <Route
          path="/jobs"
          element={
            <JobExplorerPage
              onOpenJob={(job) =>
                navigate(`/jobs/${encodeURIComponent(job.id)}`)
              }
            />
          }
        />
        <Route
          path="/jobs/:jobId"
          element={
            <JobDetailPage
              jobId={decodeURIComponent(jobId)}
              onBack={() => navigate(-1)}
            />
          }
        />
        <Route path="/error" element={<ErrorPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </AppLayout>
  );
}

class ErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean; error: Error | null }
> {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return <ErrorPage error={this.state.error} />;
    }

    return this.props.children;
  }
}

function ErrorPage({ error = null }: { error?: Error | null }) {
  return (
    <StatusPage
      eyebrow="Something went wrong"
      title="This page hit an error."
      description={error?.message || 'The workspace could not load this page.'}
      actionLabel="Back to dashboard"
      onAction={() => window.location.replace('/uk/dashboard')}
    />
  );
}

function NotFoundPage() {
  return (
    <StatusPage
      eyebrow="404 / Not found"
      title="We could not find that page."
      description="The address may be outdated or the page may have moved."
      actionLabel="Back to dashboard"
      onAction={() => window.location.replace('/uk/dashboard')}
    />
  );
}

function StatusPage({ eyebrow, title, description, actionLabel, onAction }) {
  return (
    <section className="flex min-h-[60vh] items-center">
      <div className="max-w-2xl">
        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">
          {eyebrow}
        </p>
        <h1 className="mt-3 text-4xl font-semibold leading-tight sm:text-6xl">
          {title}
        </h1>
        <p className="mt-5 max-w-xl border-l-2 border-primary pl-4 text-muted-foreground">
          {description}
        </p>
        <button
          type="button"
          onClick={onAction}
          className="mt-8 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition hover:opacity-90"
        >
          {actionLabel}
        </button>
      </div>
    </section>
  );
}
