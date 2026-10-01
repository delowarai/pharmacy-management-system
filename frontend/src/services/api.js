const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export async function api(path, options = {}) {
  const token = localStorage.getItem('token');
  const isFormData = options.body instanceof FormData;
  const response = await fetch(API_URL + path, {
    ...options,
    headers: {
      ...(isFormData ? {} : {'Content-Type': 'application/json'}),
      ...(token ? {Authorization: `Bearer ${token}`} : {}),
      ...options.headers,
    },
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || 'Request failed');
  }
  return response.json();
}

export {API_URL};

