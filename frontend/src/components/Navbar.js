import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

function Navbar({ onLogout }) {
  const location = useLocation();

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-logo">
          <Link to="/dashboard"> Backup Service</Link>
        </div>
        <ul className="navbar-menu">
          <li className={location.pathname === '/dashboard' ? 'active' : ''}>
            <Link to="/dashboard"> Файлы</Link>
          </li>
          <li className={location.pathname === '/config' ? 'active' : ''}>
            <Link to="/config"> Настройки</Link>
          </li>
          <li className={location.pathname === '/monitor' ? 'active' : ''}>
            <Link to="/monitor"> Мониторинг</Link>
          </li>
          <li className={location.pathname === '/profile' ? 'active' : ''}>
            <Link to="/profile"> Профиль</Link>
          </li>
          <li>
            <button onClick={onLogout} className="logout-btn">Выход</button>
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default Navbar;

