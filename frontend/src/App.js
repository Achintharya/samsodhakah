import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import ResearchWorkspace from './features/research-workspace/ResearchWorkspace';
import DocumentLibrary from './features/document-library/Library';
import EvidenceExplorer from './features/evidence-explorer/Explorer';
import VerificationDashboard from './features/verification-dashboard/Dashboard';
import DraftingWorkspace from './features/drafting-workspace/Drafting';
import CitationManager from './features/citation-manager/CitationManager';
import ExportCenter from './features/export-center/ExportCenter';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<ResearchWorkspace />} />
          <Route path="library" element={<DocumentLibrary />} />
          <Route path="evidence" element={<EvidenceExplorer />} />
          <Route path="verify" element={<VerificationDashboard />} />
          <Route path="verification" element={<VerificationDashboard />} />
          <Route path="draft" element={<DraftingWorkspace />} />
          <Route path="citations" element={<CitationManager />} />
          <Route path="export" element={<ExportCenter />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;