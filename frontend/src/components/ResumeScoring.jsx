import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../config/api.js';

const ResumeScoring = ({ uploadedResumes, loading, setLoading }) => {
  const [selectedResume, setSelectedResume] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [scoringMode, setScoringMode] = useState('standalone'); // 'standalone' or 'comparison'
  const [scoringResults, setScoringResults] = useState(null);
  const [errors, setErrors] = useState({});

  // Load saved state from localStorage on component mount
  useEffect(() => {
    const savedState = localStorage.getItem('jobseeker_scoring_state');
    if (savedState) {
      try {
        const parsedState = JSON.parse(savedState);
        setSelectedResume(parsedState.selectedResume || '');
        setJobDescription(parsedState.jobDescription || '');
        setScoringMode(parsedState.scoringMode || 'standalone');
        setScoringResults(parsedState.scoringResults || null);
      } catch (error) {
        console.error('Error loading scoring state from localStorage:', error);
        localStorage.removeItem('jobseeker_scoring_state');
      }
    }
  }, []);

  // Save state to localStorage whenever relevant state changes
  useEffect(() => {
    const stateToSave = {
      selectedResume,
      jobDescription,
      scoringMode,
      scoringResults
    };
    localStorage.setItem('jobseeker_scoring_state', JSON.stringify(stateToSave));
  }, [selectedResume, jobDescription, scoringMode, scoringResults]);

  const handleScoringModeChange = (mode) => {
    setScoringMode(mode);
    setScoringResults(null);
    setErrors({});
    if (mode === 'standalone') {
      setJobDescription('');
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!selectedResume) {
      newErrors.resume = 'Please select a resume to analyze.';
    }

    if (scoringMode === 'comparison' && !jobDescription.trim()) {
      newErrors.jobDescription = 'Please provide a job description for comparison.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleScoreResume = async () => {
    if (!validateForm()) return;

    setLoading(true);
    setErrors({});
    setScoringResults(null);

    try {
      let response;
      
      if (scoringMode === 'standalone') {
        // For standalone scoring, we'll create a new endpoint
        const formData = new FormData();
        formData.append('session_id', selectedResume);
        
        response = await fetch(API_ENDPOINTS.scoreResumeStandalone(), {
          method: 'POST',
          body: formData,
        });
      } else {
        // For comparison scoring, use existing endpoint
        const requestData = {
          session_id: selectedResume,
          job_description: jobDescription
        };
        
        response = await fetch(API_ENDPOINTS.analyzeResumeVsJob(), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestData),
        });
      }

      const result = await response.json();

      if (result.success) {
        setScoringResults(result.data);
      } else {
        setErrors({ submit: result.detail || 'Failed to analyze resume. Please try again.' });
      }
    } catch (error) {
      console.error('Scoring error:', error);
      setErrors({ submit: 'Network error. Please check your connection and try again.' });
    } finally {
      setLoading(false);
    }
  };

  const clearResults = () => {
    setScoringResults(null);
    setErrors({});
  };

  const getScoreColor = (score) => {
    if (score >= 85) return '#22c55e'; // green
    if (score >= 70) return '#3b82f6'; // blue  
    if (score >= 55) return '#f59e0b'; // orange
    return '#ef4444'; // red
  };

  const getScoreLabel = (score) => {
    if (score >= 85) return 'Excellent';
    if (score >= 70) return 'Good';
    if (score >= 55) return 'Fair';
    return 'Needs Improvement';
  };

  const selectedResumeData = uploadedResumes.find(r => r.id === selectedResume);

  return (
    <div className="resume-scoring">
      <div className="section-header">
        <h1 className="section-title">Resume Scoring</h1>
        <p className="section-description">
          Analyze your resume's ATS compatibility and get actionable insights for improvement.
        </p>
      </div>

      {uploadedResumes.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14,2 14,8 20,8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10,9 9,9 8,9"/>
            </svg>
          </div>
          <h3>No Resumes Available</h3>
          <p>Please upload a resume in the Resume Manager section first.</p>
        </div>
      ) : (
        <>
          {/* Scoring Configuration */}
          <div className="scoring-config">
            <h2 className="subsection-title">Configure Analysis</h2>
            
            {/* Resume Selection */}
            <div className="config-section">
              <label htmlFor="resume-select">Select Resume</label>
              <select
                id="resume-select"
                value={selectedResume}
                onChange={(e) => setSelectedResume(e.target.value)}
                className={errors.resume ? 'error' : ''}
              >
                <option value="">Choose a resume...</option>
                {uploadedResumes.map((resume) => (
                  <option key={resume.id} value={resume.id}>
                    {resume.name} - {resume.extractedInfo.role || 'No role detected'}
                  </option>
                ))}
              </select>
              {errors.resume && <span className="error-text">{errors.resume}</span>}
            </div>

            {/* Scoring Mode Selection */}
            <div className="config-section">
              <label>Analysis Type</label>
              <div className="mode-selection">
                <button
                  className={`mode-btn ${scoringMode === 'standalone' ? 'active' : ''}`}
                  onClick={() => handleScoringModeChange('standalone')}
                >
                  <div className="mode-content">
                    <h4>ATS Score</h4>
                    <p>Analyze resume against general ATS standards</p>
                  </div>
                </button>
                <button
                  className={`mode-btn ${scoringMode === 'comparison' ? 'active' : ''}`}
                  onClick={() => handleScoringModeChange('comparison')}
                >
                  <div className="mode-content">
                    <h4>Job Match Score</h4>
                    <p>Compare resume against specific job description</p>
                  </div>
                </button>
              </div>
            </div>

            {/* Job Description Input (only for comparison mode) */}
            {scoringMode === 'comparison' && (
              <div className="config-section">
                <label htmlFor="job-description">Job Description</label>
                <textarea
                  id="job-description"
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the job description here..."
                  rows="8"
                  className={errors.jobDescription ? 'error' : ''}
                />
                {errors.jobDescription && <span className="error-text">{errors.jobDescription}</span>}
              </div>
            )}

            {/* Action Button */}
            <div className="config-actions">
              <button
                className="analyze-btn"
                onClick={handleScoreResume}
                disabled={loading || !selectedResume}
              >
                {loading ? (
                  <>
                    <div className="btn-spinner"></div>
                    Analyzing...
                  </>
                ) : (
                  `Analyze Resume ${scoringMode === 'comparison' ? 'vs Job' : ''}`
                )}
              </button>
            </div>

            {errors.submit && (
              <div className="error-message">
                {errors.submit}
              </div>
            )}
          </div>

          {/* Selected Resume Preview */}
          {selectedResumeData && (
            <div className="resume-preview">
              <h3>Selected Resume</h3>
              <div className="preview-card">
                <div className="preview-header">
                  <h4>{selectedResumeData.name}</h4>
                  <span className="resume-role">{selectedResumeData.extractedInfo.role}</span>
                </div>
                <div className="preview-skills">
                  <strong>Skills:</strong> {selectedResumeData.extractedInfo.skills?.slice(0, 5).join(', ')}
                  {selectedResumeData.extractedInfo.skills?.length > 5 && ` +${selectedResumeData.extractedInfo.skills.length - 5} more`}
                </div>
              </div>
            </div>
          )}

          {/* Scoring Results */}
          {scoringResults && (
            <div className="scoring-results">
              <div className="results-header">
                <h2 className="subsection-title">Analysis Results</h2>
                <button 
                  className="clear-results-btn"
                  onClick={clearResults}
                  title="Clear results"
                >
                  Clear Results
                </button>
              </div>
              
              {/* Overall Score */}
              <div className="score-overview">
                <div className="score-circle" style={{ borderColor: getScoreColor(scoringResults.overall_score) }}>
                  <span className="score-number">{scoringResults.overall_score}</span>
                  <span className="score-label">{getScoreLabel(scoringResults.overall_score)}</span>
                </div>
                <div className="score-details">
                  <h3>Overall Score: {scoringResults.overall_score}/100</h3>
                  <p className="score-description">
                    {scoringMode === 'standalone' 
                      ? 'This score reflects your resume\'s compatibility with standard ATS systems.'
                      : 'This score shows how well your resume matches the provided job description.'
                    }
                  </p>
                </div>
              </div>

              {/* Category Breakdown */}
              {scoringResults.category_breakdown && (
                <div className="category-breakdown">
                  <h3>Category Breakdown</h3>
                  <div className="categories-grid">
                    {Object.entries(scoringResults.category_breakdown)
                      .filter(([category, score]) => {
                        // Filter categories based on analysis type
                        if (scoringMode === 'standalone') {
                          // For standalone ATS analysis, only show relevant fields
                          const standaloneCategories = [
                            'ats_friendliness', 'section_completeness', 'grammar_language',
                            'resume_length', 'bullet_point_quality', 'keyword_strength',
                            'work_experience_quality', 'timeline_consistency',
                            'soft_skills_indicators', 'design_layout'
                          ];
                          return standaloneCategories.includes(category) && score !== null;
                        } else {
                          // For job comparison, only show job-specific fields
                          const comparisonCategories = [
                            'keyword_match', 'skills_relevance', 'job_title_match',
                            'experience_alignment', 'education_fit', 'certifications',
                            'section_completeness', 'resume_formatting', 'grammar_clarity',
                            'overall_presentation'
                          ];
                          return comparisonCategories.includes(category) && score !== null;
                        }
                      })
                      .map(([category, score]) => (
                        <div key={category} className="category-item">
                          <div className="category-header">
                            <span className="category-name">
                              {category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </span>
                            <span className="category-score">{score}/100</span>
                          </div>
                          <div className="category-bar">
                            <div 
                              className="category-fill" 
                              style={{ 
                                width: `${score}%`,
                                backgroundColor: getScoreColor(score)
                              }}
                            ></div>
                          </div>
                        </div>
                      ))}
                  </div>
                </div>
              )}

              {/* Strengths & Weaknesses */}
              <div className="insights-grid">
                {/* Strengths */}
                <div className="insights-section strengths">
                  <h3>Strengths</h3>
                  <ul>
                    {scoringResults.strengths?.map((strength, index) => (
                      <li key={index}>{strength}</li>
                    ))}
                  </ul>
                </div>

                {/* Weaknesses */}
                <div className="insights-section weaknesses">
                  <h3>Areas for Improvement</h3>
                  <ul>
                    {scoringResults.weaknesses?.map((weakness, index) => (
                      <li key={index}>{weakness}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Recommendations */}
              {scoringResults.recommendations && (
                <div className="recommendations">
                  <h3>Recommendations</h3>
                  
                  {scoringResults.recommendations.high_priority && scoringResults.recommendations.high_priority.length > 0 && (
                    <div className="priority-section high-priority">
                      <h4>High Priority</h4>
                      <ul>
                        {scoringResults.recommendations.high_priority.map((rec, index) => (
                          <li key={index}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {scoringResults.recommendations.medium_priority && scoringResults.recommendations.medium_priority.length > 0 && (
                    <div className="priority-section medium-priority">
                      <h4>Medium Priority</h4>
                      <ul>
                        {scoringResults.recommendations.medium_priority.map((rec, index) => (
                          <li key={index}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {scoringResults.recommendations.low_priority && scoringResults.recommendations.low_priority.length > 0 && (
                    <div className="priority-section low-priority">
                      <h4>Nice to Have</h4>
                      <ul>
                        {scoringResults.recommendations.low_priority.map((rec, index) => (
                          <li key={index}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Keyword Analysis (for comparison mode) */}
              {scoringMode === 'comparison' && scoringResults.keyword_analysis && (
                <div className="keyword-analysis">
                  <h3>Keyword Analysis</h3>
                  <div className="keyword-stats">
                    <div className="stat-item">
                      <span className="stat-label">Keywords Matched</span>
                      <span className="stat-value">
                        {scoringResults.keyword_analysis.matched_keywords} / {scoringResults.keyword_analysis.total_job_keywords}
                      </span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Match Rate</span>
                      <span className="stat-value">{scoringResults.keyword_analysis.keyword_match_rate}%</span>
                    </div>
                  </div>

                  {scoringResults.keyword_analysis.critical_missing && scoringResults.keyword_analysis.critical_missing.length > 0 && (
                    <div className="missing-keywords">
                      <h4>Critical Missing Keywords</h4>
                      <div className="keyword-tags">
                        {scoringResults.keyword_analysis.critical_missing.map((keyword, index) => (
                          <span key={index} className="keyword-tag missing">{keyword}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {scoringResults.keyword_analysis.well_matched && scoringResults.keyword_analysis.well_matched.length > 0 && (
                    <div className="matched-keywords">
                      <h4>Well Matched Keywords</h4>
                      <div className="keyword-tags">
                        {scoringResults.keyword_analysis.well_matched.map((keyword, index) => (
                          <span key={index} className="keyword-tag matched">{keyword}</span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* ATS-Specific Analysis (for standalone mode) */}
              {scoringMode === 'standalone' && (
                <>
                  {/* Section Analysis */}
                  {scoringResults.section_analysis && (
                    <div className="section-analysis">
                      <h3>Section Analysis</h3>
                      <div className="section-grid">
                        {Object.entries(scoringResults.section_analysis).map(([section, status]) => (
                          <div key={section} className={`section-item ${status}`}>
                            <span className="section-name">
                              {section.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </span>
                            <span className={`section-status ${status}`}>
                              {status === 'present' ? '✓ Present' : 
                               status === 'missing' ? '✗ Missing' : 
                               status === 'incomplete' ? '⚠ Incomplete' : status}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}



                  {/* Content Analysis */}
                  {scoringResults.content_analysis && (
                    <div className="content-analysis">
                      <h3>Content Quality Analysis</h3>
                      <div className="content-grid">
                        {Object.entries(scoringResults.content_analysis).map(([aspect, score]) => (
                          <div key={aspect} className="content-item">
                            <div className="content-header">
                              <span className="content-name">
                                {aspect.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                              </span>
                              <span className="content-score">{score}/100</span>
                            </div>
                            <div className="content-bar">
                              <div 
                                className="content-fill" 
                                style={{ 
                                  width: `${score}%`,
                                  backgroundColor: getScoreColor(score)
                                }}
                              ></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ResumeScoring; 