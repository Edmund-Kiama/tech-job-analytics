import { useState } from 'react';

const NAV_ITEMS = [
  { path: '/dashboard', label: 'Dashboard', icon: '▦' },
  { path: '/analytics/salary', label: 'Salary analytics', icon: '£' },
  { path: '/analytics/market', label: 'Market analysis', icon: '◫' },
  { path: '/analytics/trends', label: 'Market activity', icon: '↗' },
  { path: '/jobs', label: 'Job explorer', icon: '⌕' },
  { path: '/applications', label: 'Application tracker', icon: '✓' },
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
    <div className="min-h-screen bg-background text-foreground">
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
            {mobileOpen ? '×' : '☰'}
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
          <div className="border-b border-border p-6">
            <Brand />
          </div>
          <nav className="flex-1 p-4">
            <Navigation activePath={activePath} onNavigate={navigate} />
          </nav>
          <div className="border-t border-border p-4">
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
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-primary">
        UK job analytics
      </p>
      <p className="mt-2 text-lg font-bold tracking-tight">
        Career command center
      </p>
    </div>
  );
}

function Navigation({ activePath, onNavigate }) {
  return (
    <div className="space-y-1">
      {NAV_ITEMS.map((item) => {
        const active = activePath === item.path;
        return (
          <button
            key={item.path}
            type="button"
            onClick={() => onNavigate(item.path)}
            className={`flex w-full items-center gap-3 rounded-lg px-3 py-3 text-left text-sm font-medium transition ${active ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-muted hover:text-foreground'}`}
          >
            <span
              className="grid h-7 w-7 place-items-center rounded-md border border-current/20 text-base"
              aria-hidden="true"
            >
              {item.icon}
            </span>
            {item.label}
          </button>
        );
      })}
    </div>
  );
}

function ThemeSwitcher({ theme, setTheme }) {
  return (
    <div className="rounded-lg border border-border bg-background p-1">
      <p className="px-2 pb-1 pt-1 text-[10px] font-bold uppercase tracking-[0.16em] text-muted-foreground">
        Appearance
      </p>
      <div className="grid grid-cols-3 gap-1">
        {['light', 'dark', 'system'].map((option) => (
          <button
            key={option}
            type="button"
            aria-pressed={theme === option}
            onClick={() => setTheme(option)}
            className={`rounded-md px-2 py-1.5 text-xs font-medium capitalize ${theme === option ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-muted'}`}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}
