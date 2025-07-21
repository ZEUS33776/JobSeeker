import React, { useState } from 'react';
import { API_ENDPOINTS } from '../config/api.js';

const TemplateSelector = ({ templates, onTemplateSelect, loading }) => {
  const [modalOpen, setModalOpen] = useState(false);
  const [modalImage, setModalImage] = useState(null);
  const [modalAlt, setModalAlt] = useState('');
  const [hovered, setHovered] = useState(null);

  const openModal = (src, alt) => {
    setModalImage(src);
    setModalAlt(alt);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setModalImage(null);
    setModalAlt('');
  };

  if (loading) {
    return (
      <div className="template-selector">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading templates...</p>
        </div>
      </div>
    );
  }

  if (templates.length === 0) {
    return (
      <div className="template-selector">
        <div className="empty-state">
          <h3>No Templates Available</h3>
          <p>Unable to load resume templates. Please try again later.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="template-selector">
      <div className="selector-header">
        <h3>Choose a Resume Template</h3>
        <p>Select a template that best matches your style and industry</p>
      </div>

      <div className="templates-grid">
        {templates.map((template) => (
          <div
            key={template.id}
            className="template-card"
            onMouseEnter={() => setHovered(template.id)}
            onMouseLeave={() => setHovered(null)}
            style={{ position: 'relative' }}
          >
            <div className="template-preview" style={{ position: 'relative' }}>
              <img
                src={API_ENDPOINTS.resumeBuilderTemplateImage(template.id)}
                alt={`${template.name} preview`}
                onError={(e) => {
                  e.target.src = '/placeholder-template.svg';
                }}
                style={{ width: '100%', height: '100%', objectFit: 'contain', background: '#fff' }}
              />
              {/* Zoom/View button on image */}
              <button
                className="template-zoom-btn"
                title="View Full Image"
                onClick={e => { e.stopPropagation(); openModal(API_ENDPOINTS.resumeBuilderTemplateImage(template.id), `${template.name} preview`); }}
                style={{ position: 'absolute', top: 10, right: 10, background: 'rgba(0,0,0,0.6)', border: 'none', borderRadius: '50%', color: '#fff', width: 36, height: 36, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', zIndex: 2 }}
              >
                <span style={{ fontSize: 20 }}>🔍</span>
              </button>
            </div>
            
            <div className="template-info">
              <h4 className="template-name">{template.name}</h4>
              <p className="template-description">{template.description}</p>
              
              <div className="template-tags">
                <span className="template-category">{template.category}</span>
                {template.tags.map((tag, index) => (
                  <span key={index} className="template-tag">
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            {/* Select Template button/overlay only at the bottom */}
            <div
              className="template-select-overlay"
              style={{
                opacity: hovered === template.id ? 1 : 0,
                pointerEvents: hovered === template.id ? 'auto' : 'none',
                cursor: hovered === template.id ? 'pointer' : 'default',
                position: 'absolute',
                left: 0,
                right: 0,
                bottom: 0,
                top: '60%', // Only bottom part
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'rgba(0,0,0,0.7)',
                transition: 'opacity 0.3s ease',
              }}
              onClick={() => hovered === template.id && onTemplateSelect(template)}
            >
              <span className="select-text">Select Template</span>
            </div>
          </div>
        ))}
      </div>

      {/* Modal for full image view */}
      {modalOpen && (
        <div className="template-modal-overlay" onClick={closeModal}>
          <div className="template-modal-content" onClick={e => e.stopPropagation()}>
            <button className="template-modal-close" onClick={closeModal}>&times;</button>
            <img src={modalImage} alt={modalAlt} className="template-modal-img" />
          </div>
        </div>
      )}

      <div className="template-tips">
        <h4>Template Selection Tips:</h4>
        <ul>
          <li><strong>Modern:</strong> Clean, contemporary designs suitable for tech and creative industries</li>
          <li><strong>Classic:</strong> Traditional layouts perfect for conservative industries like finance and law</li>
          <li><strong>Tech:</strong> Optimized for technical roles with emphasis on skills and projects</li>
        </ul>
      </div>
    </div>
  );
};

export default TemplateSelector; 