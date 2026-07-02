const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`API request failed ${response.status}: ${body}`);
  }

  return response.json();
}

export function getHealth() {
  return request('/api/v1/health');
}

export function previewStrategy(payload = {}) {
  return request('/api/v1/strategy/preview', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function runMonteCarloSimulation(payload = {}) {
  return request('/api/v1/simulations/monte-carlo', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
