import React, { useState } from 'react';
import { uploadFile } from '../api';
import './FileUpload.css';

function FileUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [provider, setProvider] = useState('s3');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError('');
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Выберите файл для загрузки');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await uploadFile(file, provider);
      setFile(null);
      e.target.reset();
      onUploadSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке файла');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="file-upload-card">
      <h3>Загрузить файл</h3>
      <form onSubmit={handleUpload}>
        {error && <div className="error-message">{error}</div>}
        
        <div className="form-group">
          <label>Облачное хранилище:</label>
          <select value={provider} onChange={(e) => setProvider(e.target.value)}>
            <option value="s3">Amazon S3</option>
            <option value="azure">Azure Blob</option>
            <option value="gcs">Google Cloud Storage</option>
          </select>
        </div>

        <div className="form-group">
          <label>Выберите файл:</label>
          <input 
            type="file" 
            onChange={handleFileChange}
            disabled={loading}
          />
        </div>

        <button type="submit" className="btn" disabled={loading || !file}>
          {loading ? 'Загрузка...' : 'Загрузить'}
        </button>
      </form>
    </div>
  );
}

export default FileUpload;

