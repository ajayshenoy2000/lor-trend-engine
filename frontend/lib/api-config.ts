// API configuration - use backend on 8000, frontend on 3002
export const API_BASE = typeof window !== 'undefined'
  ? `http://${window.location.hostname}:8000`
  : 'http://localhost:8000';
