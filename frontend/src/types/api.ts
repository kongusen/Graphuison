export interface APIError {
  detail: string;
  code?: string;
  status?: number;
}

export interface APIResponse<T> {
  data: T;
  error?: APIError;
} 