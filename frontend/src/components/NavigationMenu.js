import React from 'react';
import MenuItem from './MenuItem';
import './NavigationMenu.css';

function NavigationMenu() {
  const menuItems = [
    { id: 'home', text: 'Home', icon: '🏠' },
    { id: 'generations', text: 'My Generations', icon: '📄' },
    { id: 'aiStyles', text: 'AI Styles', icon: '🎨' },
    { id: 'promptLibrary', text: 'Prompt Library', icon: '📚' },
    { id: 'wallet', text: 'Wallet', icon: '💰' },
    { id: 'newPrompt', text: 'New Prompt', icon: '➕' },
  ];

  return (
    <nav className="navigation-menu">
      {menuItems.map(item => (
        <MenuItem key={item.id} text={item.text} icon={item.icon} />
      ))}
    </nav>
  );
}

export default NavigationMenu;