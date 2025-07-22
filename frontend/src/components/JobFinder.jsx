import React, { useState } from 'react';
import { API_ENDPOINTS } from '../config/api.js';
import JobSearch from './JobSearch';
import JobResults from './JobResults';
import './JobFinder.css';

const JobFinder = ({ uploadedResumes, loading, setLoading }) => {
  const [step, setStep] = useState(1); // 1: Select Resume, 2: Search Form, 3: Results
  const [selectedResume, setSelectedResume] = useState('');
  const [sessionData, setSessionData] = useState(null);
  const [jobResults, setJobResults] = useState(null);
  const [error, setError] = useState('');

  // Step 1: Resume selection
  const handleResumeSelect = async (e) => {
    const sessionId = e.target.value;
    setSelectedResume(sessionId);
    setJobResults(null);
    setError('');
    if (sessionId) {
      setLoading(true);
      try {
        const res = await fetch(`${API_ENDPOINTS.getSession(sessionId).replace('/sessions/', '/resume/sessions/')}`);
        const data = await res.json();
        if (data.success) {
          setSessionData({ ...data, session_id: sessionId });
          setStep(2);
        } else {
          setSessionData(null);
          setError('Failed to load resume session data.');
        }
      } catch (err) {
        setSessionData(null);
        setError('Network error loading resume session.');
      } finally {
        setLoading(false);
      }
    } else {
      setSessionData(null);
    }
  };

  // Step 2: Job Search logic
  const handleJobSearchCompleted = (results) => {
    setJobResults(results);
    setStep(3);
  };

  // Step navigation
  const handleBackToResume = () => {
    setStep(1);
    setSelectedResume('');
    setSessionData(null);
    setJobResults(null);
    setError('');
  };

  const handleBackToSearch = () => {
    setStep(2);
    setJobResults(null);
    setError('');
  };

  // If no resumes uploaded
  if (!uploadedResumes || uploadedResumes.length === 0) {
    return (
      <div className="job-finder-section">
        <h2>Let's find you a job!</h2>
        <div className="no-resumes-message">
          <p>You haven't uploaded any resumes yet. Start by uploading a resume to find matching jobs!</p>
          <a href="#resume-manager" className="btn btn-primary">
            <span>📄</span>
            Upload Resume
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="job-finder-section">
      <h2>Let's find you a job!</h2>
      
      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading...</p>
        </div>
      )}

      {/* Step 1: Resume selection */}
      {!loading && step === 1 && (
        <div className="step-resume-select">
          <div className="form-group">
            <label>Select a Resume</label>
            <select 
              value={selectedResume} 
              onChange={handleResumeSelect} 
              required
              className={error ? 'error' : ''}
            >
              <option value="">Choose a resume to start...</option>
              {uploadedResumes.map(resume => (
                <option key={resume.id} value={resume.id}>
                  {resume.name || resume.filename}
                </option>
              ))}
            </select>
            {error && <div className="error-message">{error}</div>}
          </div>
          <p className="help-text">
            Choose a resume to find matching job opportunities. We'll analyze your skills and experience to find the best matches.
          </p>
        </div>
      )}

      {/* Step 2: Job Search Form */}
      {!loading && step === 2 && sessionData && (
        <div className="step-job-search">
          <button className="back-button" onClick={handleBackToResume}>
            Back to Resume Selection
          </button>
          <JobSearch
            sessionData={sessionData}
            onJobSearchCompleted={handleJobSearchCompleted}
            loading={loading}
            setLoading={setLoading}
          />
        </div>
      )}

      {/* Step 3: Job Results */}
      {!loading && step === 3 && jobResults && (
        <div className="step-job-results">
          <button className="back-button" onClick={handleBackToSearch}>
            Back to Search
          </button>
          <JobResults
            jobResults={jobResults}
            sessionData={sessionData}
            onBackToSearch={handleBackToSearch}
            loading={loading}
            setLoading={setLoading}
          />
        </div>
      )}
    </div>
  );
};

export default JobFinder; 