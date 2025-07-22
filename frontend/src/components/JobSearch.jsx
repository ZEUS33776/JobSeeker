import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS, buildApiUrl } from '../config/api.js';
import './JobSearch.css';

const JobSearch = ({ sessionData, onJobSearchCompleted, loading, setLoading }) => {
  // Form state
  const [locations, setLocations] = useState('');
  const [selectedRoles, setSelectedRoles] = useState([]); // Array of roles
  const [experienceLevel, setExperienceLevel] = useState('entry');
  const [jobType, setJobType] = useState('full-time');
  const [remotePreference, setRemotePreference] = useState('hybrid');
  const [maxResults, setMaxResults] = useState(20);
  const [searchScope, setSearchScope] = useState('job_boards'); // Add search scope state
  const [errors, setErrors] = useState({});
  const [analyzing, setAnalyzing] = useState(false);
  const [customRole, setCustomRole] = useState('');
  const [showCustomRole, setShowCustomRole] = useState(false);
  
  // Analysis state
  const [extractedSkills, setExtractedSkills] = useState([]);
  const [domainAnalysis, setDomainAnalysis] = useState(null);
  const [selectedDomain, setSelectedDomain] = useState(null);
  const [recommendedRoles, setRecommendedRoles] = useState([]); // All unique roles from LLM
  const [llmExtracted, setLlmExtracted] = useState({}); // Store all extracted info from LLM

  // Fetch LLM-driven domain/role analysis from backend
  useEffect(() => {
    const fetchDomains = async () => {
      if (!sessionData?.session_id) return;
      setAnalyzing(true);
      try {
        const formData = new FormData();
        formData.append('session_id', sessionData.session_id);
        const response = await fetch(buildApiUrl('/resume/extract-domains'), {
          method: 'POST',
          body: formData
        });
        const result = await response.json();
        if (result.success && result.data) {
          // Save all extracted info for display
          setLlmExtracted(result.data);
          // Use LLM result for domains and roles
          const llmDomains = result.data.identified_domains || [];
          const llmRoles = result.data.suggested_roles || [];
          const primaryRoles = result.data.primary_role_recommendations || [];
          const secondaryRoles = result.data.secondary_role_options || [];

          // Build a set of all unique roles (from suggested_roles, primary, secondary)
          const allRolesSet = new Set();
          llmRoles.forEach(r => allRolesSet.add(r.role));
          primaryRoles.forEach(r => allRolesSet.add(r));
          secondaryRoles.forEach(r => allRolesSet.add(r));
          const allRoles = Array.from(allRolesSet);
          setRecommendedRoles(allRoles);

          // Map roles to domains (if possible)
          setDomainAnalysis(
            llmDomains.map(domain => {
              // Find all roles (from suggested_roles) that match this domain
              const domainRoles = llmRoles
                .filter(role => role.domain === domain.domain)
                .map(role => role.role);
              return {
                name: domain.domain,
                roles: domainRoles,
                skills: domain.matching_skills,
                confidence: domain.confidence
              };
            })
          );
          // Set extracted skills for display
          const allSkills = llmDomains.flatMap(d => d.matching_skills);
          setExtractedSkills([...new Set(allSkills)]);
        } else {
          setDomainAnalysis([]);
          setExtractedSkills([]);
          setRecommendedRoles([]);
          setLlmExtracted({});
        }
        // Pre-fill form from session data
        const preferences = sessionData?.data?.preferences || {};
        if (preferences.location) setLocations(preferences.location);
        if (preferences.job_type) setJobType(preferences.job_type);
        if (preferences.remote_preference) setRemotePreference(preferences.remote_preference);
      } catch (error) {
        setDomainAnalysis([]);
        setExtractedSkills([]);
        setRecommendedRoles([]);
        setLlmExtracted({});
      } finally {
        setAnalyzing(false);
      }
    };
    fetchDomains();
  }, [sessionData]);

  const handleDomainSelect = (domain) => {
    setSelectedDomain(domain);
  };

  // Toggle role selection
  const handleRoleToggle = (role) => {
    setSelectedRoles(prev =>
      prev.includes(role)
        ? prev.filter(r => r !== role)
        : [...prev, role]
    );
    setShowCustomRole(false);
  };

  // Add custom role to selection
  const handleCustomRoleSubmit = () => {
    if (customRole.trim() && !selectedRoles.includes(customRole.trim())) {
      setSelectedRoles(prev => [...prev, customRole.trim()]);
      setShowCustomRole(false);
      setCustomRole('');
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    // Validate inputs
    const newErrors = {};
    if (!locations.trim()) newErrors.locations = 'Please enter at least one location';
    if (!selectedRoles.length) newErrors.roles = 'Please select or enter at least one role';
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    setLoading(true);
    setErrors({});
    try {
      const formData = new FormData();
      formData.append('session_id', sessionData.session_id);
      formData.append('locations', locations);
      formData.append('desired_roles', selectedRoles.join(', '));
      formData.append('experience_level', experienceLevel);
      formData.append('job_type', jobType);
      formData.append('remote_preference', remotePreference);
      formData.append('max_results', maxResults);
      formData.append('search_scope', searchScope); // Add search scope to form data
      const response = await fetch(API_ENDPOINTS.searchJobs(), {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();
      if (result.success) {
        onJobSearchCompleted(result.data);
      } else {
        setErrors({ search: result.detail || 'Failed to search jobs. Please try again.' });
      }
    } catch (error) {
      setErrors({ search: 'Network error. Please check your connection and try again.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="job-search">
      {/* Job Preferences Form */}
      <div className="search-section job-preferences">
        <h3>
          <span className="section-icon">⚙️</span>
          Job Search Preferences
          {analyzing && <span className="analyzing-spinner">Analyzing resume...</span>}
        </h3>
        <form onSubmit={handleSearch} className="search-form">
          {/* Locations */}
          <div className="form-group">
            <label>
              Locations
              <span className="label-hint">Enter one or more locations (comma-separated)</span>
            </label>
            <input
              type="text"
              value={locations}
              onChange={(e) => setLocations(e.target.value)}
              placeholder="e.g., Bengaluru, Mumbai, Remote"
              className={errors.locations ? 'error' : ''}
            />
            {errors.locations && <span className="error-text">{errors.locations}</span>}
          </div>
          {/* Experience Level */}
          <div className="form-row">
            <div className="form-group">
              <label>Experience Level</label>
              <select value={experienceLevel} onChange={(e) => setExperienceLevel(e.target.value)}>
                <option value="entry">Entry Level</option>
                <option value="mid">Mid Level</option>
                <option value="senior">Senior Level</option>
              </select>
            </div>
            <div className="form-group">
              <label>Job Type</label>
              <select value={jobType} onChange={(e) => setJobType(e.target.value)}>
                <option value="full-time">Full Time</option>
                <option value="part-time">Part Time</option>
                <option value="contract">Contract</option>
                <option value="internship">Internship</option>
              </select>
            </div>
            <div className="form-group">
              <label>Work Preference</label>
              <select value={remotePreference} onChange={(e) => setRemotePreference(e.target.value)}>
                <option value="onsite">On-site</option>
                <option value="hybrid">Hybrid</option>
                <option value="remote">Remote</option>
              </select>
            </div>
            <div className="form-group">
              <label>
                Maximum Results
                <span className="label-hint">Number of job listings to find (5-50)</span>
              </label>
              <select value={maxResults} onChange={(e) => setMaxResults(parseInt(e.target.value))}>
                <option value={5}>5 jobs</option>
                <option value={10}>10 jobs</option>
                <option value={15}>15 jobs</option>
                <option value={20}>20 jobs</option>
                <option value={30}>30 jobs</option>
                <option value={50}>50 jobs</option>
              </select>
            </div>
            {/* Search Scope */}
            <div className="form-group">
              <label>Search Scope</label>
              <select value={searchScope} onChange={(e) => setSearchScope(e.target.value)}>
                <option value="job_boards">Job Boards Only</option>
                <option value="company_pages">Company Pages Only</option>
                <option value="comprehensive">Comprehensive Search (Job Boards + Company Pages)</option>
              </select>
            </div>
          </div>
        </form>
      </div>
      {/* LLM Extracted Info Section */}
      {!analyzing && llmExtracted && (
        <div className="search-section llm-extracted-info">
          <h3>
            <span className="section-icon">📋</span>
            Resume Analysis Summary
          </h3>
          <div className="llm-summary-grid">
            {/* Identified Skills */}
            {llmExtracted.identified_domains && (
              <div className="llm-summary-block">
                <div className="llm-summary-label">Identified Skills</div>
                <div className="llm-summary-value skills-container">
                  {[...new Set(
                    llmExtracted.identified_domains.flatMap(d => d.matching_skills)
                  )].map((skill, i) => (
                    <span key={i} className="skill-tag">{skill}</span>
                  ))}
                </div>
              </div>
            )}
            {/* Strongest Domain */}
            {llmExtracted.skill_domain_summary && llmExtracted.skill_domain_summary.strongest_domain && (
              <div className="llm-summary-block">
                <div className="llm-summary-label">Strongest Domain</div>
                <div className="llm-summary-value">{llmExtracted.skill_domain_summary.strongest_domain}</div>
              </div>
            )}
            {/* Cross Domain Potential */}
            {llmExtracted.skill_domain_summary && llmExtracted.skill_domain_summary.cross_domain_potential && (
              <div className="llm-summary-block">
                <div className="llm-summary-label">Cross-Domain Potential</div>
                <div className="llm-summary-value">{llmExtracted.skill_domain_summary.cross_domain_potential}</div>
              </div>
            )}
            {/* Other extracted info can be added here as needed */}
          </div>
        </div>
      )}
      {/* Key Skills Section */}
      {!analyzing && extractedSkills.length > 0 && (
        <div className="search-section key-skills">
          <h3>
            <span className="section-icon">🛠️</span>
            Key Skills Found in Your Resume
          </h3>
          <div className="skills-list">
            {extractedSkills.map((skill, index) => (
              <span key={index} className="skill-tag">
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}
      {/* Domain Selection */}
      {!analyzing && domainAnalysis && (
        <div className="search-section domain-selection">
          <h3>
            <span className="section-icon">🎯</span>
            Select Your Domain & Role(s)
          </h3>
          <div className="domains-grid">
            {domainAnalysis.map((domain, index) => (
              <div 
                key={index}
                className={`domain-card ${selectedDomain?.name === domain.name ? 'selected' : ''}`}
                onClick={() => handleDomainSelect(domain)}
              >
                <h4>{domain.name}</h4>
                <div className="domain-skills">
                  {domain.skills.map((skill, i) => (
                    <span key={i} className="skill-tag">{skill}</span>
                  ))}
                </div>
                <div className="domain-roles">
                  {domain.roles.length > 0 ? (
                    domain.roles.map((role, i) => (
                      <button
                        key={i}
                        type="button"
                        className={`role-btn${selectedRoles.includes(role) ? ' selected' : ''}`}
                        onClick={e => {
                          e.stopPropagation();
                          handleRoleToggle(role);
                        }}
                      >
                        {selectedRoles.includes(role) ? '✓ ' : ''}{role}
                      </button>
                    ))
                  ) : (
                    <span className="no-domain-roles">No direct roles for this domain.</span>
                  )}
                </div>
              </div>
            ))}
          </div>
          {/* If no domain roles, show recommended roles */}
          {recommendedRoles.length > 0 && (
            <div className="recommended-roles">
              <h4>Recommended Roles</h4>
              <div className="recommended-roles-list">
                {recommendedRoles.map((role, i) => (
                  <button
                    key={i}
                    type="button"
                    className={`role-btn${selectedRoles.includes(role) ? ' selected' : ''}`}
                    onClick={() => handleRoleToggle(role)}
                  >
                    {selectedRoles.includes(role) ? '✓ ' : ''}{role}
                  </button>
                ))}
              </div>
            </div>
          )}
          {/* Custom Role Input */}
          <div className="custom-role">
            {!showCustomRole ? (
              <button 
                className="btn btn-secondary"
                onClick={() => setShowCustomRole(true)}
              >
                + Add a Custom Role
              </button>
            ) : (
              <div className="custom-role-input">
                <input
                  type="text"
                  value={customRole}
                  onChange={(e) => setCustomRole(e.target.value)}
                  placeholder="Enter your desired role"
                  className={errors.roles ? 'error' : ''}
                />
                <button 
                  className="btn btn-primary"
                  onClick={handleCustomRoleSubmit}
                  disabled={!customRole.trim()}
                >
                  Add Role
                </button>
                <button 
                  className="btn btn-text"
                  onClick={() => setShowCustomRole(false)}
                >
                  Cancel
                </button>
              </div>
            )}
          </div>
        </div>
      )}
      {/* Search Button */}
      {selectedRoles.length > 0 && (
        <div className="search-section search-actions">
          <div className="search-preview">
            <p>
              Searching for <strong>{selectedRoles.join(', ')}</strong>
              {locations && <> in <strong>{locations}</strong></>}
              {' '}at <strong>{experienceLevel.replace('-', ' ')}</strong> level
              {' '}for <strong>{jobType.replace('-', ' ')}</strong> positions
              {' '}with <strong>{remotePreference}</strong> work arrangement.
              {' '}Finding up to <strong>{maxResults}</strong> relevant jobs
              {' '}using <strong>
                {searchScope === 'job_boards' && 'Job Boards Only'}
                {searchScope === 'company_pages' && 'Company Career Pages Only'}
                {searchScope === 'comprehensive' && 'Job Boards + Company Pages'}
              </strong> search.
            </p>
          </div>
          <button 
            onClick={handleSearch}
            className="btn btn-primary search-button"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Searching Jobs...
              </>
            ) : (
              <>
                <span>🔍</span>
                Find Jobs
              </>
            )}
          </button>
          {errors.search && (
            <div className="error-message">
              <span className="error-icon">⚠️</span>
              {errors.search}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default JobSearch; 