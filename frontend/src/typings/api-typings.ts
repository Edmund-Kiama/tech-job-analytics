export type Theme = 'light' | 'dark' | 'system';

export type ApplicationStatus =
  'NEW' | 'SAVED' | 'APPLIED' | 'INTERVIEW' | 'OFFER' | 'REJECTED' | 'ARCHIVED';

export interface Job {
  id: string;
  title: string;
  company_name?: string | null;
  category_label?: string | null;
  location_name?: string | null;
  city?: string | null;
  contract_time?: string | null;
  contract_type?: string | null;
  salary_min?: number | null;
  salary_max?: number | null;
  is_active?: boolean;
  description?: string | null;
  first_seen_at?: string | null;
  last_seen_at?: string | null;
  redirect_url?: string | null;
  application_status?: ApplicationStatus | null;
  user_priority?: number | null;
  application_notes?: string | null;
  saved_at?: string | null;
  applied_at?: string | null;
  follow_up_at?: string | null;
}

export interface JobFilters {
  search: string;
  category: string;
  location: string;
  contract_time: string;
  contract_type: string;
  min_salary: string;
  max_salary: string;
  salary_predicted: string;
  sort: string;
  page: number;
  page_size: number;
}

export interface Pagination {
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface JobsResponse {
  items: Job[];
  pagination: Pagination;
}

export interface ApplicationUpdate {
  application_status?: ApplicationStatus;
  user_priority?: number | null;
  application_notes?: string;
  follow_up_at?: string | null;
}

export interface ApiApplication extends Job {
  application_status: ApplicationStatus;
}

export interface ApiErrorDetail {
  msg: string;
}

export interface SalaryStatistics {
  minimum: number;
  q1: number;
  median: number;
  mean: number;
  q3: number;
  maximum: number;
  iqr: number;
  standard_deviation: number;
}

export interface SalaryAnalytics {
  distribution: SalaryStatistics;
  standard_deviation_ranges: {
    lower_1_std: number;
    upper_1_std: number;
    lower_2_std: number;
    upper_2_std: number;
  };
  salary_coverage: {
    with_min_salary: number;
    with_max_salary: number;
    with_midpoint_salary: number;
    with_complete_range: number;
  };
}

export interface AnalyticsSummary {
  job_count: number;
  salary_count: number;
  mean_salary: number;
  median_salary: number;
}

export interface CategoryAnalytics {
  category: string;
  job_count: number;
  mean_salary: number;
  median_salary: number;
}

export interface CountAnalytics {
  [key: string]: string | number;
}

export interface AnalyticsBreakdown {
  job_status?: { active?: number; inactive?: number };
  top_categories?: CategoryAnalytics[];
  top_locations?: CountAnalytics[];
  contract_time?: CountAnalytics[];
  contract_type?: CountAnalytics[];
  salary_prediction?: CountAnalytics[];
  top_salary_jobs?: Job[];
}

export interface AnalyticsMetadata {
  categories: string[];
}

export interface TrendPoint {
  date: string;
  [key: string]: string | number;
}

export interface AnalyticsTrends {
  daily: TrendPoint[];
}

export interface SalaryBin {
  label: string;
  count: number;
}

export interface SalaryDistribution {
  bins: SalaryBin[];
  statistics: SalaryStatistics;
  outliers: { total: number; lower: number; upper: number };
  job_count: number;
}
