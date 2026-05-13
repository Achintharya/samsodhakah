import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

/**
 * Uploads a document to the backend.
 * @param {File} file - The file to upload.
 * @returns {Promise} - A promise that resolves with the response from the server.
 */
const uploadDocument = async (file) => {
  const formData = new FormData();
  formData.append('document', file);

  try {
    const response = await axios.post(`${API_BASE_URL}/documents/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading document:', error);
    throw error;
  }
};

export { uploadDocument };