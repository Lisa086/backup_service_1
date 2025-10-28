import React, { useState, useEffect } from 'react';
import { getHealth, getLogs, getMetricsSnapshot } from '../api';
import './Monitor.css';

function Monitor() {
  const [health, setHealth] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMonitoringData();
    const interval = setInterval(loadMonitoringData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadMonitoringData = async () => {
    try {
      const [healthData, metricsData, logsData] = await Promise.all([
        getHealth(),
        getMetricsSnapshot(),
        getLogs(20)
      ]);
      setHealth(healthData);
      setMetrics(metricsData);
      setLogs(logsData.logs || []);
    } catch (err) {
      console.error('Ошибка загрузки мониторинга:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="container"><div className="loading">Загрузка...</div></div>;
  }

  return (
    <div className="container">
      <h1>Мониторинг системы</h1>

      <div className="monitor-grid">
        <div className="monitor-card">
          <h3>Статус системы</h3>
          <div className="status-indicator">
            <span className={`status-dot ${health?.status === 'healthy' ? 'healthy' : 'unhealthy'}`}></span>
            <span>{health?.status === 'healthy' ? 'Работает' : 'Ошибка'}</span>
          </div>
          <div className="uptime">
            Время работы: {health?.uptime ? Math.floor(health.uptime / 60) : 0} мин
          </div>
        </div>

        {metrics && (
          <>
            <div className="monitor-card">
              <h3>Активные пользователи</h3>
              <div className="metric-value">{metrics.active_users}</div>
            </div>

            <div className="monitor-card">
              <h3>Всего загрузок</h3>
              <div className="metric-value">{metrics.total_uploads}</div>
            </div>

            <div className="monitor-card">
              <h3>Всего скачиваний</h3>
              <div className="metric-value">{metrics.total_downloads}</div>
            </div>
          </>
        )}
      </div>

      <div className="logs-section">
        <h3>Последние логи</h3>
        {logs.length === 0 ? (
          <p className="no-logs">Логи отсутствуют</p>
        ) : (
          <div className="logs-list">
            {logs.map((log, index) => (
              <div key={index} className="log-item">
                <span className="log-timestamp">{new Date(log.timestamp).toLocaleString()}</span>
                <span className={`log-level ${log.level}`}>{log.level}</span>
                <span className="log-message">{log.message}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Monitor;

