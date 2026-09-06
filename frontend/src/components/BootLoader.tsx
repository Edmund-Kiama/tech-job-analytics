import { FiCloud, FiDatabase, FiZap } from 'react-icons/fi';

type BootLoaderProps = {
  error?: string | null;
};

export default function BootLoader({ error = null }: BootLoaderProps) {
  const hasError = Boolean(error);

  return (
    <main
      className={`boot-loader ${hasError ? 'boot-loader--error' : ''}`}
      role={hasError ? 'alert' : 'status'}
      aria-live="polite"
    >
      <div className="boot-loader__backdrop" aria-hidden="true">
        <span className="boot-loader__orbit boot-loader__orbit--one" />
        <span className="boot-loader__orbit boot-loader__orbit--two" />
        <span className="boot-loader__spark boot-loader__spark--one" />
        <span className="boot-loader__spark boot-loader__spark--two" />
        <span className="boot-loader__spark boot-loader__spark--three" />
      </div>

      <section className="boot-loader__content">
        <div className="boot-loader__mark" aria-hidden="true">
          <FiZap />
        </div>
        <p className="boot-loader__eyebrow">Career command center</p>
        {hasError ? (
          <>
            <h1>We could not wake the workspace</h1>
            <p className="boot-loader__message">
              The backend did not respond successfully. Reload the page to try
              connecting again.
            </p>
            <p className="boot-loader__error-detail">{error}</p>
            <button
              type="button"
              className="boot-loader__retry"
              onClick={() => window.location.reload()}
            >
              Reload and try again
            </button>
          </>
        ) : (
          <>
            <h1>Waking up your workspace</h1>
            <p className="boot-loader__message">
              The analytics service is starting for the first request. Free
              hosting can take a little longer to wake up, so your dashboard
              will appear as soon as the connection is ready.
            </p>

            <div className="boot-loader__status-list" aria-hidden="true">
              <div className="boot-loader__status-item">
                <span className="boot-loader__status-icon">
                  <FiCloud />
                </span>
                <span>Connecting to the service</span>
                <span className="boot-loader__dots">...</span>
              </div>
              <div className="boot-loader__status-item boot-loader__status-item--delayed">
                <span className="boot-loader__status-icon">
                  <FiDatabase />
                </span>
                <span>Preparing your latest data</span>
                <span className="boot-loader__dots">...</span>
              </div>
            </div>

            <span className="sr-only">Waiting for the backend to respond.</span>
          </>
        )}
      </section>
    </main>
  );
}
