import React, { useState, useEffect } from 'react';
import ResumeUpload from './components/ResumeUpload';
import JobSearch from './components/JobSearch';
import JobResults from './components/JobResults';
import Header from './components/Header';
import './App.css';

function App() {
  const [currentStep, setCurrentStep] = useState('upload'); // upload, search, results
  const [sessionData, setSessionData] = useState(null);
  const [jobResults, setJobResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleResumeUploaded = (data) => {
    setSessionData(data);
    setCurrentStep('search');
  };

  const handleJobSearchCompleted = (results) => {
    setJobResults(results);
    setCurrentStep('results');
  };

  const handleBackToSearch = () => {
    setCurrentStep('search');
  };

  const handleNewSession = () => {
    setSessionData(null);
    setJobResults(null);
    setCurrentStep('upload');
  };

  return (
    <div className="app">
      <Header 
        currentStep={currentStep}
        onNewSession={handleNewSession}
        sessionData={sessionData}
      />
      
      <main className="main-content">
        {currentStep === 'upload' && (
          <ResumeUpload 
            onResumeUploaded={handleResumeUploaded}
            loading={loading}
            setLoading={setLoading}
          />
        )}
        
        {currentStep === 'search' && sessionData && (
          <JobSearch 
            sessionData={sessionData}
            onJobSearchCompleted={handleJobSearchCompleted}
            loading={loading}
            setLoading={setLoading}
          />
        )}
        
        {currentStep === 'results' && jobResults && (
          <JobResults 
            jobResults={jobResults}
            sessionData={sessionData}
            onBackToSearch={handleBackToSearch}
            loading={loading}
            setLoading={setLoading}
          />
        )}
      </main>

      <footer className="footer">
        <div className="footer-content">
          <p>&copy; 2025 Job Seeker Pro. Find your perfect job with AI-powered matching.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
