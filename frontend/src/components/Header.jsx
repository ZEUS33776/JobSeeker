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
        
        <div className="header-actions">
          <button className="help-btn">
            Help
          </button>
          <button className="settings-btn">
            Settings
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header; 