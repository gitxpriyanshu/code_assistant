/**
 * API service layer.
 * Centralises all HTTP calls to the FastAPI backend.
 */

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60s — LLM calls can be slow
});

/**
 * Submit code + error for debugging.
 * @param {{ code: string, error_message: string, language: string }} payload
 * @returns {Promise<{ explanation: string, fix: string, optimized_code: string, relevant_context: string[] }>}
 */
export async function debugCode(payload) {
  const response = await apiClient.post('/debug', payload);
  return response.data;
}

/**
 * Health check.
 * @returns {Promise<{ status: string, service: string, version: string }>}
 */
export async function healthCheck() {
  const response = await apiClient.get('/health');
  return response.data;
}

export default apiClient;
