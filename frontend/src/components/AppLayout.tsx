import { useState } from 'react';
import {
  FiBarChart2,
  FiBriefcase,
  FiDatabase,
  FiGrid,
  FiMenu,
  FiPieChart,
  FiSearch,
  FiSettings,
  FiStar,
  FiTarget,
  FiTrendingUp,
  FiUsers,
  FiX,
  FiClock,
} from 'react-icons/fi';

const NAV_SECTIONS = [
  {
    label: 'Overview',
    items: [{ path: '/dashboard', label: 'Dashboard', icon: FiGrid }],
  },
  {
    label: 'Find jobs',
    items: [
      { path: '/recommended', label: 'Recommended jobs', icon: FiStar },
      { path: '/jobs', label: 'Job explorer', icon: FiSearch },
      { path: '/categories', label: 'Categories', icon: FiPieChart },
      { path: '/companies', label: 'Companies', icon: FiUsers },
    ],
  },
  {
    label: 'Application workspace',
    items: [
      { path: '/applications', label: 'Applications', icon: FiBriefcase },
      { path: '/follow-ups', label: 'Follow-ups', icon: FiClock },
    ],
  },
  {
    label: 'Analytics',
    items: [
      {
        path: '/analytics/salary',
        label: 'Salary analytics',
        icon: FiBarChart2,
      },
      { path: '/analytics/market', label: 'Market analysis', icon: FiTarget },
      {
        path: '/analytics/trends',
        label: 'Market activity',
        icon: FiTrendingUp,
      },
    ],
  },
  {
    label: 'System',
    items: [
      { path: '/data-health', label: 'Data health', icon: FiDatabase },
      { path: '/settings', label: 'Settings', icon: FiSettings },
    ],
  },
];

export default function AppLayout({
  activePath,
  theme,
  setTheme,
  children,
  onNavigate,
}) {
  const [mobileOpen, setMobileOpen] = useState(false);

  function navigate(path) {
    onNavigate(path);
    setMobileOpen(false);
  }

  return (
    <div className="app-shell min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-20 border-b border-border bg-card/95 backdrop-blur lg:hidden">
        <div className="flex h-16 items-center justify-between px-4">
          <Brand />
          <button
            type="button"
            aria-label="Open navigation"
            aria-expanded={mobileOpen}
            onClick={() => setMobileOpen((open) => !open)}
            className="rounded-lg border border-border px-3 py-2 text-lg hover:bg-muted"
          >
            {mobileOpen ? (
              <FiX aria-hidden="true" />
            ) : (
              <FiMenu aria-hidden="true" />
            )}
          </button>
        </div>
        {mobileOpen && (
          <nav className="border-t border-border px-3 py-3">
            <Navigation activePath={activePath} onNavigate={navigate} />
          </nav>
        )}
      </header>

      <div className="flex min-h-screen">
        <aside className="sticky top-0 hidden h-screen max-h-screen w-64 shrink-0 overflow-y-auto border-r border-border bg-card lg:flex lg:flex-col">
          <div className="border-b border-border px-4 py-4">
            <Brand />
          </div>
          <nav className="flex-1 px-3 py-4">
            <Navigation activePath={activePath} onNavigate={navigate} />
          </nav>
          <div className="border-t border-border p-3">
            <ThemeSwitcher theme={theme} setTheme={setTheme} />
          </div>
        </aside>

        <main className="min-w-0 flex-1">
          <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-10 lg:py-10">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

function Brand() {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-primary">
        UK job analytics
      </p>
      <p className="mt-2 text-lg font-semibold leading-tight tracking-[-0.02em]">
        Career command center
      </p>
    </div>
  );
}

function Navigation({ activePath, onNavigate }) {
  return (
    <div className="space-y-3 flex flex-col h-full justify-between">
      {NAV_SECTIONS.map((section) => (
        <section key={section.label}>
          <p className="mb-1 px-2 text-xs font-bold uppercase tracking-[0.14em] text-muted-foreground">
            {section.label}
          </p>
          <div className="space-y-0.5">
            {section.items.map((item) => {
              const active = activePath === item.path;
              return (
                <button
                  key={item.path}
                  type="button"
                  onClick={() => onNavigate(item.path)}
                  className={`nav-item flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left text-xs font-medium transition ${active ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}`}
                >
                  <item.icon aria-hidden="true" />
                  {/* <span
                    className="grid h-6 w-6 place-items-center rounded-md border border-current/20 text-sm"
                    aria-hidden="true"
                  >
                  </span> */}
                  {item.label}
                </button>
              );
            })}
          </div>
        </section>
      ))}
    </div>
  );
}

function ThemeSwitcher({ theme, setTheme }) {
  return (
    <div className="rounded-lg border border-border bg-background p-1">
      <p className="px-2 pb-1 text-[9px] font-bold uppercase tracking-[0.14em] text-muted-foreground">
        Appearance
      </p>
      <div className="grid grid-cols-3 gap-1">
        {['light', 'dark', 'system'].map((option) => (
          <button
            key={option}
            type="button"
            aria-pressed={theme === option}
            onClick={() => setTheme(option)}
            className={`rounded-md px-1.5 py-1 text-[11px] font-medium capitalize ${theme === option ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-muted'}`}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}
