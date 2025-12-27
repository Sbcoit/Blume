// API client for FastAPI backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public response?: Response
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };

  // Add auth token if available
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(
      `API error: ${response.statusText}`,
      response.status,
      response
    );
  }

  return response;
}

export const api = {
  get: async <T>(endpoint: string): Promise<T> => {
    const response = await fetchApi(endpoint, { method: 'GET' });
    return response.json();
  },

  post: async <T>(endpoint: string, data?: unknown): Promise<T> => {
    const response = await fetchApi(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
    return response.json();
  },

  patch: async <T>(endpoint: string, data?: unknown): Promise<T> => {
    const response = await fetchApi(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
    return response.json();
  },

  delete: async <T>(endpoint: string): Promise<T> => {
    const response = await fetchApi(endpoint, { method: 'DELETE' });
    return response.json();
  },
};

