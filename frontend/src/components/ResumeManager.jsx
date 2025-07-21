import React, { useState, useRef, useEffect } from 'react';
import { API_ENDPOINTS } from '../config/api.js';

const ResumeManager = ({ uploadedResumes, setUploadedResumes, loading, setLoading }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadForm, setUploadForm] = useState({
    location: '',
    experience_level: 'entry',
    job_type: 'full-time',
    remote_preference: 'hybrid'
  });
  const [errors, setErrors] = useState({});
  const fileInputRef = useRef(null);

  // Load resumes from localStorage on component mount
  useEffect(() => {
    const savedResumes = localStorage.getItem('jobseeker_resumes');
    if (savedResumes) {
      try {
        const parsedResumes = JSON.parse(savedResumes);
        setUploadedResumes(parsedResumes);
      } catch (error) {
        console.error('Error loading resumes from localStorage:', error);
        localStorage.removeItem('jobseeker_resumes');
      }
    }
  }, [setUploadedResumes]);

  // Save resumes to localStorage whenever uploadedResumes changes
  useEffect(() => {
    if (uploadedResumes.length > 0) {
      localStorage.setItem('jobseeker_resumes', JSON.stringify(uploadedResumes));
    } else {
      localStorage.removeItem('jobseeker_resumes');
    }
  }, [uploadedResumes]);

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
      handleFileUpload(droppedFile);
    }
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      handleFileUpload(selectedFile);
    }
  };

  const validateFile = (file) => {
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword', 'text/plain'];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!validTypes.includes(file.type)) {
      return 'Please upload a PDF, DOCX, DOC, or TXT file.';
    }

    if (file.size > maxSize) {
      return 'File size must be less than 10MB.';
    }

    return null;
  };

  const handleFileUpload = async (file) => {
    const fileError = validateFile(file);
    if (fileError) {
      setErrors({ upload: fileError });
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('location', uploadForm.location);
      formData.append('experience_level', uploadForm.experience_level);
      formData.append('job_type', uploadForm.job_type);
      formData.append('remote_preference', uploadForm.remote_preference);

      const response = await fetch(API_ENDPOINTS.uploadResume(), {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        const newResume = {
          id: result.session_id,
          name: file.name,
          uploadedAt: new Date().toISOString(),
          extractedInfo: result.data.extracted_info,
          preferences: result.data.preferences,
          size: file.size
        };
        
        setUploadedResumes(prev => [...prev, newResume]);
        
        // Clear file input
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
      } else {
        setErrors({ upload: result.detail || 'Failed to process resume. Please try again.' });
      }
    } catch (error) {
      console.error('Upload error:', error);
      setErrors({ upload: 'Network error. Please check your connection and try again.' });
    } finally {
      setLoading(false);
    }
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setUploadForm(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const deleteResume = (resumeId) => {
    setUploadedResumes(prev => prev.filter(resume => resume.id !== resumeId));
  };

  const clearAllResumes = () => {
    if (window.confirm('Are you sure you want to delete all uploaded resumes? This action cannot be undone.')) {
      setUploadedResumes([]);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="resume-manager">
      <div className="section-header">
        <h1 className="section-title">Resume Manager</h1>
        <p className="section-description">
          Upload and manage your resumes. Each uploaded resume will be processed and available for scoring.
        </p>
      </div>

      {/* Upload Section */}
      <div className="upload-section">
        <h2 className="subsection-title">Upload New Resume</h2>
        
        <div className="upload-container">
          <div 
            className={`file-upload-area ${dragActive ? 'drag-active' : ''}`}
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
            
            <div className="upload-content">
              <div className="upload-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14,2 14,8 20,8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10,9 9,9 8,9"/>
                </svg>
              </div>
              <h3>Drop your resume here or click to browse</h3>
              <p>Supports PDF, DOCX, DOC, and TXT files (max 10MB)</p>
            </div>
          </div>

          {/* Upload Form */}
          <div className="upload-form">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="location">Preferred Location</label>
                <input
                  type="text"
                  id="location"
                  name="location"
                  value={uploadForm.location}
                  onChange={handleFormChange}
                  placeholder="e.g., San Francisco, Remote"
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="experience_level">Experience Level</label>
                <select
                  id="experience_level"
                  name="experience_level"
                  value={uploadForm.experience_level}
                  onChange={handleFormChange}
                >
                  <option value="entry">Entry Level</option>
                  <option value="mid">Mid Level</option>
                  <option value="senior">Senior Level</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="job_type">Job Type</label>
                <select
                  id="job_type"
                  name="job_type"
                  value={uploadForm.job_type}
                  onChange={handleFormChange}
                >
                  <option value="full-time">Full Time</option>
                  <option value="part-time">Part Time</option>
                  <option value="contract">Contract</option>
                  <option value="internship">Internship</option>
                </select>
              </div>
              
              <div className="form-group">
                <label htmlFor="remote_preference">Work Preference</label>
                <select
                  id="remote_preference"
                  name="remote_preference"
                  value={uploadForm.remote_preference}
                  onChange={handleFormChange}
                >
                  <option value="onsite">On-site</option>
                  <option value="remote">Remote</option>
                  <option value="hybrid">Hybrid</option>
                </select>
              </div>
            </div>
          </div>

          {errors.upload && (
            <div className="error-message">
              {errors.upload}
            </div>
          )}
        </div>
      </div>

      {/* Uploaded Resumes Section */}
      <div className="resumes-section">
        <div className="resumes-header">
          <h2 className="subsection-title">
            Your Resumes ({uploadedResumes.length})
          </h2>
          {uploadedResumes.length > 0 && (
            <button 
              className="clear-all-btn"
              onClick={clearAllResumes}
              title="Delete all resumes"
            >
              Clear All
            </button>
          )}
        </div>
        
        {uploadedResumes.length === 0 ? (
          <div className="empty-state">
            <p>No resumes uploaded yet. Upload your first resume above to get started.</p>
          </div>
        ) : (
          <div className="resumes-grid">
            {uploadedResumes.map((resume) => (
              <div key={resume.id} className="resume-card">
                <div className="resume-header">
                  <h3 className="resume-name">{resume.name}</h3>
                  <button 
                    className="delete-btn"
                    onClick={() => deleteResume(resume.id)}
                    title="Delete resume"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <polyline points="3,6 5,6 21,6"/>
                      <path d="M19,6v14a2,2,0,0,1-2,2H7a2,2,0,0,1-2-2V6m3,0V4a2,2,0,0,1,2-2h4a2,2,0,0,1,2,2V6"/>
                    </svg>
                  </button>
                </div>
                
                <div className="resume-info">
                  <div className="info-item">
                    <span className="label">Role:</span>
                    <span className="value">{resume.extractedInfo.role || 'Not specified'}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Skills:</span>
                    <span className="value">
                      {resume.extractedInfo.skills?.slice(0, 3).join(', ')}
                      {resume.extractedInfo.skills?.length > 3 && ` +${resume.extractedInfo.skills.length - 3} more`}
                    </span>
                  </div>
                  <div className="info-item">
                    <span className="label">Location:</span>
                    <span className="value">{resume.preferences.location || 'Not specified'}</span>
                  </div>
                </div>
                
                <div className="resume-meta">
                  <span className="upload-date">
                    Uploaded: {formatDate(resume.uploadedAt)}
                  </span>
                  <span className="file-size">
                    {formatFileSize(resume.size)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p>Processing resume...</p>
        </div>
      )}
    </div>
  );
};

export default ResumeManager; 