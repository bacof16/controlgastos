
export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  status: number;
}

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
  try {
    const res = await fetch(`/api${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    const data = await res.json();

    if (!res.ok) {
        return {
            error: data.detail || 'Error en la petición',
            status: res.status
        };
    }

    return { data, status: res.status };
  } catch (error) {
    return {
        error: error instanceof Error ? error.message : 'Error de red',
        status: 500
    };
  }
}
