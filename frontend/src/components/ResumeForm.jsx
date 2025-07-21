import React, { useState } from 'react';

const ResumeForm = ({ onSubmit, onBack }) => {
  const [formData, setFormData] = useState({
    personal_info: {
      name: '',
      email: '',
      phone: '',
      location: '',
      linkedin: '',
      github: '',
      portfolio: '',
      summary: ''
    },
    education: [{
      degree: '',
      institution: '',
      location: '',
      graduation_date: '',
      gpa: '',
      relevant_courses: []
    }],
    experience: [{
      title: '',
      company: '',
      location: '',
      start_date: '',
      end_date: '',
      description: [''],
      technologies: []
    }],
    projects: [{
      name: '',
      description: '',
      technologies: [],
      url: '',
      github: ''
    }],
    skills: {
      technical_skills: [],
      programming_languages: [],
      frameworks: [],
      tools: [],
      soft_skills: []
    },
    certifications: [],
    languages: []
  });

  const [errors, setErrors] = useState({});

  const handleInputChange = (section, field, value, index = null) => {
    setFormData(prev => {
      const newData = { ...prev };
      
      if (index !== null) {
        // Handle array fields (education, experience, projects)
        newData[section] = [...newData[section]];
        newData[section][index] = { ...newData[section][index], [field]: value };
      } else if (section === 'skills') {
        // Handle skills object
        newData.skills = { ...newData.skills, [field]: value };
      } else if (section === 'personal_info') {
        // Handle personal info
        newData.personal_info = { ...newData.personal_info, [field]: value };
      } else {
        // Handle simple arrays (certifications, languages)
        newData[section] = value;
      }
      
      return newData;
    });
  };

  const handleArrayItemChange = (section, index, field, value) => {
    setFormData(prev => {
      const newData = { ...prev };
      newData[section] = [...newData[section]];
      newData[section][index] = { ...newData[section][index], [field]: value };
      return newData;
    });
  };

  const addArrayItem = (section) => {
    setFormData(prev => {
      const newData = { ...prev };
      const templates = {
        education: {
          degree: '',
          institution: '',
          location: '',
          graduation_date: '',
          gpa: '',
          relevant_courses: []
        },
        experience: {
          title: '',
          company: '',
          location: '',
          start_date: '',
          end_date: '',
          description: [''],
          technologies: []
        },
        projects: {
          name: '',
          description: '',
          technologies: [],
          url: '',
          github: ''
        }
      };
      
      newData[section] = [...newData[section], templates[section]];
      return newData;
    });
  };

  const removeArrayItem = (section, index) => {
    setFormData(prev => {
      const newData = { ...prev };
      newData[section] = newData[section].filter((_, i) => i !== index);
      return newData;
    });
  };

  const handleSkillsChange = (skillType, value) => {
    // Convert comma-separated string to array
    const skillsArray = value.split(',').map(skill => skill.trim()).filter(skill => skill);
    handleInputChange('skills', skillType, skillsArray);
  };

  const validateForm = () => {
    const newErrors = {};

    // Validate personal info
    if (!formData.personal_info.name.trim()) {
      newErrors.name = 'Name is required';
    }
    if (!formData.personal_info.email.trim()) {
      newErrors.email = 'Email is required';
    }

    // Validate at least one education entry
    if (formData.education.length === 0 || !formData.education[0].degree.trim()) {
      newErrors.education = 'At least one education entry is required';
    }

    // Validate at least one experience entry
    if (formData.experience.length === 0 || !formData.experience[0].title.trim()) {
      newErrors.experience = 'At least one work experience entry is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  return (
    <div className="resume-form">
      <form onSubmit={handleSubmit}>
        {/* Personal Information */}
        <div className="form-section">
          <h3>Personal Information</h3>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="name">Full Name *</label>
              <input
                type="text"
                id="name"
                value={formData.personal_info.name}
                onChange={(e) => handleInputChange('personal_info', 'name', e.target.value)}
                className={errors.name ? 'error' : ''}
              />
              {errors.name && <span className="error-message">{errors.name}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="email">Email *</label>
              <input
                type="email"
                id="email"
                value={formData.personal_info.email}
                onChange={(e) => handleInputChange('personal_info', 'email', e.target.value)}
                className={errors.email ? 'error' : ''}
              />
              {errors.email && <span className="error-message">{errors.email}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="phone">Phone</label>
              <input
                type="tel"
                id="phone"
                value={formData.personal_info.phone}
                onChange={(e) => handleInputChange('personal_info', 'phone', e.target.value)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="location">Location</label>
              <input
                type="text"
                id="location"
                value={formData.personal_info.location}
                onChange={(e) => handleInputChange('personal_info', 'location', e.target.value)}
                placeholder="City, State/Country"
              />
            </div>

            <div className="form-group">
              <label htmlFor="linkedin">LinkedIn</label>
              <input
                type="url"
                id="linkedin"
                value={formData.personal_info.linkedin}
                onChange={(e) => handleInputChange('personal_info', 'linkedin', e.target.value)}
                placeholder="https://linkedin.com/in/username"
              />
            </div>

            <div className="form-group">
              <label htmlFor="github">GitHub</label>
              <input
                type="url"
                id="github"
                value={formData.personal_info.github}
                onChange={(e) => handleInputChange('personal_info', 'github', e.target.value)}
                placeholder="https://github.com/username"
              />
            </div>

            <div className="form-group full-width">
              <label htmlFor="portfolio">Portfolio Website</label>
              <input
                type="url"
                id="portfolio"
                value={formData.personal_info.portfolio}
                onChange={(e) => handleInputChange('personal_info', 'portfolio', e.target.value)}
                placeholder="https://your-portfolio.com"
              />
            </div>

            <div className="form-group full-width">
              <label htmlFor="summary">Professional Summary</label>
              <textarea
                id="summary"
                value={formData.personal_info.summary}
                onChange={(e) => handleInputChange('personal_info', 'summary', e.target.value)}
                placeholder="Brief professional summary or objective"
                rows="3"
              />
            </div>
          </div>
        </div>

        {/* Education */}
        <div className="form-section">
          <div className="section-header">
            <h3>Education</h3>
            <button
              type="button"
              className="btn-add"
              onClick={() => addArrayItem('education')}
            >
              + Add Education
            </button>
          </div>
          
          {formData.education.map((edu, index) => (
            <div key={index} className="array-item">
              <div className="item-header">
                <h4>Education #{index + 1}</h4>
                {formData.education.length > 1 && (
                  <button
                    type="button"
                    className="btn-remove"
                    onClick={() => removeArrayItem('education', index)}
                  >
                    Remove
                  </button>
                )}
              </div>
              
              <div className="form-grid">
                <div className="form-group">
                  <label>Degree *</label>
                  <input
                    type="text"
                    value={edu.degree}
                    onChange={(e) => handleArrayItemChange('education', index, 'degree', e.target.value)}
                    placeholder="e.g., Bachelor of Science in Computer Science"
                  />
                </div>

                <div className="form-group">
                  <label>Institution *</label>
                  <input
                    type="text"
                    value={edu.institution}
                    onChange={(e) => handleArrayItemChange('education', index, 'institution', e.target.value)}
                    placeholder="University name"
                  />
                </div>

                <div className="form-group">
                  <label>Location</label>
                  <input
                    type="text"
                    value={edu.location}
                    onChange={(e) => handleArrayItemChange('education', index, 'location', e.target.value)}
                    placeholder="City, State"
                  />
                </div>

                <div className="form-group">
                  <label>Graduation Date</label>
                  <input
                    type="text"
                    value={edu.graduation_date}
                    onChange={(e) => handleArrayItemChange('education', index, 'graduation_date', e.target.value)}
                    placeholder="e.g., May 2023"
                  />
                </div>

                <div className="form-group">
                  <label>GPA</label>
                  <input
                    type="text"
                    value={edu.gpa}
                    onChange={(e) => handleArrayItemChange('education', index, 'gpa', e.target.value)}
                    placeholder="e.g., 3.8/4.0"
                  />
                </div>
              </div>
            </div>
          ))}
          {errors.education && <span className="error-message">{errors.education}</span>}
        </div>

        {/* Experience */}
        <div className="form-section">
          <div className="section-header">
            <h3>Work Experience</h3>
            <button
              type="button"
              className="btn-add"
              onClick={() => addArrayItem('experience')}
            >
              + Add Experience
            </button>
          </div>
          
          {formData.experience.map((exp, index) => (
            <div key={index} className="array-item">
              <div className="item-header">
                <h4>Experience #{index + 1}</h4>
                {formData.experience.length > 1 && (
                  <button
                    type="button"
                    className="btn-remove"
                    onClick={() => removeArrayItem('experience', index)}
                  >
                    Remove
                  </button>
                )}
              </div>
              
              <div className="form-grid">
                <div className="form-group">
                  <label>Job Title *</label>
                  <input
                    type="text"
                    value={exp.title}
                    onChange={(e) => handleArrayItemChange('experience', index, 'title', e.target.value)}
                    placeholder="e.g., Software Engineer"
                  />
                </div>

                <div className="form-group">
                  <label>Company *</label>
                  <input
                    type="text"
                    value={exp.company}
                    onChange={(e) => handleArrayItemChange('experience', index, 'company', e.target.value)}
                    placeholder="Company name"
                  />
                </div>

                <div className="form-group">
                  <label>Location</label>
                  <input
                    type="text"
                    value={exp.location}
                    onChange={(e) => handleArrayItemChange('experience', index, 'location', e.target.value)}
                    placeholder="City, State or Remote"
                  />
                </div>

                <div className="form-group">
                  <label>Start Date *</label>
                  <input
                    type="text"
                    value={exp.start_date}
                    onChange={(e) => handleArrayItemChange('experience', index, 'start_date', e.target.value)}
                    placeholder="e.g., June 2022"
                  />
                </div>

                <div className="form-group">
                  <label>End Date</label>
                  <input
                    type="text"
                    value={exp.end_date}
                    onChange={(e) => handleArrayItemChange('experience', index, 'end_date', e.target.value)}
                    placeholder="e.g., Present or December 2023"
                  />
                </div>

                <div className="form-group full-width">
                  <label>Technologies Used</label>
                  <input
                    type="text"
                    value={exp.technologies.join(', ')}
                    onChange={(e) => handleArrayItemChange('experience', index, 'technologies', e.target.value.split(',').map(t => t.trim()).filter(t => t))}
                    placeholder="e.g., Python, React, AWS (comma-separated)"
                  />
                </div>

                <div className="form-group full-width">
                  <label>Description</label>
                  <textarea
                    value={exp.description.join('\n')}
                    onChange={(e) => handleArrayItemChange('experience', index, 'description', e.target.value.split('\n').filter(line => line.trim()))}
                    placeholder="Describe your responsibilities and achievements (one per line)"
                    rows="4"
                  />
                </div>
              </div>
            </div>
          ))}
          {errors.experience && <span className="error-message">{errors.experience}</span>}
        </div>

        {/* Projects */}
        <div className="form-section">
          <div className="section-header">
            <h3>Projects</h3>
            <button
              type="button"
              className="btn-add"
              onClick={() => addArrayItem('projects')}
            >
              + Add Project
            </button>
          </div>
          
          {formData.projects.map((project, index) => (
            <div key={index} className="array-item">
              <div className="item-header">
                <h4>Project #{index + 1}</h4>
                {formData.projects.length > 1 && (
                  <button
                    type="button"
                    className="btn-remove"
                    onClick={() => removeArrayItem('projects', index)}
                  >
                    Remove
                  </button>
                )}
              </div>
              
              <div className="form-grid">
                <div className="form-group">
                  <label>Project Name</label>
                  <input
                    type="text"
                    value={project.name}
                    onChange={(e) => handleArrayItemChange('projects', index, 'name', e.target.value)}
                    placeholder="Project name"
                  />
                </div>

                <div className="form-group">
                  <label>Technologies</label>
                  <input
                    type="text"
                    value={project.technologies.join(', ')}
                    onChange={(e) => handleArrayItemChange('projects', index, 'technologies', e.target.value.split(',').map(t => t.trim()).filter(t => t))}
                    placeholder="e.g., React, Node.js, MongoDB"
                  />
                </div>

                <div className="form-group">
                  <label>Project URL</label>
                  <input
                    type="url"
                    value={project.url}
                    onChange={(e) => handleArrayItemChange('projects', index, 'url', e.target.value)}
                    placeholder="https://project-demo.com"
                  />
                </div>

                <div className="form-group">
                  <label>GitHub Repository</label>
                  <input
                    type="url"
                    value={project.github}
                    onChange={(e) => handleArrayItemChange('projects', index, 'github', e.target.value)}
                    placeholder="https://github.com/username/project"
                  />
                </div>

                <div className="form-group full-width">
                  <label>Description</label>
                  <textarea
                    value={project.description}
                    onChange={(e) => handleArrayItemChange('projects', index, 'description', e.target.value)}
                    placeholder="Describe the project, your role, and key features"
                    rows="3"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Skills */}
        <div className="form-section">
          <h3>Skills</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Programming Languages</label>
              <input
                type="text"
                value={formData.skills.programming_languages.join(', ')}
                onChange={(e) => handleSkillsChange('programming_languages', e.target.value)}
                placeholder="e.g., Python, JavaScript, Java"
              />
            </div>

            <div className="form-group">
              <label>Frameworks & Libraries</label>
              <input
                type="text"
                value={formData.skills.frameworks.join(', ')}
                onChange={(e) => handleSkillsChange('frameworks', e.target.value)}
                placeholder="e.g., React, Django, TensorFlow"
              />
            </div>

            <div className="form-group">
              <label>Tools & Platforms</label>
              <input
                type="text"
                value={formData.skills.tools.join(', ')}
                onChange={(e) => handleSkillsChange('tools', e.target.value)}
                placeholder="e.g., Git, Docker, AWS"
              />
            </div>

            <div className="form-group">
              <label>Soft Skills</label>
              <input
                type="text"
                value={formData.skills.soft_skills.join(', ')}
                onChange={(e) => handleSkillsChange('soft_skills', e.target.value)}
                placeholder="e.g., Leadership, Communication, Problem Solving"
              />
            </div>
          </div>
        </div>

        {/* Additional Information */}
        <div className="form-section">
          <h3>Additional Information</h3>
          <div className="form-grid">
            <div className="form-group">
              <label>Certifications</label>
              <input
                type="text"
                value={formData.certifications.join(', ')}
                onChange={(e) => handleInputChange('certifications', null, e.target.value.split(',').map(c => c.trim()).filter(c => c))}
                placeholder="e.g., AWS Certified Developer, Google Cloud Professional"
              />
            </div>

            <div className="form-group">
              <label>Languages</label>
              <input
                type="text"
                value={formData.languages.join(', ')}
                onChange={(e) => handleInputChange('languages', null, e.target.value.split(',').map(l => l.trim()).filter(l => l))}
                placeholder="e.g., English (Native), Spanish (Fluent)"
              />
            </div>
          </div>
        </div>

        {/* Form Actions */}
        <div className="form-actions">
          <button type="button" className="btn-secondary" onClick={onBack}>
            Back
          </button>
          <button type="submit" className="btn-primary">
            Continue to Preview
          </button>
        </div>
      </form>
    </div>
  );
};

export default ResumeForm; 