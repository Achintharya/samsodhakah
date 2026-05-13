import React, { useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

function readStoredJson(key) {
  try {
    const value = localStorage.getItem(key);
    return value ? JSON.parse(value) : null;
  } catch (error) {
    console.warn(`Unable to parse ${key}`, error);
    return null;
  }
}

function MetricCard({ label, value }) {
  return (
    <div style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12, background: '#fafafa' }}>
      <strong>{value ?? 0}</strong>
      <div style={{ color: '#555', fontSize: 13 }}>{label}</div>
    </div>
  );
}

function DraftingWorkspace() {
  const location = useLocation();
  const navigate = useNavigate();
  const section = useMemo(
    () => location.state?.section || readStoredJson('currentSection'),
    [location.state]
  );

  if (!section) {
    return (
      <div className="drafting-workspace">
        <h1>Drafting Workspace</h1>
        <p>No generated section is available yet.</p>
        <button onClick={() => navigate('/research')}>Generate a Section</button>
      </div>
    );
  }

  const contextStats = section.context_stats || {};
  const provenance = section.provenance || {};
  const citations = section.citations || [];
  const evidenceUnits = section.evidence_units || [];
  const verificationResults = section.verification_results || [];
  const confidenceScores = section.confidence_scores || {};

  return (
    <div className="drafting-workspace" style={{ padding: 24 }}>
      <h1>Drafting Workspace</h1>
      <p>Review the generated section, grounding metadata, citations, provenance, and token usage.</p>

      <section style={{ marginBottom: 24 }}>
        <h2>{section.section_type?.replaceAll('_', ' ') || 'Generated Section'}</h2>
        <p><strong>Topic:</strong> {section.topic}</p>
        <p><strong>Model:</strong> {section.generation_model || 'unknown'} · <strong>Generated:</strong> {section.generated_at || 'unknown'}</p>
        {section.warnings?.length > 0 && (
          <div style={{ background: '#fff7e6', border: '1px solid #ffd591', padding: 12, borderRadius: 8 }}>
            <strong>Warnings</strong>
            <ul>{section.warnings.map((warning, index) => <li key={index}>{warning}</li>)}</ul>
          </div>
        )}
      </section>

      <section style={{ marginBottom: 24 }}>
        <h2>Draft Content</h2>
        <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6, border: '1px solid #eee', borderRadius: 8, padding: 16 }}>
          {section.content || 'No content returned.'}
        </div>
      </section>

      <section style={{ marginBottom: 24 }}>
        <h2>Grounding Summary</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 12 }}>
          <MetricCard label="Evidence units" value={evidenceUnits.length || contextStats.evidence_count} />
          <MetricCard label="Semantic units" value={section.semantic_units?.length || contextStats.semantic_unit_count} />
          <MetricCard label="Retrieval results" value={section.retrieval_results?.length || contextStats.retrieval_result_count} />
          <MetricCard label="Context tokens" value={contextStats.token_count || section.token_count} />
          <MetricCard label="Citations" value={citations.length} />
          <MetricCard label="Verified claims" value={verificationResults.length} />
        </div>
        {confidenceScores.overall !== undefined && (
          <p><strong>Overall confidence:</strong> {Math.round(confidenceScores.overall * 100)}%</p>
        )}
      </section>

      <section style={{ marginBottom: 24 }}>
        <h2>Citations</h2>
        {citations.length === 0 ? <p>No citations returned.</p> : (
          <ol>
            {citations.map((citation, index) => (
              <li key={citation.id || citation.key || index}>
                <strong>{citation.key || citation.id}</strong> — {citation.title || citation.source_document || 'Unknown title'}
                {citation.year && <> ({citation.year})</>}
                {citation.confidence !== undefined && <> · confidence {Math.round(citation.confidence * 100)}%</>}
              </li>
            ))}
          </ol>
        )}
      </section>

      <section style={{ marginBottom: 24 }}>
        <h2>Provenance</h2>
        <p><strong>Retrieval mode:</strong> {provenance.retrieval_mode || 'unknown'}</p>
        <p><strong>Source documents:</strong> {provenance.source_documents?.length || 0}</p>
        <p><strong>Evidence chain:</strong> {provenance.evidence_chain?.length || 0} linked evidence items</p>
        {provenance.evidence_chain?.length > 0 && (
          <ul>
            {provenance.evidence_chain.slice(0, 8).map((item, index) => (
              <li key={item.evidence_id || index}>
                {item.evidence_id || 'evidence'} → {item.semantic_unit_id || 'semantic unit unknown'}
                {item.retrieval_score !== undefined && <> · score {Number(item.retrieval_score).toFixed(3)}</>}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h2>Evidence Used</h2>
        {evidenceUnits.length === 0 ? <p>No evidence units returned.</p> : (
          <ul>
            {evidenceUnits.slice(0, 10).map((evidence, index) => (
              <li key={evidence.id || index} style={{ marginBottom: 8 }}>
                <strong>{evidence.role || evidence.type || 'evidence'}:</strong> {evidence.content || evidence.text || evidence.summary || 'No preview available.'}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

export default DraftingWorkspace;