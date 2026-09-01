const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

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
      // Keep the HTTP error message.
    }

    throw new Error(message);
  }

  return response.json();
}

export async function getJobs(filters = {}) {
  const params = new URLSearchParams();

  if (filters.page) {
    params.set("page", filters.page);
  }

  if (filters.page_size) {
    params.set("page_size", filters.page_size);
  }

  if (filters.search) {
    params.set("search", filters.search);
  }

  if (filters.category) {
    params.set("category", filters.category);
  }

  if (filters.location) {
    params.set("location", filters.location);
  }

  if (filters.contract_time) {
    params.set("contract_time", filters.contract_time);
  }

  if (filters.contract_type) {
    params.set("contract_type", filters.contract_type);
  }

  if (filters.min_salary !== "") {
    params.set("min_salary", filters.min_salary);
  }

  if (filters.max_salary !== "") {
    params.set("max_salary", filters.max_salary);
  }

  if (filters.salary_predicted !== "") {
    params.set("salary_is_predicted", filters.salary_predicted);
  }

  if (filters.sort) {
    params.set("sort", filters.sort);
  }

  return fetchApi(`/jobs?${params.toString()}`);
}

export async function getSalaryAnalytics() {
  return fetchApi("/analytics/salary");
}

export async function getAnalyticsSummary() {
  return fetchApi("/analytics/summary");
}