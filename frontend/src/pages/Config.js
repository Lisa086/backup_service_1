import React, { useState, useEffect } from 'react';
import { getConfig, createConfig, updateConfig } from '../api';
import Alert from '../components/Alert';
import './Config.css';

function Config() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [alert, setAlert] = useState({ type: '', message: '' });

  const [formData, setFormData] = useState({
    default_provider: 's3',
    backup_schedule: '',
    notification_preferences: {
      email_enabled: false,
      telegram_enabled: false
    },
    storage_settings: {
      max_file_size: 100,
      retention_days: 30
    }
  });

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const data = await getConfig();
      setConfig(data);
      setFormData({
        default_provider: data.default_provider || 's3',
        backup_schedule: data.backup_schedule || '',
        notification_preferences: data.notification_preferences || {
          email_enabled: false,
          telegram_enabled: false
        },
        storage_settings: data.storage_settings || {
          max_file_size: 100,
          retention_days: 30
        }
      });
    } catch {
      console.log('Конфигурация еще не создана');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      if (config) {
        await updateConfig(formData);
        setAlert({ type: 'success', message: 'Настройки обновлены!' });
      } else {
        await createConfig(formData);
        setAlert({ type: 'success', message: 'Настройки созданы!' });
      }
      loadConfig();
    } catch {
      setAlert({ type: 'error', message: 'Ошибка сохранения настроек' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="container"><div className="loading">Загрузка...</div></div>;
  }

  return (
    <div className="container">
      <h1>Настройки</h1>

      <Alert 
        type={alert.type} 
        message={alert.message} 
        onClose={() => setAlert({ type: '', message: '' })} 
      />

      <form onSubmit={handleSubmit} className="config-form">
        <div className="config-section">
          <h3>Облачное хранилище по умолчанию</h3>
          <select
            value={formData.default_provider}
            onChange={e => setFormData({...formData, default_provider: e.target.value})}
          >
            <option value="s3">Amazon S3</option>
            <option value="azure">Azure Blob</option>
            <option value="gcs">Google Cloud Storage</option>
          </select>
        </div>

        <div className="config-section">
          <h3>Расписание резервного копирования</h3>
          <input
            type="text"
            placeholder="Например: daily, weekly"
            value={formData.backup_schedule}
            onChange={e => setFormData({...formData, backup_schedule: e.target.value})}
          />
        </div>

        <div className="config-section">
          <h3>Уведомления</h3>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={formData.notification_preferences.email_enabled}
              onChange={e => setFormData({
                ...formData,
                notification_preferences: { ...formData.notification_preferences, email_enabled: e.target.checked }
              })}
            />
            Email уведомления
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={formData.notification_preferences.telegram_enabled}
              onChange={e => setFormData({
                ...formData,
                notification_preferences: { ...formData.notification_preferences, telegram_enabled: e.target.checked }
              })}
            />
            Telegram уведомления
          </label>
        </div>

        <div className="config-section">
          <h3>Настройки хранилища</h3>
          <div className="form-group">
            <label>Максимальный размер файла (MB):</label>
            <input
              type="number"
              value={formData.storage_settings.max_file_size}
              onChange={e => setFormData({
                ...formData,
                storage_settings: { ...formData.storage_settings, max_file_size: parseInt(e.target.value) }
              })}
            />
          </div>
          <div className="form-group">
            <label>Срок хранения (дней):</label>
            <input
              type="number"
              value={formData.storage_settings.retention_days}
              onChange={e => setFormData({
                ...formData,
                storage_settings: { ...formData.storage_settings, retention_days: parseInt(e.target.value) }
              })}
            />
          </div>
        </div>

        <button type="submit" className="btn" disabled={saving}>
          {saving ? 'Сохранение...' : 'Сохранить настройки'}
        </button>
      </form>
    </div>
  );
}

export default Config;

