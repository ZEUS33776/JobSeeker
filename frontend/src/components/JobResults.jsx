import React, { useState } from 'react';

const JobResults = ({ jobResults, sessionData, onBackToSearch, loading, setLoading }) => {
  const [expandedJobs, setExpandedJobs] = useState(new Set());
  const [fetchingDescriptions, setFetchingDescriptions] = useState(new Set());
  const [jobDescriptions, setJobDescriptions] = useState(new Map());
  const [errors, setErrors] = useState({});
  
  // Job Description Analysis State (per job)
  const [manualJobDescriptions, setManualJobDescriptions] = useState(new Map()); // jobIndex -> description text
  const [analyzingJobs, setAnalyzingJobs] = useState(new Set()); // jobIndex set
  const [analysisResults, setAnalysisResults] = useState(new Map()); // jobIndex -> analysis result
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [currentAnalysisJob, setCurrentAnalysisJob] = useState(null);

  const getSourceLogo = (source) => {
    const logoMap = {
      'linkedin.com': '💼',
      'indeed.com': '🔵',
      'naukri.com': '🔴',
      'internshala.com': '🟡',
      'wellfound.com': '🚀'
    };
    return logoMap[source] || '🌐';
  };

  const getSourceColor = (source) => {
    const colorMap = {
      'linkedin.com': '#0077B5',
      'indeed.com': '#2164f3',
      'naukri.com': '#ef4444',
      'internshala.com': '#f59e0b',
      'wellfound.com': '#8b5cf6'
    };
    return colorMap[source] || '#6b7280';
  };

  const getScoreColor = (score) => {
    if (score >= 85) return '#22c55e'; // green
    if (score >= 70) return '#eab308'; // yellow
    if (score >= 60) return '#f97316'; // orange
    return '#ef4444'; // red
  };

  const toggleJobExpansion = (jobIndex) => {
    const newExpanded = new Set(expandedJobs);
    if (newExpanded.has(jobIndex)) {
      newExpanded.delete(jobIndex);
    } else {
      newExpanded.add(jobIndex);
    }
    setExpandedJobs(newExpanded);
  };

  const fetchJobDescription = async (job, jobIndex) => {
    if (fetchingDescriptions.has(jobIndex) || jobDescriptions.has(jobIndex)) {
      return;
    }

    setFetchingDescriptions(prev => new Set([...prev, jobIndex]));
    setErrors(prev => ({ ...prev, [`job_${jobIndex}`]: null }));

    try {
      const formData = new FormData();
      formData.append('job_url', job.url);
      formData.append('session_id', sessionData.session_id);

      const response = await fetch('http://localhost:8000/fetch-job-description', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        setJobDescriptions(prev => new Map([...prev, [jobIndex, result.data]]));
        // Auto-expand the job card to show the description
        setExpandedJobs(prev => new Set([...prev, jobIndex]));
      } else {
        setErrors(prev => ({ 
          ...prev, 
          [`job_${jobIndex}`]: result.error || 'Failed to fetch job description' 
        }));
      }
    } catch (error) {
      console.error('Fetch description error:', error);
      setErrors(prev => ({ 
        ...prev, 
        [`job_${jobIndex}`]: 'Network error. Please try again.' 
      }));
    } finally {
      setFetchingDescriptions(prev => {
        const newSet = new Set(prev);
        newSet.delete(jobIndex);
        return newSet;
      });
    }
  };

  const analyzeJobDescription = async (jobIndex, job) => {
    const jobDescription = manualJobDescriptions.get(jobIndex) || '';
    
    if (!jobDescription.trim()) {
      setErrors(prev => ({ ...prev, [`analysis_${jobIndex}`]: 'Please enter a job description.' }));
      return;
    }

    if (jobDescription.trim().length < 50) {
      setErrors(prev => ({ ...prev, [`analysis_${jobIndex}`]: 'Job description is too short. Please provide more details.' }));
      return;
    }

    setAnalyzingJobs(prev => new Set([...prev, jobIndex]));
    setErrors(prev => ({ ...prev, [`analysis_${jobIndex}`]: null }));

    try {
      const formData = new FormData();
      formData.append('session_id', sessionData.session_id);
      formData.append('job_description', jobDescription);

      const response = await fetch('http://localhost:8000/analyze-resume-vs-job', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        // Store analysis result for this specific job
        setAnalysisResults(prev => new Map([...prev, [jobIndex, { ...result.data, job }]]));
        setCurrentAnalysisJob({ index: jobIndex, job, analysis: result.data });
        setShowAnalysisModal(true);
      } else {
        setErrors(prev => ({ 
          ...prev, 
          [`analysis_${jobIndex}`]: result.error || 'Failed to analyze resume. Please try again.' 
        }));
      }
    } catch (error) {
      console.error('Analysis error:', error);
      setErrors(prev => ({ 
        ...prev, 
        [`analysis_${jobIndex}`]: 'Network error. Please check your connection and try again.' 
      }));
    } finally {
      setAnalyzingJobs(prev => {
        const newSet = new Set(prev);
        newSet.delete(jobIndex);
        return newSet;
      });
    }
  };

  const updateJobDescription = (jobIndex, description) => {
    setManualJobDescriptions(prev => new Map([...prev, [jobIndex, description]]));
  };

  // Fit level helper functions
  const getFitLevelText = (fitLevel) => {
    if (typeof fitLevel === 'string') {
      const levelMap = {
        'excellent_fit': 'Excellent Fit',
        'very_good_fit': 'Very Good Fit',
        'good_fit': 'Good Fit',
        'moderate_fit': 'Moderate Fit',
        'poor_fit': 'Poor Fit',
        'not_a_fit': 'Not a Fit'
      };
      return levelMap[fitLevel] || 'Unknown Fit';
    }
    
    // Fallback for score-based classification
    const score = fitLevel;
    if (score >= 90) return 'Excellent Fit';
    if (score >= 75) return 'Very Good Fit';
    if (score >= 60) return 'Good Fit';
    if (score >= 40) return 'Moderate Fit';
    if (score >= 20) return 'Poor Fit';
    return 'Not a Fit';
  };

  const getFitLevelClass = (fitLevel) => {
    if (typeof fitLevel === 'string') {
      const classMap = {
        'excellent_fit': 'excellent',
        'very_good_fit': 'very-good',
        'good_fit': 'good',
        'moderate_fit': 'moderate',
        'poor_fit': 'poor',
        'not_a_fit': 'not-fit'
      };
      return classMap[fitLevel] || 'unknown';
    }
    
    // Fallback for score-based classification
    const score = fitLevel;
    if (score >= 90) return 'excellent';
    if (score >= 75) return 'very-good';
    if (score >= 60) return 'good';
    if (score >= 40) return 'moderate';
    if (score >= 20) return 'poor';
    return 'not-fit';
  };

  const getFitDescription = (fitLevel) => {
    if (typeof fitLevel === 'string') {
      const descMap = {
        'excellent_fit': 'Outstanding match! Your resume aligns exceptionally well with this job.',
        'very_good_fit': 'Strong match with only minor gaps. Great opportunity!',
        'good_fit': 'Solid match with some room for improvement.',
        'moderate_fit': 'Reasonable match but significant optimization needed.',
        'poor_fit': 'Limited alignment. Major improvements required.',
        'not_a_fit': 'Very little alignment. Consider other opportunities.'
      };
      return descMap[fitLevel] || 'Analysis completed.';
    }
    
    // Fallback for score-based descriptions
    const score = fitLevel;
    if (score >= 90) return 'Outstanding match! Your resume aligns exceptionally well with this job.';
    if (score >= 75) return 'Strong match with only minor gaps. Great opportunity!';
    if (score >= 60) return 'Solid match with some room for improvement.';
    if (score >= 40) return 'Reasonable match but significant optimization needed.';
    if (score >= 20) return 'Limited alignment. Major improvements required.';
    return 'Very little alignment. Consider other opportunities.';
  };

  const jobs = jobResults.jobs || [];
  const summary = jobResults.summary || {};

  return (
    <div className="job-results">
      <div className="results-container">
        {/* Results Header */}
        <div className="results-header">
          <div className="header-main">
            <h2 className="results-title">
              <span className="results-icon">🎯</span>
              Your Job Matches
            </h2>
            <button 
              className="btn btn-outline"
              onClick={onBackToSearch}
            >
              <span>🔍</span>
              New Search
            </button>
          </div>
          
          <div className="results-stats">
            <div className="stat-item">
              <span className="stat-value">{jobs.length}</span>
              <span className="stat-label">Relevant Jobs</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{summary.high_relevance || 0}</span>
              <span className="stat-label">High Match</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{summary.medium_relevance || 0}</span>
              <span className="stat-label">Good Match</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{summary.total_jobs || 0}</span>
              <span className="stat-label">Total Found</span>
            </div>
          </div>
        </div>

        {/* Job Listings */}
        <div className="job-listings">
          {jobs.length === 0 ? (
            <div className="no-results">
              <div className="no-results-icon">😔</div>
              <h3>No matching jobs found</h3>
              <p>Try adjusting your search criteria or adding different keywords.</p>
              <button className="btn btn-primary" onClick={onBackToSearch}>
                <span>🔍</span>
                Refine Search
              </button>
            </div>
          ) : (
            jobs.map((job, index) => {
              const isExpanded = expandedJobs.has(index);
              const isFetching = fetchingDescriptions.has(index);
              const hasDescription = jobDescriptions.has(index);
              const description = jobDescriptions.get(index);
              const error = errors[`job_${index}`];

              return (
                <div key={index} className={`job-card ${isExpanded ? 'expanded' : ''}`}>
                  {/* Job Header */}
                  <div className="job-header">
                    <div className="job-main-info">
                      <div className="job-title-row">
                        <h3 className="job-title">
                          <a 
                            href={job.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="job-link"
                          >
                            {job.title}
                          </a>
                        </h3>
                        <div className="job-score" style={{ backgroundColor: getScoreColor(job.score) }}>
                          {job.score}%
                        </div>
                      </div>
                      
                      <div className="job-meta">
                        <div className="job-source" style={{ borderLeftColor: getSourceColor(job.source) }}>
                          <span 
                            className="source-logo"
                            style={{ color: getSourceColor(job.source) }}
                          >
                            {getSourceLogo(job.source)}
                          </span>
                          <span className="source-name">{job.source}</span>
                        </div>
                      </div>
                    </div>

                    <div className="job-actions">
                      <button
                        className={`btn btn-outline btn-small ${hasDescription ? 'btn-success' : ''}`}
                        onClick={() => fetchJobDescription(job, index)}
                        disabled={isFetching || hasDescription}
                        title={hasDescription ? 'Description already fetched' : 'Fetch full job description'}
                      >
                        {isFetching ? (
                          <>
                            <span className="spinner-small"></span>
                            Fetching...
                          </>
                        ) : hasDescription ? (
                          <>
                            <span>✅</span>
                            Fetched
                          </>
                        ) : (
                          <>
                            <span>📄</span>
                            Fetch Description
                          </>
                        )}
                      </button>
                      
                      <button
                        className="btn btn-ghost btn-small"
                        onClick={() => toggleJobExpansion(index)}
                      >
                        <span>{isExpanded ? '🔼' : '🔽'}</span>
                      </button>
                    </div>
                  </div>

                  {/* Job Preview/Snippet */}
                  <div className="job-preview">
                    <p className="job-snippet">{job.snippet}</p>
                    
                    {job.skill_matches && job.skill_matches.length > 0 && (
                      <div className="skill-matches">
                        <span className="skill-matches-label">Matching Skills:</span>
                        <div className="skill-matches-list">
                          {job.skill_matches.map((skill, skillIndex) => (
                            <span key={skillIndex} className="skill-match-tag">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {job.reasons && job.reasons.length > 0 && (
                      <div className="job-reasons">
                        <span className="reasons-label">Why this matches:</span>
                        <ul className="reasons-list">
                          {job.reasons.map((reason, reasonIndex) => (
                            <li key={reasonIndex} className="reason-item">
                              {reason}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  {/* Expanded Content */}
                  {isExpanded && (
                    <div className="job-expanded">
                      {error && (
                        <div className="error-message">
                          <span className="error-icon">⚠️</span>
                          {error}
                        </div>
                      )}

                      {hasDescription && description && (
                        <div className="job-description">
                          <h4 className="description-title">
                            <span className="description-icon">📋</span>
                            Full Job Description
                          </h4>
                          
                          <div className="description-meta">
                            <div className="meta-item">
                              <strong>Title:</strong> {description.title || 'Not specified'}
                            </div>
                            <div className="meta-item">
                              <strong>Company:</strong> {description.company || 'Not specified'}
                            </div>
                            <div className="meta-item">
                              <strong>Location:</strong> {description.location || 'Not specified'}
                            </div>
                            <div className="meta-item">
                              <strong>Fetched:</strong> {new Date(description.fetched_at).toLocaleString()}
                            </div>
                          </div>

                          <div className="description-content">
                            <p>{description.description}</p>
                          </div>
                        </div>
                      )}

                      {/* Manual Job Description Analysis Section */}
                      <div className="manual-analysis-section">
                        <h4 className="analysis-section-title">
                          <span className="analysis-icon">🎯</span>
                          {hasDescription && description ? 'Alternative Analysis' : 'Manual Job Description Analysis'}
                        </h4>
                        <p className="analysis-section-subtitle">
                          {hasDescription && description 
                            ? 'Paste a more detailed or updated job description for better analysis'
                            : 'Paste the job description here to analyze how well your resume matches this position'
                          }
                        </p>

                        <div className="manual-description-form">
                          <div className="form-group">
                            <label htmlFor={`manual-desc-${index}`} className="form-label">
                              Job Description
                            </label>
                            <textarea
                              id={`manual-desc-${index}`}
                              className="form-textarea manual-desc-textarea"
                              rows="6"
                              placeholder="Paste the complete job description here including requirements, responsibilities, and qualifications..."
                              value={manualJobDescriptions.get(index) || ''}
                              onChange={(e) => updateJobDescription(index, e.target.value)}
                              disabled={analyzingJobs.has(index)}
                            />
                            <div className="char-count">
                              {(manualJobDescriptions.get(index) || '').length} characters
                            </div>
                          </div>

                          {errors[`analysis_${index}`] && (
                            <div className="error-message">
                              <span className="error-icon">⚠️</span>
                              {errors[`analysis_${index}`]}
                            </div>
                          )}

                          <div className="analysis-actions">
                            <button 
                              className="btn btn-primary"
                              onClick={() => analyzeJobDescription(index, job)}
                              disabled={analyzingJobs.has(index) || !(manualJobDescriptions.get(index) || '').trim()}
                            >
                              {analyzingJobs.has(index) ? (
                                <>
                                  <span className="spinner"></span>
                                  Analyzing...
                                </>
                              ) : (
                                <>
                                  <span>📊</span>
                                  Analyze Resume Match
                                </>
                              )}
                            </button>

                            {analysisResults.has(index) && (
                              <button 
                                className="btn btn-outline"
                                onClick={() => {
                                  setCurrentAnalysisJob({ 
                                    index, 
                                    job, 
                                    analysis: analysisResults.get(index) 
                                  });
                                  setShowAnalysisModal(true);
                                }}
                              >
                                <span>👁️</span>
                                View Last Analysis
                              </button>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>



        {/* Results Footer */}
        {jobs.length > 0 && (
          <div className="results-footer">
            <div className="footer-stats">
              <p>
                Showing {jobs.length} most relevant jobs out of {summary.total_jobs || 0} found.
                Results ranked by AI based on your profile.
              </p>
            </div>
            <button className="btn btn-outline" onClick={onBackToSearch}>
              <span>🔍</span>
              Search Again
            </button>
          </div>
        )}

        {/* Analysis Results Modal */}
        {showAnalysisModal && currentAnalysisJob && (
          <div className="modal-overlay" onClick={() => setShowAnalysisModal(false)}>
            <div className="modal-content analysis-modal" onClick={(e) => e.stopPropagation()}>
              <div className="modal-header">
                <div className="modal-title-section">
                  <h3 className="modal-title">
                    <span className="modal-icon">📊</span>
                    Resume Analysis Results
                  </h3>
                  <div className="modal-job-info">
                    <p className="job-title-small">{currentAnalysisJob.job.title}</p>
                    <p className="job-company-small">{currentAnalysisJob.job.source}</p>
                  </div>
                </div>
                <button 
                  className="modal-close"
                  onClick={() => setShowAnalysisModal(false)}
                >
                  ✕
                </button>
              </div>

              <div className="modal-body">
                {/* Overall Score */}
                <div className="analysis-overview">
                  <div className="score-card">
                    <div className="score-circle">
                      <span className="score-value">{currentAnalysisJob.analysis.overall_score || 0}%</span>
                    </div>
                    <h4 className="score-title">Overall Match Score</h4>
                                         <div className="fit-level">
                       <span className={`fit-badge ${getFitLevelClass(currentAnalysisJob.analysis.fit_level || currentAnalysisJob.analysis.overall_score)}`}>
                         {getFitLevelText(currentAnalysisJob.analysis.fit_level || currentAnalysisJob.analysis.overall_score)}
                       </span>
                     </div>
                     <p className="score-description">
                       {getFitDescription(currentAnalysisJob.analysis.fit_level || currentAnalysisJob.analysis.overall_score)}
                     </p>
                  </div>
                </div>

                                 {/* Category Breakdown */}
                 {currentAnalysisJob.analysis.category_breakdown && (
                   <div className="category-breakdown">
                     <h4>Match Breakdown</h4>
                     <div className="category-grid">
                       {Object.entries(currentAnalysisJob.analysis.category_breakdown).map(([category, score]) => (
                        <div key={category} className="category-item">
                          <div className="category-label">
                            {category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </div>
                          <div className="category-score">
                            <div 
                              className="score-bar" 
                              style={{ 
                                width: `${score}%`,
                                backgroundColor: getScoreColor(score)
                              }}
                            ></div>
                            <span className="score-text">{score}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                                 {/* Strengths */}
                 {currentAnalysisJob.analysis.strengths && currentAnalysisJob.analysis.strengths.length > 0 && (
                   <div className="analysis-section strengths-section">
                     <h4 className="section-title">
                       <span className="section-icon">✅</span>
                       Strengths
                     </h4>
                     <ul className="analysis-list">
                       {currentAnalysisJob.analysis.strengths.map((strength, index) => (
                        <li key={index} className="analysis-item positive">
                          {strength}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                                 {/* Weaknesses */}
                 {currentAnalysisJob.analysis.weaknesses && currentAnalysisJob.analysis.weaknesses.length > 0 && (
                   <div className="analysis-section weaknesses-section">
                     <h4 className="section-title">
                       <span className="section-icon">⚠️</span>
                       Areas for Improvement
                     </h4>
                     <ul className="analysis-list">
                       {currentAnalysisJob.analysis.weaknesses.map((weakness, index) => (
                        <li key={index} className="analysis-item warning">
                          {weakness}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                                 {/* Missing Keywords */}
                 {currentAnalysisJob.analysis.missing_keywords && currentAnalysisJob.analysis.missing_keywords.length > 0 && (
                   <div className="analysis-section keywords-section">
                     <h4 className="section-title">
                       <span className="section-icon">🔑</span>
                       Missing Keywords
                     </h4>
                     <div className="keywords-grid">
                       {currentAnalysisJob.analysis.missing_keywords.map((keyword, index) => (
                        <span key={index} className="keyword-tag missing">
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                                 {/* ATS Optimization */}
                 {currentAnalysisJob.analysis.ats_optimization && currentAnalysisJob.analysis.ats_optimization.length > 0 && (
                   <div className="analysis-section optimization-section">
                     <h4 className="section-title">
                       <span className="section-icon">🎯</span>
                       ATS Optimization Tips
                     </h4>
                     <ul className="analysis-list">
                       {currentAnalysisJob.analysis.ats_optimization.map((tip, index) => (
                        <li key={index} className="analysis-item info">
                          {tip}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                                 {/* Action Items */}
                 {currentAnalysisJob.analysis.action_items && currentAnalysisJob.analysis.action_items.length > 0 && (
                   <div className="analysis-section action-items-section">
                     <h4 className="section-title">
                       <span className="section-icon">📝</span>
                       Action Items
                     </h4>
                     <ul className="analysis-list">
                       {currentAnalysisJob.analysis.action_items.map((action, index) => (
                        <li key={index} className="analysis-item action">
                          {action}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                                 {/* Keyword Analysis */}
                 {currentAnalysisJob.analysis.keyword_analysis && (
                   <div className="analysis-section keyword-analysis-section">
                     <h4 className="section-title">
                       <span className="section-icon">📈</span>
                       Keyword Analysis
                     </h4>
                     <div className="keyword-stats">
                       <div className="stat-item">
                         <span className="stat-value">{currentAnalysisJob.analysis.keyword_analysis.matched_keywords || 0}</span>
                         <span className="stat-label">Matched Keywords</span>
                       </div>
                       <div className="stat-item">
                         <span className="stat-value">{currentAnalysisJob.analysis.keyword_analysis.total_job_keywords || 0}</span>
                         <span className="stat-label">Total Job Keywords</span>
                       </div>
                       <div className="stat-item">
                         <span className="stat-value">{currentAnalysisJob.analysis.keyword_analysis.keyword_match_rate || 0}%</span>
                         <span className="stat-label">Match Rate</span>
                       </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="modal-footer">
                <button 
                  className="btn btn-outline"
                  onClick={() => setShowAnalysisModal(false)}
                >
                  Close
                </button>
                <button 
                  className="btn btn-primary"
                                     onClick={() => {
                     // Copy action items to clipboard
                     const actionText = currentAnalysisJob.analysis.action_items?.join('\n') || '';
                     navigator.clipboard.writeText(actionText);
                   }}
                >
                  <span>📋</span>
                  Copy Action Items
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default JobResults; 