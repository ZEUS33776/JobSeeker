import React, { useState, useEffect } from 'react';
import ResumeManager from './components/ResumeManager';
import ResumeScoring from './components/ResumeScoring';
import ResumeBuilder from './components/ResumeBuilder';
import JobFinder from './components/JobFinder';
import SectionPlaceholder from './components/SectionPlaceholder';
import Header from './components/Header';
import './App.css';

function App() {
  const [activeSection, setActiveSection] = useState('resume-manager');
  const [uploadedResumes, setUploadedResumes] = useState([]);
  const [loading, setLoading] = useState(false);

  const sections = [
    { id: 'resume-manager', title: 'Resume Manager', icon: 'folder' },
    { id: 'resume-scoring', title: 'Resume Scoring', icon: 'chart' },
    { id: 'resume-builder', title: 'Make Your Resume', icon: 'file-text' },
    { id: 'section-3', title: 
      "Let's find you a job!", icon: 'target' }
  ];

  return (
    <div className="app">
      <Header />
      
      <div className="app-layout">
        {/* Section Navigation */}
        <nav className="section-nav">
          <div className="nav-header">
            <h2>Dashboard</h2>
          </div>
          <ul className="nav-list">
            {sections.map((section) => (
              <li key={section.id}>
                <button
                  className={`nav-item ${activeSection === section.id ? 'active' : ''}`}
                  onClick={() => setActiveSection(section.id)}
                                 >
                   <span className="nav-icon">
                     {section.icon === 'folder' && (
                       <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                         <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2v11z"/>
                       </svg>
                     )}
                     {section.icon === 'chart' && (
                       <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                         <line x1="18" y1="20" x2="18" y2="10"/>
                         <line x1="12" y1="20" x2="12" y2="4"/>
                         <line x1="6" y1="20" x2="6" y2="14"/>
                       </svg>
                     )}
                     {section.icon === 'file-text' && (
                       <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                         <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                         <polyline points="14,2 14,8 20,8"/>
                         <line x1="16" y1="13" x2="8" y2="13"/>
                         <line x1="16" y1="17" x2="8" y2="17"/>
                         <polyline points="10,9 9,9 8,9"/>
                       </svg>
                     )}
                     {section.icon === 'target' && (
                       <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                         <circle cx="12" cy="12" r="10"/>
                         <circle cx="12" cy="12" r="6"/>
                         <circle cx="12" cy="12" r="2"/>
                       </svg>
                     )}
                   </span>
                   <span className="nav-text">{section.title}</span>
                 </button>
              </li>
            ))}
          </ul>
        </nav>

        {/* Main Content Area */}
        <main className="main-content">
          <div className="content-container">
            {activeSection === 'resume-manager' && (
              <ResumeManager
                uploadedResumes={uploadedResumes}
                setUploadedResumes={setUploadedResumes}
                loading={loading}
                setLoading={setLoading}
              />
            )}
            
            {activeSection === 'resume-scoring' && (
              <ResumeScoring
                uploadedResumes={uploadedResumes}
                loading={loading}
                setLoading={setLoading}
              />
            )}
            
            {activeSection === 'resume-builder' && (
              <ResumeBuilder
                uploadedResumes={uploadedResumes}
                loading={loading}
                setLoading={setLoading}
              />
            )}
            
            {activeSection === 'section-3' && (
              <JobFinder
                uploadedResumes={uploadedResumes}
                loading={loading}
                setLoading={setLoading}
              />
            )}
          </div>
        </main>
      </div>

      <footer className="footer">
        <div className="footer-content">
          <p>&copy; 2025 Job Seeker Pro. Professional job matching platform.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
