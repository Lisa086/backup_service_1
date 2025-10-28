import React, { useState, useEffect } from 'react';
import { getCurrentUser } from '../api';
import './Profile.css';

function Profile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const data = await getCurrentUser();
      setUser(data);
    } catch (err) {
      console.error('Ошибка загрузки профиля:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="container"><div className="loading">Загрузка...</div></div>;
  }

  if (!user) {
    return <div className="container"><div className="error-message">Ошибка загрузки профиля</div></div>;
  }

  return (
    <div className="container">
      <h1>Профиль пользователя</h1>
      <div className="profile-card">
        <div className="profile-avatar">
          <div className="avatar-circle">
            {user.username.charAt(0).toUpperCase()}
          </div>
        </div>
        <div className="profile-info">
          <div className="info-row">
            <span className="info-label">Имя пользователя:</span>
            <span className="info-value">{user.username}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Email:</span>
            <span className="info-value">{user.email}</span>
          </div>
          <div className="info-row">
            <span className="info-label">Статус:</span>
            <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
              {user.is_active ? 'Активен' : 'Неактивен'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Profile;

