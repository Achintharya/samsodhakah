import React, { useState } from 'react';
import { uploadDocument } from '../../services/documentService';

function DocumentLibrary() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus('Please select a file first.');
      return;
    }

    try {
      const response = await uploadDocument(selectedFile);
      setUploadStatus(`Document uploaded successfully: ${response.message}`);
    } catch (error) {
      setUploadStatus(`Error uploading document: ${error.message}`);
    }
  };

  return (
    <div className="document-library">
      <h1>Document Library</h1>
      <p>Manage your uploaded documents.</p>

      <div className="upload-section">
        <h2>Upload Document</h2>
        <input type="file" onChange={handleFileChange} />
        <button onClick={handleUpload}>Upload</button>
        {uploadStatus && <p>{uploadStatus}</p>}
      </div>
    </div>
  );
}

export default DocumentLibrary;