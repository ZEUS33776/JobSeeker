# JobSeeker API Setup Guide

## Required API Keys

To use all features of the JobSeeker application, you need to configure the following API keys:

### 1. Gemini AI API Key (GEMINI_API_KEY)
- **Purpose**: Used for resume analysis and LLM operations
- **Get your key**: https://makersuite.google.com/app/apikey
- **Free tier**: Available with usage limits

### 2. Serper API Key (SERPER_API_KEY)  
- **Purpose**: Used for job search functionality
- **Get your key**: https://serper.dev/
- **Free tier**: 2,500 free searches per month

## Setup Instructions

1. **Create .env file** in the backend directory:
```bash
cp .env.example .env
```

2. **Edit the .env file** and add your API keys:
```
GEMINI_API_KEY=your_actual_gemini_api_key_here
SERPER_API_KEY=your_actual_serper_api_key_here
PORT=8000
```

3. **Restart the backend server** for changes to take effect.

## What Works Without API Keys

Even without API keys configured, you can still use:
- ✅ Resume PDF text extraction  
- ✅ Basic job description scraping (from job URLs)
- ✅ Frontend interface

## What Requires API Keys

These features need API keys to function:
- ❌ Resume analysis and skill extraction (needs GEMINI_API_KEY)
- ❌ Job search functionality (needs SERPER_API_KEY)
- ❌ Job ranking based on resume (needs GEMINI_API_KEY)

## Error Messages

If you see errors like "API configuration incomplete", it means:
1. The .env file is missing, or
2. One or more required API keys are not set

## Getting Started Quickly

For testing purposes, you can:
1. Use the job description scraper with direct URLs
2. Upload resumes to test PDF text extraction
3. Set up API keys later when you're ready for full functionality

## Support

If you need help getting API keys or configuring the application, please check:
- [Gemini AI Documentation](https://ai.google.dev/docs)
- [Serper API Documentation](https://serper.dev/api) 