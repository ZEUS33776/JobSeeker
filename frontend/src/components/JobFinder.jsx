import React, { useState } from 'react';
import { API_ENDPOINTS } from '../config/api';

const JobFinder = ({ uploadedResumes, loading, setLoading }) => {
  const [selectedResume, setSelectedResume] = useState('');
  const [locations, setLocations] = useState('');
  const [positions, setPositions] = useState('');
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResults(null);
    if (!selectedResume || !locations || !positions) {
      setError('Please select a resume, enter at least one location, and a position.');
      return;
    }
    setLoading(true);
    try {
      // Call the backend job search endpoint (assume /jobs/search)
      const response = await fetch(API_ENDPOINTS.searchJobs(), {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          session_id: selectedResume,
          additional_keywords: positions,
          max_results: 20,
          updated_skills: '' // Optionally add skills
        })
      });
      const data = await response.json();
      if (data.success) {
        setResults(data.data.jobs || []);
      } else {
        setError(data.message || 'Failed to find jobs.');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="job-finder-section">
      <h2>Let's find you a job!</h2>
      <form className="job-finder-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Select Resume</label>
          <select
            value={selectedResume}
            onChange={e => setSelectedResume(e.target.value)}
            required
          >
            <option value="">Choose a resume...</option>
            {uploadedResumes.map(resume => (
              <option key={resume.id} value={resume.id}>
                {resume.name || resume.filename}
              </option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>Location(s)</label>
          <input
            type="text"
            placeholder="Enter one or more locations (comma separated)"
            value={locations}
            onChange={e => setLocations(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>Position(s)</label>
          <input
            type="text"
            placeholder="Enter the position(s) you are looking for (comma separated)"
            value={positions}
            onChange={e => setPositions(e.target.value)}
            required
          />
        </div>
        <button className="btn-primary" type="submit" disabled={loading}>
          {loading ? 'Searching...' : 'Find Jobs'}
        </button>
        {error && <div className="error-message">{error}</div>}
      </form>
      {results && (
        <div className="job-results">
          <h3>Job Results</h3>
          {results.length === 0 ? (
            <p>No jobs found for your criteria.</p>
          ) : (
            <ul className="job-list">
              {results.map((job, idx) => (
                <li key={job.url || idx} className="job-item">
                  <a href={job.url} target="_blank" rel="noopener noreferrer">
                    <h4>{job.title}</h4>
                  </a>
                  <p><strong>Company:</strong> {job.company}</p>
                  <p><strong>Location:</strong> {job.location}</p>
                  <p><strong>Description:</strong> {job.snippet || job.description}</p>
                  <p><strong>Source:</strong> {job.source}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

export default JobFinder; 