# JobSeeker Frontend

A modern React application for job searching with AI-powered resume analysis.

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Environment Setup
Copy the environment example and configure your backend URL:

```bash
cp src/config/env.example .env
```

Edit `.env` file:
```bash
# Required: Backend API URL
VITE_BACKEND_URL=http://localhost:8000

# Optional: App settings
VITE_APP_NAME=JobSeeker
VITE_APP_VERSION=1.0.0
```

### 3. Start Development Server
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Environment Configuration

The application uses environment variables for configuration. See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for detailed setup instructions.

### Quick Environment Setup

| Environment | Backend URL |
|-------------|-------------|
| Development | `http://localhost:8000` |
| Staging | `https://staging-api.jobseeker.com` |
| Production | `https://api.jobseeker.com` |

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Features

### ✅ **Implemented**
- 📄 **Resume Upload & Analysis** - AI-powered resume parsing
- 🤖 **AI Role Suggestions** - Smart role recommendations based on skills
- 🔍 **Job Search** - Multi-platform job discovery
- 📊 **ATS Analysis** - Resume vs job description compatibility
- 🎯 **Skill Management** - Interactive skill editing
- 📱 **Responsive Design** - Mobile-friendly interface

### 🎨 **UI Components**
- Modern dark theme with blue accents
- Drag & drop file upload
- Interactive skill tags with add/remove functionality
- AI suggestions with one-click integration
- Real-time job search with filtering
- Detailed ATS analysis with actionable insights

### 🔧 **Technical Features**
- Environment-based configuration
- Centralized API management
- Error handling and loading states
- Form validation and user feedback
- Responsive grid layouts

## API Integration

The frontend communicates with the JobSeeker API through a centralized configuration system:

```javascript
// All API calls use the configured backend URL
import { API_ENDPOINTS } from './config/api.js';

// Example usage
const response = await fetch(API_ENDPOINTS.searchJobs(), {
  method: 'POST',
  body: formData
});
```

## Project Structure

```
src/
├── components/          # React components
│   ├── Header.jsx
│   ├── ResumeUpload.jsx
│   ├── JobSearch.jsx
│   └── JobResults.jsx
├── config/              # Configuration files
│   ├── api.js          # API endpoints and configuration
│   └── env.example     # Environment variables example
├── assets/             # Static assets
├── App.jsx             # Main application component
└── main.jsx           # Application entry point
```

## Development

### Prerequisites
- Node.js 16+ and npm
- JobSeeker backend API running

### Local Development
1. Clone the repository
2. Install dependencies: `npm install`
3. Configure environment: Copy `src/config/env.example` to `.env`
4. Start backend API on port 8000
5. Start frontend: `npm run dev`

### Building for Production
```bash
npm run build
```

The built files will be in the `dist` directory.

## Troubleshooting

### Common Issues

**Environment Variables Not Working:**
- Ensure variables start with `VITE_`
- Restart the development server after changes
- Check the browser console for configuration logs

**API Calls Failing:**
- Verify backend is running at the configured URL
- Check CORS settings on the backend
- Verify network connectivity

**Build Issues:**
- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check for TypeScript errors: `npm run lint`

### Development Console

In development mode, the API configuration is logged:
```
🔧 API Configuration: {
  baseUrl: "http://localhost:8000",
  mode: "development",
  endpoints: ["uploadResume", "searchJobs", ...]
}
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Update tests if needed
4. Submit a pull request

## License

This project is part of the JobSeeker application suite.
