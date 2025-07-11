import React from 'react';
import './SettingsPanel.css';

function SettingsPanel({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="settings-panel">
      <h2>Settings</h2>
      <button className="close-button" onClick={onClose}>Close</button>
    </div>
  );
}

export default SettingsPanel;