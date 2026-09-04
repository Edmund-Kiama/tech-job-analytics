import { useEffect, useState } from 'react';
import { getJobApplication, updateJobApplication } from '../api';
import Loader from './Loader';

const STATUSES = [
  'NEW',
  'SAVED',
  'APPLIED',
  'INTERVIEW',
  'OFFER',
  'REJECTED',
  'ARCHIVED',
];

const PRIORITIES = [
  { value: 1, label: 'Low' },
  { value: 2, label: 'Medium' },
  { value: 3, label: 'High' },
];

function formatDate(value) {
  if (!value) {
    return '—';
  }

  return new Date(value).toLocaleDateString();
}

export default function ApplicationTracker({ job, onUpdated }) {
  const [application, setApplication] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [notes, setNotes] = useState('');
  const [followUp, setFollowUp] = useState('');

  useEffect(() => {
    async function loadApplication() {
      try {
        setLoading(true);
        setError(null);

        const data = await getJobApplication(job.id);

        setApplication(data);
        setNotes(data.application_notes || '');

        if (data.follow_up_at) {
          setFollowUp(new Date(data.follow_up_at).toISOString().slice(0, 10));
        } else {
          setFollowUp('');
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadApplication();
  }, [job.id]);

  async function updateApplication(updates) {
    try {
      setSaving(true);
      setError(null);

      const updated = await updateJobApplication(job.id, updates);

      setApplication(updated);

      if (onUpdated) {
        onUpdated(updated);
      }

      return updated;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setSaving(false);
    }
  }

  async function handleStatusChange(event) {
    await updateApplication({
      application_status: event.target.value,
    });
  }

  async function handlePriorityChange(event) {
    const value = event.target.value;

    await updateApplication({
      user_priority: value ? Number(value) : null,
    });
  }

  async function saveNotes() {
    await updateApplication({
      application_notes: notes,
    });
  }

  async function saveFollowUp() {
    await updateApplication({
      follow_up_at: followUp ? `${followUp}T09:00:00` : null,
    });
  }

  if (loading) {
    return (
      <div className="rounded-xl border bg-card">
        <Loader label="Loading application tracker..." />
      </div>
    );
  }

  if (!application) {
    return null;
  }

  return (
    <section className="rounded-xl border bg-card p-5">
      <div className="mb-5">
        <h2 className="text-lg font-semibold">Application Tracker</h2>

        <p className="mt-1 text-sm text-muted-foreground">
          Track your progress for this job.
        </p>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <label className="mb-2 block text-sm font-medium">Status</label>

          <select
            value={application.application_status}
            onChange={handleStatusChange}
            disabled={saving}
            className="w-full rounded-lg border bg-background px-3 py-2 text-sm"
          >
            {STATUSES.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium">Priority</label>

          <select
            value={application.user_priority || ''}
            onChange={handlePriorityChange}
            disabled={saving}
            className="w-full rounded-lg border bg-background px-3 py-2 text-sm"
          >
            <option value="">No priority</option>

            {PRIORITIES.map((priority) => (
              <option key={priority.value} value={priority.value}>
                {priority.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <div className="rounded-lg border p-4">
          <p className="text-xs text-muted-foreground">Saved</p>

          <p className="mt-1 text-sm font-medium">
            {formatDate(application.saved_at)}
          </p>
        </div>

        <div className="rounded-lg border p-4">
          <p className="text-xs text-muted-foreground">Applied</p>

          <p className="mt-1 text-sm font-medium">
            {formatDate(application.applied_at)}
          </p>
        </div>
      </div>

      <div className="mt-5">
        <label className="mb-2 block text-sm font-medium">Follow-up date</label>

        <div className="flex gap-2">
          <input
            type="date"
            value={followUp}
            onChange={(event) => setFollowUp(event.target.value)}
            className="flex-1 rounded-lg border bg-background px-3 py-2 text-sm"
          />

          <button
            type="button"
            onClick={saveFollowUp}
            disabled={saving}
            className="rounded-lg border px-4 py-2 text-sm font-medium hover:bg-muted disabled:opacity-50"
          >
            Save
          </button>
        </div>
      </div>

      <div className="mt-5">
        <label className="mb-2 block text-sm font-medium">Notes</label>

        <textarea
          value={notes}
          onChange={(event) => setNotes(event.target.value)}
          rows={4}
          placeholder="Add notes about this application..."
          className="w-full resize-y rounded-lg border bg-background px-3 py-2 text-sm"
        />

        <button
          type="button"
          onClick={saveNotes}
          disabled={saving}
          className="mt-2 rounded-lg border px-4 py-2 text-sm font-medium hover:bg-muted disabled:opacity-50"
        >
          Save notes
        </button>
      </div>
    </section>
  );
}
