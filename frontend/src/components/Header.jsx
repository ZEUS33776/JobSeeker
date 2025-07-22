import React from 'react';

const Header = () => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="brand">
          <h1 className="brand-title">
            Job Seeker Pro
          </h1>
          <p className="brand-subtitle">Professional Resume Analysis & Career Tools</p>
        </div>
        
        {/* Remove Help and Settings buttons */}
      </div>
    </header>
  );
};

export default Header; 