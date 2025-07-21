import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../config/api.js';

const JobSearch = ({ sessionData, onJobSearchCompleted, loading, setLoading }) => {
  const [additionalKeywords, setAdditionalKeywords] = useState('');
  const [maxResults, setMaxResults] = useState(20);
  const [errors, setErrors] = useState({});
  
  // Skills management state
  const [editableSkills, setEditableSkills] = useState([]);
  const [newSkill, setNewSkill] = useState('');

  // Initialize skills from session data
  useEffect(() => {
    const extractedInfo = sessionData?.data?.extracted_info || {};
    const allSkills = extractedInfo.skills || [];
    setEditableSkills([...allSkills]);
  }, [sessionData]);

  // Skill management functions
  const addSkill = () => {
    if (newSkill.trim() && !editableSkills.includes(newSkill.trim())) {
      setEditableSkills([...editableSkills, newSkill.trim()]);
      setNewSkill('');
    }
  };

  const removeSkill = (skillToRemove) => {
    setEditableSkills(editableSkills.filter(skill => skill !== skillToRemove));
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addSkill();
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    try {
      const formData = new FormData();
      formData.append('session_id', sessionData.session_id);
      formData.append('additional_keywords', additionalKeywords);
      formData.append('max_results', maxResults);
      // Send updated skills list
      formData.append('updated_skills', JSON.stringify(editableSkills));

      const response = await fetch(API_ENDPOINTS.searchJobs(), {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        onJobSearchCompleted(result.data);
      } else {
        // Handle different error formats
        let errorMessage = 'Failed to search jobs. Please try again.';
        if (typeof result.detail === 'string') {
          errorMessage = result.detail;
        } else if (result.detail && Array.isArray(result.detail)) {
          // Handle FastAPI validation errors
          errorMessage = result.detail.map(err => `${err.loc?.join('.')}: ${err.msg}`).join(', ');
        } else if (result.message) {
          errorMessage = result.message;
        }
        setErrors({ search: errorMessage });
      }
    } catch (error) {
      console.error('Search error:', error);
      setErrors({ search: 'Network error. Please check your connection and try again.' });
    } finally {
      setLoading(false);
    }
  };

  const extractedInfo = sessionData?.data?.extracted_info || {};
  const preferences = sessionData?.data?.preferences || {};

  return (
    <div className="job-search">
      <div className="search-container">
        <div className="search-header">
          <h2 className="search-title">
            <span className="search-icon">🔍</span>
            Search for Jobs
          </h2>
          <p className="search-subtitle">
            Based on your resume analysis, we'll find the best matching opportunities
          </p>
        </div>

        {/* Resume Analysis Summary */}
        <div className="analysis-summary">
          <h3 className="summary-title">
            <span className="summary-icon">🧠</span>
            AI Resume Analysis
          </h3>
          
          <div className="summary-grid">
            <div className="summary-card">
              <div className="card-header">
                <span className="card-icon">💼</span>
                <h4>Target Role</h4>
              </div>
              <p className="card-value">
                {extractedInfo.role || 'Not specified'}
              </p>
            </div>

            <div className="summary-card skills-card">
              <div className="card-header">
                <span className="card-icon">🛠️</span>
                <h4>Your Skills</h4>
                <span className="edit-hint">Click ✕ to remove • Add new skills below</span>
              </div>
              <p className="card-value">
                {editableSkills.length} skills for job matching
              </p>
              
              {/* Editable Skills Display */}
              <div className="skills-editor">
                <div className="skills-list">
                  {editableSkills.map((skill, index) => (
                    <span key={index} className="skill-tag editable">
                      {skill}
                      <button 
                        className="remove-skill"
                        onClick={() => removeSkill(skill)}
                        title="Remove skill"
                      >
                        ✕
                      </button>
                    </span>
                  ))}
                  {editableSkills.length === 0 && (
                    <p className="no-skills">No skills selected. Add some skills below to improve job matching.</p>
                  )}
                </div>
                
                {/* Add New Skill */}
                <div className="add-skill-section">
                  <div className="add-skill-input">
                    <input
                      type="text"
                      placeholder="Add a skill (e.g., Python, React, Machine Learning)"
                      value={newSkill}
                      onChange={(e) => setNewSkill(e.target.value)}
                      onKeyPress={handleKeyPress}
                      className="skill-input"
                    />
                    <button 
                      className="btn btn-outline btn-small"
                      onClick={addSkill}
                      disabled={!newSkill.trim()}
                    >
                      Add
                    </button>
                  </div>
                  <p className="add-skill-hint">
                    💡 Add technical skills, tools, programming languages, or frameworks that match your target jobs
                  </p>
                </div>
              </div>
            </div>

            <div className="summary-card">
              <div className="card-header">
                <span className="card-icon">📍</span>
                <h4>Location</h4>
              </div>
              <p className="card-value">
                {preferences.location || 'Not specified'}
              </p>
            </div>

            <div className="summary-card">
              <div className="card-header">
                <span className="card-icon">⏱️</span>
                <h4>Experience Level</h4>
              </div>
              <p className="card-value">
                {preferences.experience_level?.charAt(0).toUpperCase() + preferences.experience_level?.slice(1) || 'Not specified'}
              </p>
            </div>
          </div>

          <div className="preferences-summary">
            <h4>Job Preferences</h4>
            <div className="preference-tags">
              <span className="preference-tag">
                <span className="tag-icon">💻</span>
                {preferences.job_type?.charAt(0).toUpperCase() + preferences.job_type?.slice(1).replace('-', ' ') || 'Full-time'}
              </span>
              <span className="preference-tag">
                <span className="tag-icon">🏠</span>
                {preferences.remote_preference?.charAt(0).toUpperCase() + preferences.remote_preference?.slice(1) || 'Hybrid'}
              </span>
            </div>
          </div>
        </div>

        {/* AI Suggested Roles */}
        {sessionData?.data?.ai_suggestions && (
          <div className="ai-suggestions">
            <h3 className="suggestions-title">
              <span className="suggestions-icon">🤖</span>
              AI-Suggested Roles
            </h3>
            <p className="suggestions-subtitle">
              Based on your skills and experience, here are the roles AI thinks you're best suited for:
            </p>
            
            <div className="suggestions-grid">
              {/* Primary Roles */}
              {sessionData.data.ai_suggestions.primary_roles?.length > 0 && (
                <div className="suggestion-category">
                  <h4 className="category-title">
                    <span className="category-icon">🎯</span>
                    Best Matches
                  </h4>
                  <div className="roles-list">
                    {sessionData.data.ai_suggestions.primary_roles.map((role, index) => (
                      <span key={index} className="role-tag primary">
                        {role}
                        <button 
                          className="add-role-btn"
                          onClick={() => setAdditionalKeywords(prev => 
                            prev ? `${prev}, ${role}` : role
                          )}
                          title="Add to search keywords"
                        >
                          +
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Secondary Roles */}
              {sessionData.data.ai_suggestions.secondary_roles?.length > 0 && (
                <div className="suggestion-category">
                  <h4 className="category-title">
                    <span className="category-icon">🔄</span>
                    Alternative Options
                  </h4>
                  <div className="roles-list">
                    {sessionData.data.ai_suggestions.secondary_roles.map((role, index) => (
                      <span key={index} className="role-tag secondary">
                        {role}
                        <button 
                          className="add-role-btn"
                          onClick={() => setAdditionalKeywords(prev => 
                            prev ? `${prev}, ${role}` : role
                          )}
                          title="Add to search keywords"
                        >
                          +
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Skill Domains */}
              {sessionData.data.ai_suggestions.skill_domains?.length > 0 && (
                <div className="suggestion-category full-width">
                  <h4 className="category-title">
                    <span className="category-icon">🏗️</span>
                    Your Skill Domains
                  </h4>
                  <div className="domains-list">
                    {sessionData.data.ai_suggestions.skill_domains.map((domain, index) => (
                      <div key={index} className="domain-card">
                        <h5 className="domain-name">{domain.domain}</h5>
                        <p className="domain-confidence">
                          Confidence: <span className={`confidence ${domain.confidence}`}>
                            {domain.confidence}
                          </span>
                        </p>
                        <div className="domain-skills">
                          {domain.matching_skills?.slice(0, 4).map((skill, skillIndex) => (
                            <span key={skillIndex} className="domain-skill">
                              {skill}
                            </span>
                          ))}
                          {domain.matching_skills?.length > 4 && (
                            <span className="more-skills">
                              +{domain.matching_skills.length - 4} more
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Strongest Domain Summary */}
              {sessionData.data.ai_suggestions.strongest_domain && (
                <div className="suggestion-category full-width">
                  <div className="strongest-domain">
                    <h4 className="category-title">
                      <span className="category-icon">💪</span>
                      Your Strongest Domain
                    </h4>
                    <p className="strongest-domain-text">
                      <strong>{sessionData.data.ai_suggestions.strongest_domain}</strong>
                      {sessionData.data.ai_suggestions.cross_domain_potential && (
                        <span className="cross-domain">
                          • {sessionData.data.ai_suggestions.cross_domain_potential}
                        </span>
                      )}
                    </p>
                  </div>
                </div>
              )}
            </div>
            
            <div className="suggestions-hint">
              <p>💡 Click the + button next to any role to add it to your search keywords</p>
            </div>
          </div>
        )}

        {/* Search Configuration */}
        <div className="search-configuration">
          <h3 className="config-title">
            <span className="config-icon">⚙️</span>
            Search Configuration
          </h3>
          
          <form onSubmit={handleSearch} className="search-form">
            <div className="form-group">
              <label htmlFor="additionalKeywords">
                Additional Keywords (Optional)
                <span className="label-hint">Add specific skills, technologies, or job titles</span>
              </label>
              <input
                type="text"
                id="additionalKeywords"
                value={additionalKeywords}
                onChange={(e) => setAdditionalKeywords(e.target.value)}
                placeholder="e.g., React, Python, Machine Learning, Product Manager"
                className="keyword-input"
              />
              <small className="input-help">
                Separate multiple keywords with commas. These will be added to your profile-based search.
              </small>
            </div>

            <div className="form-group">
              <label htmlFor="maxResults">
                Maximum Results
                <span className="label-hint">How many job listings to search for</span>
              </label>
              <select
                id="maxResults"
                value={maxResults}
                onChange={(e) => setMaxResults(parseInt(e.target.value))}
                className="results-select"
              >
                <option value={10}>10 results</option>
                <option value={20}>20 results</option>
                <option value={30}>30 results</option>
                <option value={50}>50 results</option>
              </select>
            </div>

            {errors.search && (
              <div className="error-banner">
                <span className="error-icon">⚠️</span>
                {errors.search}
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
                  Searching Jobs...
                </>
              ) : (
                <>
                  <span>🚀</span>
                  Start Job Search
                </>
              )}
            </button>
          </form>
        </div>

        {/* Search Preview */}
        <div className="search-preview">
          <h4 className="preview-title">
            <span className="preview-icon">👀</span>
            Search Preview
          </h4>
          <div className="preview-content">
            <p className="preview-text">
              We'll search for <strong>"{extractedInfo.role || 'jobs'}"</strong> positions
              {additionalKeywords && (
                <span> with additional keywords: <strong>"{additionalKeywords}"</strong></span>
              )}
              {' '}in <strong>{preferences.location}</strong> area, 
              focusing on <strong>{preferences.job_type?.replace('-', ' ')}</strong> opportunities
              with <strong>{preferences.remote_preference}</strong> work arrangements.
            </p>
            <p className="preview-note">
              Our AI will rank the results based on your skills and experience to show the most relevant matches first.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobSearch; 