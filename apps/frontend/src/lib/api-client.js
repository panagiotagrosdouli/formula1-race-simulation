const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const DEMO_RESPONSES = {
  '/api/v1/health': {
    status: 'demo',
    service: 'APEX Race Engineering demo mode',
    demo: true,
  },
  '/api/v1/strategy/preview': {
    recommended_window_start: 22,
    recommended_window_end: 29,
    risk_label: 'medium',
    explanation:
      'Demo strategy model: tyre age is approaching the crossover region. A stop between laps 22 and 29 balances undercut potential, pit-loss exposure and hard-tyre raceability. Connect the FastAPI backend for live model outputs.',
    demo: true,
  },
  '/api/v1/simulations/monte-carlo': {
    runs: 2500,
    probabilities: [
      {
        driver_id: 'LEC',
        win_probability: 0.31,
        win_ci_lower: 0.28,
        win_ci_upper: 0.34,
        expected_finish_position: 2.4,
      },
      {
        driver_id: 'NOR',
        win_probability: 0.27,
        win_ci_lower: 0.24,
        win_ci_upper: 0.3,
        expected_finish_position: 2.8,
      },
      {
        driver_id: 'VER',
        win_probability: 0.22,
        win_ci_lower: 0.19,
        win_ci_upper: 0.25,
        expected_finish_position: 3.1,
      },
      {
        driver_id: 'PIA',
        win_probability: 0.13,
        win_ci_lower: 0.1,
        win_ci_upper: 0.16,
        expected_finish_position: 4.2,
      },
      {
        driver_id: 'HAM',
        win_probability: 0.07,
        win_ci_lower: 0.05,
        win_ci_upper: 0.1,
        expected_finish_position: 5.0,
      },
    ],
    assumptions: [
      'Demo data only: no private team telemetry is used.',
      'Monte Carlo samples model pace uncertainty, tyre degradation and pit-loss exposure.',
      'Connect VITE_API_BASE_URL to the FastAPI backend for live calculations.',
    ],
    demo: true,
  },
};

async function request(path, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API request failed ${response.status}: ${await response.text()}`);
    }

    return response.json();
  } catch (error) {
    if (DEMO_RESPONSES[path]) {
      return DEMO_RESPONSES[path];
    }
    throw error;
  }
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
