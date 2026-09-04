import { useState } from 'react';
import { updateJobApplication } from '../api';

export default function JobApplicationActions({ job, onUpdated }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const status = job.application_status || 'NEW';

  async function updateStatus(application_status) {
    try {
      setLoading(true);
      setError(null);

      const updated = await updateJobApplication(job.id, {
        application_status,
      });

      if (onUpdated) {
        onUpdated(updated);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleApply() {
    if (!job.redirect_url) {
      setError('This job does not have an application URL.');
      return;
    }

    window.open(job.redirect_url, '_blank', 'noopener,noreferrer');
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          disabled={loading}
          onClick={() => updateStatus('SAVED')}
          className="rounded-lg border px-4 py-2 text-sm font-medium hover:bg-muted disabled:opacity-50"
        >
          {status === 'SAVED' ? 'Saved' : 'Save'}
        </button>

        <button
          type="button"
          onClick={handleApply}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90"
        >
          Apply
        </button>

        <button
          type="button"
          disabled={loading}
          onClick={() => updateStatus('APPLIED')}
          className="rounded-lg border px-4 py-2 text-sm font-medium hover:bg-muted disabled:opacity-50"
        >
          Mark as Applied
        </button>

        <button
          type="button"
          disabled={loading}
          onClick={() => updateStatus('INTERVIEW')}
          className="rounded-lg border px-4 py-2 text-sm font-medium hover:bg-muted disabled:opacity-50"
        >
          Interview
        </button>

        <button
          type="button"
          disabled={loading}
          onClick={() => updateStatus('REJECTED')}
          className="rounded-lg border px-4 py-2 text-sm font-medium hover:bg-muted disabled:opacity-50"
        >
          Reject
        </button>

        <button
          type="button"
          disabled={loading}
          onClick={() => updateStatus('ARCHIVED')}
          className="rounded-lg border px-4 py-2 text-sm font-medium hover:bg-muted disabled:opacity-50"
        >
          Archive
        </button>
      </div>

      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  );
}
