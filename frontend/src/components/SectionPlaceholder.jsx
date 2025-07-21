import React from 'react';

const SectionPlaceholder = ({ title, description }) => {
  return (
    <div className="section-placeholder">
      <div className="placeholder-content">
        <div className="placeholder-header">
          <h2 className="placeholder-title">{title}</h2>
          <p className="placeholder-description">{description}</p>
        </div>
        
        <div className="placeholder-visual">
          <div className="placeholder-card">
            <div className="placeholder-line"></div>
            <div className="placeholder-line short"></div>
            <div className="placeholder-line medium"></div>
          </div>
          <div className="placeholder-card">
            <div className="placeholder-line"></div>
            <div className="placeholder-line medium"></div>
            <div className="placeholder-line"></div>
          </div>
          <div className="placeholder-card">
            <div className="placeholder-line short"></div>
            <div className="placeholder-line"></div>
            <div className="placeholder-line medium"></div>
          </div>
        </div>
        
        <div className="placeholder-actions">
          <button className="btn-placeholder" disabled>
            Feature in Development
          </button>
        </div>
      </div>
    </div>
  );
};

export default SectionPlaceholder; 