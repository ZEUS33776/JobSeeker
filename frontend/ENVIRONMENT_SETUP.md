# Environment Setup Guide

## Overview

The JobSeeker frontend uses environment variables to configure the backend API URL and other settings. This ensures the application can work in different environments (development, staging, production) without code changes.

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_BACKEND_URL` | Backend API base URL | `http://localhost:8000` |

### Optional Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `VITE_API_BASE_URL` | Alternative name for backend URL | `http://localhost:8000` | `https://api.jobseeker.com` |
| `VITE_APP_NAME` | Application name | `JobSeeker` | `JobSeeker Pro` |
| `VITE_APP_VERSION` | Application version | `1.0.0` | `2.1.0` |

## Setup Instructions

### 1. Create Environment File

Copy the example file and modify it for your environment:

```bash
# In the frontend directory
cp src/config/env.example .env
```

### 2. Configure Variables

Edit the `.env` file with your settings:

```bash
# Development (default)
VITE_BACKEND_URL=http://localhost:8000

# Production example
# VITE_BACKEND_URL=https://your-api-domain.com

# Optional settings
VITE_APP_NAME=JobSeeker
VITE_APP_VERSION=1.0.0
```

### 3. Restart Development Server

After changing environment variables, restart the Vite development server:

```bash
npm run dev
```

## Environment-Specific Configurations

### Development
```bash
VITE_BACKEND_URL=http://localhost:8000
```

### Staging
```bash
VITE_BACKEND_URL=https://staging-api.jobseeker.com
```

### Production
```bash
VITE_BACKEND_URL=https://api.jobseeker.com
```

## How It Works

### 1. Configuration Loading

The `src/config/api.js` file reads environment variables and provides a centralized configuration:

```javascript
import { API_ENDPOINTS } from '../config/api.js';

// Use configured endpoints
const response = await fetch(API_ENDPOINTS.uploadResume(), {
  method: 'POST',
  body: formData
});
```

### 2. Fallback Behavior

The configuration includes fallbacks for missing variables:

1. `VITE_BACKEND_URL` (primary)
2. `VITE_API_BASE_URL` (fallback)
3. `http://localhost:8000` (development default)

### 3. Available Endpoints

All API endpoints are pre-configured and accessible via `API_ENDPOINTS`:

- `API_ENDPOINTS.uploadResume()`
- `API_ENDPOINTS.searchJobs()`
- `API_ENDPOINTS.fetchJobDescription()`
- `API_ENDPOINTS.analyzeResumeVsJob()`
- `API_ENDPOINTS.getSession(sessionId)`
- `API_ENDPOINTS.deleteSession(sessionId)`
- `API_ENDPOINTS.health()`

## Troubleshooting

### Environment Variables Not Loading

1. **Check Variable Names**: Ensure variables start with `VITE_`
2. **Restart Server**: Environment changes require a restart
3. **Check .env Location**: File should be in the frontend root directory
4. **Check Console**: Development mode logs the configuration

### API Calls Failing

1. **Check Backend URL**: Verify the backend is running at the configured URL
2. **Check CORS**: Ensure backend allows requests from frontend domain
3. **Check Network**: Verify network connectivity between frontend and backend

### Development Console

In development mode, the API configuration is logged to the browser console:

```
🔧 API Configuration: {
  baseUrl: "http://localhost:8000",
  mode: "development",
  endpoints: ["uploadResume", "searchJobs", ...]
}
```

## Security Notes

- Never commit `.env` files to version control
- Use different URLs for different environments
- Keep production URLs secure
- The `.env` files are already excluded in `.gitignore`

## Build Process

During the build process, Vite will:

1. Read environment variables starting with `VITE_`
2. Replace them in the built code
3. Remove any unused environment variables
4. Optimize the configuration for production

This ensures the final build only contains the necessary configuration for the target environment. 