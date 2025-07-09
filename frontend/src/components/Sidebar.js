import React from 'react';
import NavigationMenu from './NavigationMenu';
import WalletBalance from './WalletBalance';
import './Sidebar.css';

function Sidebar() {
  return (
    <aside className="sidebar">
      <NavigationMenu />
      <WalletBalance />
    </aside>
  );
}

export default Sidebar;