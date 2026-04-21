/**
 * API service layer.
 * Centralises all HTTP calls to the FastAPI backend.
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 120s — LLM calls can be slow and Render free tier needs time
});

/**
 * Submit code + error for debugging.
 */
export async function debugCode(payload) {
  const response = await apiClient.post('/debug', payload);
  let result = response.data;

  // Global Safety Parse: Catch cases where backend returns stringified JSON fields
  const safetyParse = (obj) => {
    if (!obj || typeof obj !== 'object') return obj;
    
    // If explanation is a JSON string, extract its fields
    const rawExp = obj.explanation;
    if (typeof rawExp === 'string' && (rawExp.trim().startsWith('{') || rawExp.includes('{'))) {
      try {
        // Attempt 1: Direct Parse
        let parsed;
        try {
          parsed = JSON.parse(rawExp);
        } catch {
          // Attempt 2: Boundary Extraction ({...})
          const match = rawExp.match(/(\{[\s\S]*\})/);
          if (match) parsed = JSON.parse(match[1]);
        }

        if (parsed) {
          if (parsed.explanation) obj.explanation = parsed.explanation;
          if (parsed.fix) obj.fix = parsed.fix;
          if (parsed.error_type) obj.error_type = parsed.error_type;
          if (parsed.confidence) obj.confidence = parsed.confidence;
          if (parsed.optimized_code) obj.optimized_code = parsed.optimized_code;
        }
      } catch { /* ignore final parse error */ }
    }
    return obj;
  };

  return safetyParse(result);
}

/**
 * Health check.
 * @returns {Promise<{ status: string, service: string, version: string }>}
 */
export async function healthCheck() {
  const response = await apiClient.get('/health');
  return response.data;
}

export const explainCode = async (data) => {
  const response = await apiClient.post("/explain", data);
  return response.data;
};

export default apiClient;
