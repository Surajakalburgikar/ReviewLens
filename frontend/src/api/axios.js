/**
 * API client configuration for ReviewLens.
 * Sets up pre-configured Axios instance to connect to the FastAPI backend.
 */
import axios from 'axios';

// Load base API URL from environment variables, fallback to local FastAPI development port
const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: `${baseURL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

export default apiClient;
