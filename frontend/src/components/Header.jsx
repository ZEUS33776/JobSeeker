import React from 'react';

const Header = ({ currentStep, onNewSession, sessionData }) => {
  const getStepTitle = () => {
    switch (currentStep) {
      case 'upload':
        return 'Upload Resume';
      case 'search':
        return 'Search Jobs';
      case 'results':
        return 'Job Results';
      default:
        return 'Job Seeker Pro';
    }
  };

  const getStepNumber = () => {
    switch (currentStep) {
      case 'upload':
        return 1;
      case 'search':
        return 2;
      case 'results':
        return 3;
      default:
        return 1;
    }
  };

  return (
    <header className="header">
      <div className="header-content">
        <div className="brand">
          <h1 className="brand-title">
            <span className="brand-icon">🎯</span>
            Job Seeker Pro
          </h1>
          <p className="brand-subtitle">AI-Powered Job Matching</p>
        </div>

        <div className="step-indicator">
          <div className="step-progress">
            <div className="step-item">
              <div className={`step-number ${currentStep === 'upload' ? 'active' : currentStep !== 'upload' && getStepNumber() > 1 ? 'completed' : ''}`}>
                1
              </div>
              <span className="step-label">Upload</span>
            </div>
            <div className="step-line"></div>
            <div className="step-item">
              <div className={`step-number ${currentStep === 'search' ? 'active' : currentStep === 'results' ? 'completed' : ''}`}>
                2
              </div>
              <span className="step-label">Search</span>
            </div>
            <div className="step-line"></div>
            <div className="step-item">
              <div className={`step-number ${currentStep === 'results' ? 'active' : ''}`}>
                3
              </div>
              <span className="step-label">Results</span>
            </div>
          </div>
        </div>

        <div className="header-actions">
          {sessionData && (
            <div className="session-info">
              <span className="session-detail">
                📄 {sessionData.data.extracted_info.role || 'Resume'} | 
                🏢 {sessionData.data.preferences.location}
              </span>
            </div>
          )}
          
          {currentStep !== 'upload' && (
            <button 
              className="btn btn-outline"
              onClick={onNewSession}
              title="Start new session"
            >
              <span>🔄</span>
              New Search
            </button>
          )}
        </div>
      </div>

      <div className="current-step-banner">
        <div className="step-banner-content">
          <h2 className="step-title">
            Step {getStepNumber()}: {getStepTitle()}
          </h2>
          <p className="step-description">
            {currentStep === 'upload' && 'Upload your resume and set your job preferences'}
            {currentStep === 'search' && 'Search for jobs that match your profile'}
            {currentStep === 'results' && 'Browse and explore your personalized job matches'}
          </p>
        </div>
      </div>
    </header>
  );
};

export default Header; 