// API client for FastAPI backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Log the API base URL on module load (for debugging)
if (typeof window !== 'undefined') {
  console.log('🔵 API Client initialized with base URL:', API_BASE_URL);
  console.log('🔵 NEXT_PUBLIC_API_URL env var:', process.env.NEXT_PUBLIC_API_URL || 'not set (using default)');
}

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
  
  console.log("🔵 fetchApi called:", { 
    url, 
    endpoint,
    apiBaseUrl: API_BASE_URL,
    method: options.method, 
    body: options.body 
  });
  
  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };

  // Add auth token if available
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`;
    console.log("✅ Token found, adding to headers (length:", token.length, ")");
  } else {
    console.warn("⚠️ No token found in localStorage");
  }

  console.log("Making fetch request to:", url, "with options:", {
    method: options.method,
    headers: defaultHeaders,
    body: options.body
  });
  
  let response: Response;
  try {
    response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });
    console.log("Fetch response received:", { status: response.status, statusText: response.statusText, ok: response.ok });
  } catch (fetchError) {
    console.error("Fetch error:", fetchError);
    throw fetchError;
  }

  if (!response.ok) {
    // Handle 401 Unauthorized - redirect to login
    if (response.status === 401) {
      // Clear invalid token
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        // Redirect to login page
        window.location.href = '/login';
      }
    }
    
    // Try to get error message from response body
    let errorMessage = `API error: ${response.statusText}`;
    try {
      const errorData = await response.clone().json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
    } catch {
      // If response isn't JSON, use status text
    }
    
    throw new ApiError(
      errorMessage,
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
    console.log("API.patch called with:", { endpoint, data });
    const response = await fetchApi(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
    console.log("API.patch response:", response);
    const json = await response.json();
    console.log("API.patch parsed JSON:", json);
    return json;
  },

  delete: async <T>(endpoint: string): Promise<T> => {
    const response = await fetchApi(endpoint, { method: 'DELETE' });
    return response.json();
  },
};

