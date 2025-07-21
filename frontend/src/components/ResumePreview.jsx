import React from 'react';

const ResumePreview = ({ 
  template, 
  inputMethod, 
  resumeData, 
  selectedResume, 
  generatedResume, 
  onGenerate, 
  onBack, 
  onReset, 
  loading 
}) => {
  const handleDownloadPDF = () => {
    if (generatedResume?.pdf_data) {
      // Create blob from base64 data
      const byteCharacters = atob(generatedResume.pdf_data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'application/pdf' });
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${template?.name || 'resume'}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    }
  };

  const handleDownloadLatex = () => {
    if (generatedResume?.latex_code) {
      const blob = new Blob([generatedResume.latex_code], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${template?.name || 'resume'}.tex`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    }
  };

  return (
    <div className="resume-preview">
      <div className="preview-header">
        <h3>Resume Preview</h3>
        <p>Review your information and generate your resume</p>
      </div>

      {/* Summary Information */}
      <div className="preview-summary">
        <div className="summary-card">
          <h4>Template Selected</h4>
          <p>{template?.name}</p>
          <span className="template-category">{template?.category}</span>
        </div>

        <div className="summary-card">
          <h4>Input Method</h4>
          <p>{inputMethod === 'form' ? 'Form Input' : 'Existing Resume'}</p>
          {inputMethod === 'existing' && (
            <span className="resume-session">Session: {selectedResume}</span>
          )}
        </div>

        {generatedResume && (
          <div className="summary-card">
            <h4>Generation Status</h4>
            <p className="status-success">✓ Successfully Generated</p>
            <p className="template-used">Using: {generatedResume.template_used}</p>
          </div>
        )}
      </div>

      {/* Information Preview */}
      {inputMethod === 'form' && resumeData && (
        <div className="information-preview">
          <h4>Information Summary</h4>
          
          <div className="info-section">
            <h5>Personal Information</h5>
            <p><strong>Name:</strong> {resumeData.personal_info.name}</p>
            <p><strong>Email:</strong> {resumeData.personal_info.email}</p>
            {resumeData.personal_info.phone && (
              <p><strong>Phone:</strong> {resumeData.personal_info.phone}</p>
            )}
            {resumeData.personal_info.location && (
              <p><strong>Location:</strong> {resumeData.personal_info.location}</p>
            )}
          </div>

          <div className="info-section">
            <h5>Education ({resumeData.education.length} entries)</h5>
            {resumeData.education.map((edu, index) => (
              <div key={index} className="info-item">
                <p><strong>{edu.degree}</strong> - {edu.institution}</p>
                {edu.graduation_date && <p>Graduated: {edu.graduation_date}</p>}
              </div>
            ))}
          </div>

          <div className="info-section">
            <h5>Experience ({resumeData.experience.length} entries)</h5>
            {resumeData.experience.map((exp, index) => (
              <div key={index} className="info-item">
                <p><strong>{exp.title}</strong> at {exp.company}</p>
                <p>{exp.start_date} - {exp.end_date || 'Present'}</p>
              </div>
            ))}
          </div>

          <div className="info-section">
            <h5>Projects ({resumeData.projects.length} entries)</h5>
            {resumeData.projects.map((project, index) => (
              <div key={index} className="info-item">
                <p><strong>{project.name}</strong></p>
                <p>{project.description}</p>
              </div>
            ))}
          </div>

          <div className="info-section">
            <h5>Skills</h5>
            <p><strong>Programming Languages:</strong> {resumeData.skills.programming_languages.join(', ') || 'None specified'}</p>
            <p><strong>Frameworks:</strong> {resumeData.skills.frameworks.join(', ') || 'None specified'}</p>
            <p><strong>Tools:</strong> {resumeData.skills.tools.join(', ') || 'None specified'}</p>
          </div>
        </div>
      )}

      {inputMethod === 'existing' && (
        <div className="information-preview">
          <h4>Using Existing Resume</h4>
          <p>Your resume will be generated using the information extracted from your uploaded resume.</p>
          <p><strong>Session ID:</strong> {selectedResume}</p>
        </div>
      )}

      {/* Generation Results */}
      {generatedResume && (
        <div className="generation-results">
          <h4>Generation Results</h4>
          
          <div className="results-info">
            <div className="result-item">
              <span className="result-label">Template Used:</span>
              <span className="result-value">{generatedResume.template_used}</span>
            </div>
            
            {generatedResume.data?.extracted_info && (
              <>
                <div className="result-item">
                  <span className="result-label">Personal Info Found:</span>
                  <span className="result-value">{generatedResume.data.extracted_info.personal || 'Yes'}</span>
                </div>
                
                <div className="result-item">
                  <span className="result-label">Experience Entries:</span>
                  <span className="result-value">{generatedResume.data.extracted_info.experience_count || '0'}</span>
                </div>
                
                <div className="result-item">
                  <span className="result-label">Education Entries:</span>
                  <span className="result-value">{generatedResume.data.extracted_info.education_count || '0'}</span>
                </div>
                
                <div className="result-item">
                  <span className="result-label">Projects Found:</span>
                  <span className="result-value">{generatedResume.data.extracted_info.projects_count || '0'}</span>
                </div>
              </>
            )}
            
            {generatedResume.data?.missing_info && generatedResume.data.missing_info.length > 0 && (
              <div className="result-item">
                <span className="result-label">Missing Information:</span>
                <span className="result-value warning">
                  {generatedResume.data.missing_info.join(', ')}
                </span>
              </div>
            )}
          </div>

          {/* Download Options */}
          <div className="download-options">
            <h5>Download Options</h5>
            <div className="download-buttons">
              <button
                className="btn-primary"
                onClick={handleDownloadPDF}
                disabled={!generatedResume.pdf_data}
              >
                📄 Download PDF
              </button>
              
              <button
                className="btn-secondary"
                onClick={handleDownloadLatex}
                disabled={!generatedResume.latex_code}
              >
                📝 Download LaTeX
              </button>
            </div>
          </div>

          {/* LaTeX Preview */}
          {generatedResume.latex_code && (
            <div className="latex-preview">
              <h5>Generated LaTeX Code</h5>
              <div className="code-container">
                <pre className="latex-code">
                  <code>{generatedResume.latex_code}</code>
                </pre>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div className="preview-actions">
        <button className="btn-secondary" onClick={onBack}>
          Back
        </button>
        
        {!generatedResume ? (
          <button 
            className="btn-primary" 
            onClick={onGenerate}
            disabled={loading}
          >
            {loading ? 'Generating...' : 'Generate Resume'}
          </button>
        ) : (
          <button className="btn-primary" onClick={onReset}>
            Create New Resume
          </button>
        )}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-content">
            <div className="spinner"></div>
            <p>Generating your resume...</p>
            <p className="loading-note">This may take a few moments</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResumePreview; 