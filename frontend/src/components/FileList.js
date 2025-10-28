import React from 'react';
import { downloadFile, deleteFile } from '../api';
import './FileList.css';

function FileList({ files, provider, onFileDeleted }) {
  const handleDownload = async (filename) => {
    try {
      const blob = await downloadFile(filename, provider);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      alert('Ошибка при скачивании файла');
    }
  };

  const handleDelete = async (filename) => {
    if (!window.confirm(`Удалить файл ${filename}?`)) return;

    try {
      await deleteFile(filename, provider);
      onFileDeleted();
    } catch (err) {
      alert('Ошибка при удалении файла');
    }
  };

  if (files.length === 0) {
    return (
      <div className="file-list-card">
        <h3>Ваши файлы</h3>
        <p className="no-files">Файлы отсутствуют. Загрузите первый файл!</p>
      </div>
    );
  }

  return (
    <div className="file-list-card">
      <h3>Ваши файлы ({files.length})</h3>
      <div className="file-list">
        {files.map((filename, index) => (
          <div key={index} className="file-item">
            <div className="file-info">
              <span className="file-icon">файл</span>
              <span className="file-name">{filename}</span>
            </div>
            <div className="file-actions">
              <button 
                className="btn-download" 
                onClick={() => handleDownload(filename)}
              >
                 Скачать
              </button>
              <button 
                className="btn-delete" 
                onClick={() => handleDelete(filename)}
              >
                ️ Удалить
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default FileList;

