import DashboardAnalytics from '../components/dashboard/DashboardAnalytics';

export default function DashboardPage({ onNavigate, refreshOnLoad }) {
  return (
    <DashboardAnalytics onNavigate={onNavigate} refreshOnLoad={refreshOnLoad} />
  );
}
