import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../config/api.js';
import TemplateSelector from './TemplateSelector.jsx';
import ResumeForm from './ResumeForm.jsx';
import ResumePreview from './ResumePreview.jsx';

const ResumeBuilder = ({ uploadedResumes, loading, setLoading }) => {
  const [step, setStep] = useState(1); // 1: Template Selection, 2: Form Input, 3: Preview
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [inputMethod, setInputMethod] = useState('form'); // 'form' or 'existing'
  const [selectedResume, setSelectedResume] = useState('');
  const [resumeData, setResumeData] = useState(null);
  const [generatedResume, setGeneratedResume] = useState(null);
  const [errors, setErrors] = useState({});

  // Load templates on component mount
  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const response = await fetch(API_ENDPOINTS.resumeBuilderTemplates());
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.data || []);
      } else {
        console.error('Failed to load templates');
      }
    } catch (error) {
      console.error('Error loading templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template);
    setStep(2);
  };

  const handleInputMethodChange = (method) => {
    setInputMethod(method);
    setSelectedResume('');
    setResumeData(null);
  };

  const handleExistingResumeSelect = (sessionId) => {
    setSelectedResume(sessionId);
  };

  const handleFormDataSubmit = (data) => {
    setResumeData(data);
    setStep(3);
  };

  const handleGenerateResume = async () => {
    try {
      setLoading(true);
      setErrors({});

      const requestData = {
        template_id: selectedTemplate.id,
        input_method: inputMethod,
        session_id: inputMethod === 'existing' ? selectedResume : null,
        resume_data: inputMethod === 'form' ? resumeData : null
      };

      const response = await fetch(API_ENDPOINTS.resumeBuilderBuild(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      if (response.ok) {
        const result = await response.json();
        setGeneratedResume(result);
      } else {
        const errorData = await response.json();
        let errorMessage = errorData.detail || 'Failed to generate resume';
        
        // Handle specific error cases
        if (response.status === 404 && errorData.detail?.includes('Session not found')) {
          errorMessage = 'The selected resume is no longer available. Please upload a new resume or use the form option.';
          // Clear the selected resume since it's no longer valid
          setSelectedResume('');
        } else if (response.status === 404 && errorData.detail?.includes('Template not found')) {
          errorMessage = 'The selected template is no longer available. Please choose a different template.';
        }
        
        setErrors({ general: errorMessage });
      }
    } catch (error) {
      console.error('Error generating resume:', error);
      setErrors({ general: 'Failed to generate resume. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    if (step === 3) {
      setStep(2);
      setGeneratedResume(null);
    } else if (step === 2) {
      setStep(1);
      setSelectedTemplate(null);
      setInputMethod('form');
      setSelectedResume('');
      setResumeData(null);
    }
  };

  const handleReset = () => {
    setStep(1);
    setSelectedTemplate(null);
    setInputMethod('form');
    setSelectedResume('');
    setResumeData(null);
    setGeneratedResume(null);
    setErrors({});
  };

  return (
    <div className="resume-builder">
      <div className="builder-header">
        <h2 className="section-title">Make Your Resume</h2>
        <p className="section-description">
          Create a professional resume using our templates and your information
        </p>
      </div>

      {/* Progress Indicator */}
      <div className="progress-indicator">
        <div className={`progress-step ${step >= 1 ? 'active' : ''}`}>
          <span className="step-number">1</span>
          <span className="step-label">Choose Template</span>
        </div>
        <div className={`progress-step ${step >= 2 ? 'active' : ''}`}>
          <span className="step-number">2</span>
          <span className="step-label">Provide Information</span>
        </div>
        <div className={`progress-step ${step >= 3 ? 'active' : ''}`}>
          <span className="step-number">3</span>
          <span className="step-label">Generate Resume</span>
        </div>
      </div>

      {/* Error Display */}
      {errors.general && (
        <div className="error-message">
          <p>{errors.general}</p>
        </div>
      )}

      {/* Step 1: Template Selection */}
      {step === 1 && (
        <div className="step-content">
          <TemplateSelector 
            templates={templates}
            onTemplateSelect={handleTemplateSelect}
            loading={loading}
          />
        </div>
      )}

      {/* Step 2: Input Method and Form */}
      {step === 2 && (
        <div className="step-content">
          <div className="input-method-selector">
            <h3>How would you like to provide your information?</h3>
            <div className="method-options">
              <button
                className={`method-option ${inputMethod === 'form' ? 'active' : ''}`}
                onClick={() => handleInputMethodChange('form')}
              >
                <div className="method-icon">📝</div>
                <div className="method-content">
                  <h4>Fill Out Form</h4>
                  <p>Provide your information through our structured form</p>
                </div>
              </button>
              
              <button
                className={`method-option ${inputMethod === 'existing' ? 'active' : ''}`}
                onClick={() => handleInputMethodChange('existing')}
                disabled={uploadedResumes.length === 0}
              >
                <div className="method-icon">📄</div>
                <div className="method-content">
                  <h4>Use Existing Resume</h4>
                  <p>Use information from a previously uploaded resume</p>
                  {uploadedResumes.length === 0 && (
                    <span className="method-note">No resumes uploaded yet</span>
                  )}
                </div>
              </button>
            </div>
          </div>

          {inputMethod === 'existing' && (
            <div className="existing-resume-selector">
              <h4>Select a Resume</h4>
              {uploadedResumes.length === 0 ? (
                <div className="no-resumes-message">
                  <p>No resumes uploaded yet. Please upload a resume first.</p>
                  <button 
                    className="btn-secondary"
                    onClick={() => {
                      // Switch to Resume Manager tab or show upload dialog
                      window.location.hash = '#resume-manager';
                    }}
                  >
                    Go to Resume Manager
                  </button>
                </div>
              ) : (
                <div className="resume-options">
                  {uploadedResumes.map((resume, index) => (
                    <button
                      key={index}
                      className={`resume-option ${selectedResume === resume.id ? 'active' : ''}`}
                      onClick={() => handleExistingResumeSelect(resume.id)}
                    >
                      <div className="resume-info">
                        <h5>{resume.filename}</h5>
                        <p>Uploaded: {resume.uploadedAt ? new Date(resume.uploadedAt).toLocaleDateString() : 'Unknown date'}</p>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {inputMethod === 'form' && (
            <ResumeForm 
              onSubmit={handleFormDataSubmit}
              onBack={handleBack}
            />
          )}

          {inputMethod === 'existing' && (
            <div className="action-buttons">
              <button className="btn-secondary" onClick={handleBack}>
                Back
              </button>
              <button 
                className="btn-primary" 
                onClick={() => setStep(3)}
                disabled={!selectedResume}
              >
                Continue
              </button>
            </div>
          )}
        </div>
      )}

      {/* Step 3: Preview and Generate */}
      {step === 3 && (
        <div className="step-content">
          <ResumePreview 
            template={selectedTemplate}
            inputMethod={inputMethod}
            resumeData={resumeData}
            selectedResume={selectedResume}
            generatedResume={generatedResume}
            onGenerate={handleGenerateResume}
            onBack={handleBack}
            onReset={handleReset}
            loading={loading}
          />
        </div>
      )}
    </div>
  );
};

export default ResumeBuilder; 