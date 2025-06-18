/**
 * API通信ユーティリティ
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

class ApiClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    if (options.body && typeof options.body === 'object') {
      config.body = JSON.stringify(options.body);
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.message || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  get(endpoint, params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${endpoint}?${queryString}` : endpoint;
    return this.request(url, { method: 'GET' });
  }

  post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: data,
    });
  }

  put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: data,
    });
  }

  delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  }
}

export const api = new ApiClient();

// 特定のAPIエンドポイント用のヘルパー関数
export const raceApi = {
  getTodayRaces: () => api.get('/api/races/today'),
  getUpcomingRaces: () => api.get('/api/races/upcoming'),
  predict: (raceId, horses) => api.post('/api/predict', { race_id: raceId, horses }),
};

export const performanceApi = {
  getHistory: (days = 30, groupBy = 'daily') => 
    api.get('/api/performance/history', { days, groupBy }),
};

export const statusApi = {
  getStatus: () => api.get('/api/status'),
  poll: () => api.get('/api/status/poll'),
};