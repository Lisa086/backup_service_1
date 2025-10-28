import React, { useState, useEffect } from 'react';
import FileUpload from '../components/FileUpload';
import FileList from '../components/FileList';
import Alert from '../components/Alert';
import { listFiles } from '../api';
import './Dashboard.css';

function Dashboard() {
  const [files, setFiles] = useState([]);
  const [provider, setProvider] = useState('s3');
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState({ type: '', message: '' });

  const loadFiles = async () => {
    setLoading(true);
    try {
      const data = await listFiles(provider);
      setFiles(data.files || []);
    } catch {
      setAlert({ type: 'error', message: 'Ошибка загрузки списка файлов' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFiles();
  }, [provider]);

  const handleUploadSuccess = () => {
    setAlert({ type: 'success', message: 'Файл успешно загружен!' });
    loadFiles();
  };

  const handleFileDeleted = () => {
    setAlert({ type: 'success', message: 'Файл успешно удален!' });
    loadFiles();
  };

  return (
    <div className="container">
      <h1>Управление файлами</h1>
      
      <Alert 
        type={alert.type} 
        message={alert.message} 
        onClose={() => setAlert({ type: '', message: '' })} 
      />

      <div className="provider-selector">
        <label>Облачное хранилище:</label>
        <select value={provider} onChange={e => setProvider(e.target.value)}>
          <option value="s3">Amazon S3</option>
          <option value="azure">Azure Blob</option>
          <option value="gcs">Google Cloud Storage</option>
        </select>
      </div>

      <FileUpload onUploadSuccess={handleUploadSuccess} />

      {loading ? (
        <div className="loading">Загрузка...</div>
      ) : (
        <FileList 
          files={files} 
          provider={provider} 
          onFileDeleted={handleFileDeleted} 
        />
      )}
    </div>
  );
}

export default Dashboard;

