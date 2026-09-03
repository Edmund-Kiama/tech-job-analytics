const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// async function fetchApi(endpoint) {
//   const response = await fetch(`${API_BASE_URL}${endpoint}`);

//   if (!response.ok) {
//     let message = `HTTP error: ${response.status}`;

//     try {
//       const errorData = await response.json();

//       if (errorData.detail) {
//         message = errorData.detail;
//       }
//     } catch {
//       // Keep the HTTP error message.
//     }

//     throw new Error(message);
//   }

//   return response.json();
// }

async function fetchApi(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let message = `HTTP error: ${response.status}`;

    try {
      const errorData = await response.json();

      if (errorData.detail) {
        if (Array.isArray(errorData.detail)) {
          message = errorData.detail.map((item) => item.msg).join(', ');
        } else {
          message = errorData.detail;
        }
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
    params.set('page', filters.page);
  }

  if (filters.page_size) {
    params.set('page_size', filters.page_size);
  }

  if (filters.search) {
    params.set('search', filters.search);
  }

  if (filters.category) {
    params.set('category', filters.category);
  }

  if (filters.location) {
    params.set('location', filters.location);
  }

  if (filters.contract_time) {
    params.set('contract_time', filters.contract_time);
  }

  if (filters.contract_type) {
    params.set('contract_type', filters.contract_type);
  }

  if (filters.min_salary !== '') {
    params.set('min_salary', filters.min_salary);
  }

  if (filters.max_salary !== '') {
    params.set('max_salary', filters.max_salary);
  }

  if (filters.salary_predicted !== '') {
    params.set('salary_is_predicted', filters.salary_predicted);
  }

  if (filters.sort) {
    params.set('sort', filters.sort);
  }

  return fetchApi(`/jobs?${params.toString()}`);
}

export async function getJob(jobId) {
  return fetchApi(`/jobs/${encodeURIComponent(jobId)}`);
}

export async function getSalaryAnalytics() {
  return fetchApi('/analytics/salary');
}

export async function getAnalyticsMetadata() {
  return fetchApi('/analytics/metadata');
}

export async function getAnalyticsBreakdown() {
  return fetchApi('/analytics/breakdown');
}

export async function getAnalyticsTrends() {
  return fetchApi('/analytics/trends');
}

export async function getAnalyticsSummary() {
  return fetchApi('/analytics/summary');
}

export async function getJobApplication(jobId) {
  return fetchApi(`/jobs/${jobId}/application`);
}

export async function updateJobApplication(jobId, updates) {
  return fetchApi(`/jobs/${jobId}/application`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}

export async function getApplications(status = null, priority = null) {
  const params = new URLSearchParams();

  if (status) {
    params.set('status', status);
  }

  if (priority !== null && priority !== undefined) {
    params.set('priority', priority);
  }

  const query = params.toString();

  return fetchApi(query ? `/applications?${query}` : '/applications');
}

export async function getSalaryDistribution(category = null) {
  const params = new URLSearchParams();

  if (category) {
    params.set('category', category);
  }

  const query = params.toString();

  return fetchApi(
    query
      ? `/analytics/salary/distribution?${query}`
      : '/analytics/salary/distribution'
  );
}
