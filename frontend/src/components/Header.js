import React from 'react';
import ThemeToggle from './ThemeToggle';
import NotificationBadge from './NotificationBadge';
import './Header.css';

function Header() {
  return (
    <header className="header">
      <div className="header-logo">
        <h1>KALA AI</h1>
      </div>
      <div className="header-controls">
        <NotificationBadge />
        <ThemeToggle />
      </div>
    </header>
  );
}

export default Header;