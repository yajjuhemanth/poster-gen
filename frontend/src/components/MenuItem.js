import React from 'react';
import './MenuItem.css';

function MenuItem({ text, icon }) {
  return (
    <div className="menu-item">
      <span>{icon}</span>
      <span>{text}</span>
    </div>
  );
}

export default MenuItem;