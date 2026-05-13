import React, { useMemo, useState } from 'react';

function readStoredJson(key) {
  try {
    const value = localStorage.getItem(key);
    return value ? JSON.parse(value) : null;
  } catch (error) {
    console.warn(`Unable to parse ${key}`, error);
    return null;
  }
}

function getDownloadFilename(disposition, format) {
  const extensions = { markdown: 'md', latex: 'tex', bibtex: 'bib', docx: 'docx' };
  const match = disposition?.match(/filename="?([^";]+)"?/i);
  return match?.[1] || `research-section.${extensions[format] || format}`;
}

function ExportCenter() {
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const section = useMemo(() => readStoredJson('currentSection'), []);

  const exportSection = async (format) => {
    if (!section) {
      setError('No generated section is available to export.');
      return;
    }

    setStatus(`Exporting ${format}...`);
    setError(null);

    try {
      const response = await fetch('/api/export/paper', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          paper_data: {
            title: `Research Section: ${section.topic || 'Generated Section'}`,
            authors: ['Researcher'],
            abstract: 'Generated research section with evidence grounding.',
            sections: [{
              title: section.section_type?.replaceAll('_', ' ') || 'Generated Section',
              content: section.content || '',
            }],
            citations: section.citations || [],
          },
          format,
        }),
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || 'Export failed');
      }

      const content = await response.text();
      const blob = new Blob([content], { type: response.headers.get('content-type') || 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = getDownloadFilename(response.headers.get('content-disposition'), format);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setStatus(`Exported ${format} successfully.`);
    } catch (err) {
      setError(err.message);
      setStatus(null);
    }
  };

  return (
    <div className="export-center" style={{ padding: 24 }}>
      <h1>Export Center</h1>
      <p>Export your evidence-grounded section with normalized file extensions and consistent citation keys.</p>

      {section ? (
        <section style={{ marginBottom: 24 }}>
          <h2>{section.topic || 'Generated Section'}</h2>
          <p><strong>Section:</strong> {section.section_type?.replaceAll('_', ' ') || 'unknown'}</p>
          <p><strong>Citations:</strong> {section.citations?.length || 0} · <strong>Evidence units:</strong> {section.evidence_units?.length || 0}</p>
          <p><strong>Context tokens:</strong> {section.context_stats?.token_count || section.token_count || 0}</p>
        </section>
      ) : (
        <p>No generated section is available yet. Generate a section from the Research Workspace first.</p>
      )}

      {error && <div style={{ color: '#a8071a', marginBottom: 12 }}>{error}</div>}
      {status && <div style={{ color: '#237804', marginBottom: 12 }}>{status}</div>}

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12 }}>
        <button onClick={() => exportSection('markdown')} disabled={!section}>Download Markdown (.md)</button>
        <button onClick={() => exportSection('latex')} disabled={!section}>Download LaTeX (.tex)</button>
        <button onClick={() => exportSection('bibtex')} disabled={!section}>Download BibTeX (.bib)</button>
        <button onClick={() => exportSection('docx')} disabled={!section}>Download DOCX (.docx)</button>
      </div>
    </div>
  );
}

export default ExportCenter;