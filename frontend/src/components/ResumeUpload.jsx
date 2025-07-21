import React, { useState, useRef } from 'react';
import { API_ENDPOINTS } from '../config/api.js';

const ResumeUpload = ({ onResumeUploaded, loading, setLoading }) => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [formData, setFormData] = useState({
    location: '',
    experience_level: 'entry',
    job_type: 'full-time',
    remote_preference: 'hybrid'
  });
  const [errors, setErrors] = useState({});
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      validateAndSetFile(droppedFile);
    }
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword', 'text/plain'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!validTypes.includes(selectedFile.type)) {
      setErrors({ file: 'Please upload a PDF, DOCX, DOC, or TXT file.' });
      return;
    }

    if (selectedFile.size > maxSize) {
      setErrors({ file: 'File size must be less than 10MB.' });
      return;
    }

    setFile(selectedFile);
    setErrors({ ...errors, file: null });
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!file) {
      newErrors.file = 'Please upload your resume.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    
    try {
      const submitData = new FormData();
      submitData.append('file', file);
      submitData.append('location', formData.location);
      submitData.append('experience_level', formData.experience_level);
      submitData.append('job_type', formData.job_type);
      submitData.append('remote_preference', formData.remote_preference);

      const response = await fetch(API_ENDPOINTS.uploadResume(), {
        method: 'POST',
        body: submitData,
      });

      const result = await response.json();

      if (result.success) {
        onResumeUploaded(result);
      } else {
        setErrors({ submit: result.detail || 'Failed to process resume. Please try again.' });
      }
    } catch (error) {
      console.error('Upload error:', error);
      setErrors({ submit: 'Network error. Please check your connection and try again.' });
    } finally {
      setLoading(false);
    }
  };

  const removeFile = () => {
    setFile(null);
    setErrors({ ...errors, file: null });
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="resume-upload">
      <div className="upload-container">
        <div className="upload-header">
          <h2 className="upload-title">
            <span className="upload-icon">📄</span>
            Upload Your Resume
          </h2>
          <p className="upload-subtitle">
            Let AI analyze your skills and find the perfect job matches
          </p>
        </div>

        <form onSubmit={handleSubmit} className="upload-form">
          {/* File Upload Section */}
          <div className="form-section">
            <h3 className="section-title">Resume File</h3>
            
            <div 
              className={`file-upload-area ${dragActive ? 'drag-active' : ''} ${file ? 'has-file' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileSelect}
                accept=".pdf,.docx,.doc,.txt"
                style={{ display: 'none' }}
              />
              
              {!file ? (
                <>
                  <div className="upload-icon-large">📁</div>
                  <h4>Drop your resume here or click to browse</h4>
                  <p>Supports PDF, DOCX, DOC, and TXT files (max 10MB)</p>
                </>
              ) : (
                <div className="file-selected">
                  <div className="file-info">
                    <span className="file-icon">📄</span>
                    <div className="file-details">
                      <h4>{file.name}</h4>
                      <p>{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                  </div>
                  <button 
                    type="button" 
                    className="remove-file-btn"
                    onClick={(e) => { e.stopPropagation(); removeFile(); }}
                  >
                    ✕
                  </button>
                </div>
              )}
            </div>
            {errors.file && <span className="error-message">{errors.file}</span>}
          </div>

          {/* Job Preferences Section */}
          <div className="form-section">
            <h3 className="section-title">Job Preferences</h3>
            
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="location">Preferred Location <span className="optional">(Optional)</span></label>
                <input
                  type="text"
                  id="location"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  placeholder="e.g., San Francisco, CA or Remote (Leave empty for all locations)"
                  className={errors.location ? 'error' : ''}
                />
                {errors.location && <span className="error-message">{errors.location}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="experience_level">Experience Level</label>
                <select
                  id="experience_level"
                  name="experience_level"
                  value={formData.experience_level}
                  onChange={handleInputChange}
                >
                  <option value="entry">Entry Level (0-2 years)</option>
                  <option value="mid">Mid Level (3-5 years)</option>
                  <option value="senior">Senior Level (5+ years)</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="job_type">Job Type</label>
                <select
                  id="job_type"
                  name="job_type"
                  value={formData.job_type}
                  onChange={handleInputChange}
                >
                  <option value="full-time">Full-time</option>
                  <option value="part-time">Part-time</option>
                  <option value="internship">Internship</option>
                  <option value="contract">Contract</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="remote_preference">Work Preference</label>
                <select
                  id="remote_preference"
                  name="remote_preference"
                  value={formData.remote_preference}
                  onChange={handleInputChange}
                >
                  <option value="remote">Remote</option>
                  <option value="hybrid">Hybrid</option>
                  <option value="on-site">On-site</option>
                </select>
              </div>
            </div>
          </div>

          {errors.submit && (
            <div className="error-banner">
              <span className="error-icon">⚠️</span>
              {errors.submit}
            </div>
          )}

          <button 
            type="submit" 
            className="btn btn-primary btn-large"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Processing Resume...
              </>
            ) : (
              <>
                <span>🚀</span>
                Analyze Resume & Find Jobs
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ResumeUpload; 