/**
 * API Configuration
 * Reads configuration from environment variables
 */

// Get API base URL from environment variables
// In Vite, environment variables must be prefixed with VITE_
const getApiBaseUrl = () => {
  // Primary: Read from VITE_BACKEND_URL (matches your existing BACKEND_URL pattern)
  if (import.meta.env.VITE_BACKEND_URL) {
    return import.meta.env.VITE_BACKEND_URL;
  }
  
  // Fallback naming conventions
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // Development fallback
  return 'http://localhost:8000';
};

// API Configuration object
export const apiConfig = {
  baseUrl: getApiBaseUrl(),
  
  // API endpoints
  endpoints: {
    // Resume endpoints
    uploadResume: '/resume/upload',
    analyzeResumeVsJob: '/resume/analyze-vs-job',
    scoreResumeStandalone: '/resume/score-standalone',
    
    // Resume Builder endpoints
    resumeBuilderTemplates: '/resume-builder/templates',
    resumeBuilderTemplate: '/resume-builder/templates',
    resumeBuilderTemplateImage: '/resume-builder/templates',
    resumeBuilderBuild: '/resume-builder/build',
    resumeBuilderGeneratePdf: '/resume-builder/generate-pdf',
    
    // Job endpoints
    searchJobs: '/jobs/search',
    fetchJobDescription: '/jobs/fetch-description',
    testJobScraper: '/jobs/test-scraper',
    
    // Session endpoints
    getSession: '/sessions',
    deleteSession: '/sessions',
    
    // Health endpoints
    health: '/health',
    healthDetailed: '/health/detailed'
  }
};

// Helper function to build full API URLs
export const buildApiUrl = (endpoint) => {
  const baseUrl = apiConfig.baseUrl.replace(/\/$/, ''); // Remove trailing slash
  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${baseUrl}${path}`;
};

// Helper function for making API requests with proper error handling
export const apiRequest = async (endpoint, options = {}) => {
  const url = buildApiUrl(endpoint);
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        // Add any default headers here
        ...options.headers,
      },
    });
    
    return response;
  } catch (error) {
    console.error(`API request failed for ${endpoint}:`, error);
    throw error;
  }
};

// Export individual endpoint builders for convenience
export const API_ENDPOINTS = {
  uploadResume: () => buildApiUrl(apiConfig.endpoints.uploadResume),
  analyzeResumeVsJob: () => buildApiUrl(apiConfig.endpoints.analyzeResumeVsJob),
  scoreResumeStandalone: () => buildApiUrl(apiConfig.endpoints.scoreResumeStandalone),
  analyzeResume: (sessionId) => buildApiUrl(`${apiConfig.endpoints.scoreResumeStandalone}?session_id=${sessionId}`),
  
  // Resume Builder endpoints
  resumeBuilderTemplates: () => buildApiUrl(apiConfig.endpoints.resumeBuilderTemplates),
  resumeBuilderTemplate: (templateId) => buildApiUrl(`${apiConfig.endpoints.resumeBuilderTemplate}/${templateId}`),
  resumeBuilderTemplateImage: (templateId) => buildApiUrl(`${apiConfig.endpoints.resumeBuilderTemplateImage}/${templateId}/image`),
  resumeBuilderBuild: () => buildApiUrl(apiConfig.endpoints.resumeBuilderBuild),
  resumeBuilderGeneratePdf: () => buildApiUrl(apiConfig.endpoints.resumeBuilderGeneratePdf),
  
  searchJobs: () => buildApiUrl(apiConfig.endpoints.searchJobs),
  fetchJobDescription: () => buildApiUrl(apiConfig.endpoints.fetchJobDescription),
  testJobScraper: () => buildApiUrl(apiConfig.endpoints.testJobScraper),
  getSession: (sessionId) => buildApiUrl(`${apiConfig.endpoints.getSession}/${sessionId}`),
  deleteSession: (sessionId) => buildApiUrl(`${apiConfig.endpoints.deleteSession}/${sessionId}`),
  health: () => buildApiUrl(apiConfig.endpoints.health),
  healthDetailed: () => buildApiUrl(apiConfig.endpoints.healthDetailed),
};

// Log configuration in development
if (import.meta.env.DEV) {
  // Determine which env variable was used
  let envSource = 'fallback (http://localhost:8000)';
  if (import.meta.env.VITE_BACKEND_URL) {
    envSource = 'VITE_BACKEND_URL';
  } else if (import.meta.env.VITE_API_BASE_URL) {
    envSource = 'VITE_API_BASE_URL';
  }
  
  console.log('🔧 API Configuration:', {
    baseUrl: apiConfig.baseUrl,
    source: envSource,
    mode: import.meta.env.MODE,
    endpoints: Object.keys(apiConfig.endpoints),
    availableEnvVars: {
      VITE_BACKEND_URL: import.meta.env.VITE_BACKEND_URL || 'not set',
      VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'not set'
    }
  });
} 