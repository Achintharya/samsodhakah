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

function verdictColor(verdict) {
  if (verdict === 'supported') return '#237804';
  if (verdict === 'contradicted') return '#a8071a';
  if (verdict === 'insufficient_evidence') return '#ad6800';
  return '#555';
}

function VerificationDashboard() {
  const location = useLocation();
  const navigate = useNavigate();
  const verification = useMemo(
    () => location.state?.verification || readStoredJson('verificationResults'),
    [location.state]
  );

  if (!verification) {
    return (
      <div className="verification-dashboard">
        <h1>Verification Dashboard</h1>
        <p>No verification results are available yet.</p>
        <button onClick={() => navigate('/research')}>Verify a Generated Section</button>
      </div>
    );
  }

  const summary = verification.summary || {};
  const evidenceUsage = verification.evidence_usage || {};
  const results = verification.verification_results || [];

  return (
    <div className="verification-dashboard" style={{ padding: 24 }}>
      <h1>Verification Dashboard</h1>
      <p>Review claim verification results, evidence usage, warnings, and contradictions.</p>

      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12, marginBottom: 24 }}>
        <div><strong>{verification.claim_count || results.length}</strong><br />Claims checked</div>
        <div><strong>{summary.supported_claims || 0}</strong><br />Supported claims</div>
        <div><strong>{summary.issues_found || 0}</strong><br />Issues found</div>
        <div><strong>{verification.source_count || 0}</strong><br />Sources consulted</div>
        <div><strong>{evidenceUsage.unique_evidence_used || 0}</strong><br />Evidence items used</div>
        <div><strong>{evidenceUsage.low_confidence_claims || 0}</strong><br />Low-confidence claims</div>
      </section>

      {summary.overall_confidence !== undefined && (
        <p><strong>Overall confidence:</strong> {Math.round(summary.overall_confidence * 100)}%</p>
      )}

      {summary.recommendations?.length > 0 && (
        <section style={{ background: '#f6ffed', border: '1px solid #b7eb8f', padding: 12, borderRadius: 8, marginBottom: 24 }}>
          <h2>Recommendations</h2>
          <ul>{summary.recommendations.map((item, index) => <li key={index}>{item}</li>)}</ul>
        </section>
      )}

      <section>
        <h2>Claim Results</h2>
        {results.length === 0 ? <p>No claim results returned.</p> : results.map((result, index) => (
          <article key={`${result.claim}-${index}`} style={{ border: '1px solid #e8e8e8', borderRadius: 8, padding: 16, marginBottom: 16 }}>
            <h3 style={{ marginTop: 0 }}>{result.claim}</h3>
            <p>
              <strong style={{ color: verdictColor(result.verdict) }}>{result.verdict || 'unknown'}</strong>
              {' '}· confidence {Math.round((result.confidence || 0) * 100)}%
              {' '}· evidence {result.evidence_count || 0}
            </p>
            {result.warnings?.length > 0 && (
              <div style={{ background: '#fff7e6', padding: 10, borderRadius: 6 }}>
                <strong>Warnings:</strong>
                <ul>{result.warnings.map((warning, warningIndex) => <li key={warningIndex}>{warning}</li>)}</ul>
              </div>
            )}
            {result.supporting_evidence?.length > 0 && (
              <div>
                <strong>Supporting evidence</strong>
                <ul>
                  {result.supporting_evidence.slice(0, 5).map((evidence, evidenceIndex) => (
                    <li key={evidence.id || evidenceIndex}>
                      {evidence.preview || evidence.text || evidence.source_id || 'Evidence preview unavailable'}
                      {evidence.confidence !== undefined && <> · {Math.round(evidence.confidence * 100)}%</>}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {result.contradictions?.length > 0 && (
              <div style={{ background: '#fff1f0', padding: 10, borderRadius: 6 }}>
                <strong>Contradictions</strong>
                <ul>{result.contradictions.map((item, contradictionIndex) => <li key={contradictionIndex}>{item.detail || item.claim || JSON.stringify(item)}</li>)}</ul>
              </div>
            )}
          </article>
        ))}
      </section>
    </div>
  );
}

export default VerificationDashboard;