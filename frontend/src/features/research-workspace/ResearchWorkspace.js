import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './ResearchWorkspace.css';

function ResearchWorkspace() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('read');
  const [documentId, setDocumentId] = useState('');
  const [sectionType, setSectionType] = useState('related_work');
  const [topic, setTopic] = useState('');
  const [relatedWorkId, setRelatedWorkId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Available section types for drafting
  const sectionTypes = [
    { value: 'related_work', label: 'Related Work' },
    { value: 'methodology', label: 'Methodology' },
    { value: 'theory', label: 'Theory' },
    { value: 'results', label: 'Results' },
    { value: 'experimental_setup', label: 'Experimental Setup' },
    { value: 'discussion', label: 'Discussion' },
    { value: 'abstract', label: 'Abstract' },
    { value: 'conclusion', label: 'Conclusion' },
  ];

  const handleGenerateOutline = async () => {
    if (!documentId || !topic) {
      setError('Please provide both document ID and topic');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch('/api/drafting/outline', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_id: documentId,
          section_type: sectionType,
          topic: topic,
          related_work_id: relatedWorkId || undefined,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate outline');
      }

      const outline = await response.json();
      setSuccess(`Outline generated successfully! Found ${outline.evidence_count} evidence units.`);
      // Store outline in local state for display
      localStorage.setItem('currentOutline', JSON.stringify(outline));
      navigate('/draft', { state: { outline } });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateSection = async () => {
    if (!documentId || !topic) {
      setError('Please provide both document ID and topic');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch('/api/drafting/section', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_id: documentId,
          section_type: sectionType,
          topic: topic,
          related_work_id: relatedWorkId || undefined,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate section');
      }

      const section = await response.json();
      setSuccess(`Section generated successfully! Used ${section.evidence_units.length} evidence units.`);
      // Store section in local state for display
      localStorage.setItem('currentSection', JSON.stringify(section));
      navigate('/draft', { state: { section } });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifySection = async () => {
    const sectionContent = localStorage.getItem('currentSection');
    if (!sectionContent || !documentId) {
      setError('No section content available to verify');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch('/api/verification/section-claims', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_id: documentId,
          section_content: JSON.parse(sectionContent).content,
          section_type: sectionType,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to verify section');
      }

      const verification = await response.json();
      setSuccess(`Verification complete! ${verification.summary.supported_claims} claims supported, ${verification.summary.issues_found} issues found.`);
      // Store verification results
      localStorage.setItem('verificationResults', JSON.stringify(verification));
      navigate('/verification', { state: { verification } });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = async (format) => {
    const sectionContent = localStorage.getItem('currentSection');
    if (!sectionContent) {
      setError('No section content available to export');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch('/api/export/paper', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          paper_data: {
            title: `Research Section: ${topic}`,
            authors: ['Researcher'],
            abstract: 'Generated research section with evidence grounding.',
            sections: [{
              title: sectionTypes.find(t => t.value === sectionType)?.label || sectionType,
              content: JSON.parse(sectionContent).content,
            }],
            citations: JSON.parse(sectionContent).citations || [],
          },
          format: format,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to export document');
      }

      const content = await response.text();
      const blob = new Blob([content], { type: response.headers.get('content-type') });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `research-section.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      setSuccess(`Document exported successfully as ${format}!`);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="research-workspace">
      <div className="workspace-header">
        <h1>Research Workspace</h1>
        <p>Generate evidence-grounded research sections with proper citations and verification</p>
      </div>

      <div className="workspace-controls">
        <div className="control-group">
          <label htmlFor="documentId">Document ID:</label>
          <input
            id="documentId"
            type="text"
            value={documentId}
            onChange={(e) => setDocumentId(e.target.value)}
            placeholder="Enter document ID"
          />
        </div>

        <div className="control-group">
          <label htmlFor="sectionType">Section Type:</label>
          <select
            id="sectionType"
            value={sectionType}
            onChange={(e) => setSectionType(e.target.value)}
          >
            {sectionTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label htmlFor="topic">Topic/Query:</label>
          <input
            id="topic"
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="What to write about..."
          />
        </div>

        <div className="control-group">
          <label htmlFor="relatedWorkId">Related Work ID (optional):</label>
          <input
            id="relatedWorkId"
            type="text"
            value={relatedWorkId}
            onChange={(e) => setRelatedWorkId(e.target.value)}
            placeholder="Enter related work document ID"
          />
        </div>

        <div className="action-buttons">
          <button
            className="btn-outline"
            onClick={handleGenerateOutline}
            disabled={isLoading}
          >
            {isLoading ? 'Generating...' : 'Generate Outline'}
          </button>

          <button
            className="btn-primary"
            onClick={handleGenerateSection}
            disabled={isLoading}
          >
            {isLoading ? 'Generating...' : 'Generate Section'}
          </button>

          <button
            className="btn-secondary"
            onClick={handleVerifySection}
            disabled={isLoading || !localStorage.getItem('currentSection')}
          >
            {isLoading ? 'Verifying...' : 'Verify Section'}
          </button>
        </div>
      </div>

      {error && <div className="alert error">{error}</div>}
      {success && <div className="alert success">{success}</div>}

      <div className="workspace-features">
        <div className="feature-card">
          <h3>📚 Document Library</h3>
          <p>Upload and manage your research documents</p>
          <button onClick={() => navigate('/library')}>Go to Library</button>
        </div>

        <div className="feature-card">
          <h3>📝 Drafting Workspace</h3>
          <p>Refine and edit generated sections</p>
          <button onClick={() => navigate('/draft')}>Go to Drafting</button>
        </div>

        <div className="feature-card">
          <h3>🔍 Evidence Explorer</h3>
          <p>Browse extracted evidence and semantic units</p>
          <button onClick={() => navigate('/evidence')}>Go to Evidence</button>
        </div>

        <div className="feature-card">
          <h3>📊 Verification Dashboard</h3>
          <p>Check claim support and evidence quality</p>
          <button onClick={() => navigate('/verification')}>Go to Verification</button>
        </div>

        <div className="feature-card">
          <h3>💾 Export Center</h3>
          <p>Export to multiple scholarly formats</p>
          <div className="export-actions">
            <button onClick={() => handleExport('markdown')}>Export as Markdown</button>
            <button onClick={() => handleExport('latex')}>Export as LaTeX</button>
            <button onClick={() => handleExport('bibtex')}>Export Citations</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ResearchWorkspace;