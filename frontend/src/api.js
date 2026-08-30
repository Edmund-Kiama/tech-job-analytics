const API_BASE_URL = "http://127.0.0.1:8000";

async function fetchApi(endpoint) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`);

  if (!response.ok) {
    let message = `HTTP error: ${response.status}`;

    try {
      const errorData = await response.json();

      if (errorData.detail) {
        message = errorData.detail;
      }
    } catch {
      // Ignore JSON parsing errors and keep the HTTP error message.
    }

    throw new Error(message);
  }

  return response.json();
}

export async function getJobs() {
  return fetchApi("/jobs");
}

export async function getSalaryAnalytics() {
  return fetchApi("/analytics/salary");
}

export async function getAnalyticsSummary() {
  return fetchApi("/analytics/summary");
}