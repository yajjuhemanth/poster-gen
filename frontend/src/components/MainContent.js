import React from 'react';
import ChatWindow from './ChatWindow';
import PromptLibrary from './PromptLibrary';
import './MainContent.css';

function MainContent() {
  return (
    <main className="main-content">
      <ChatWindow />
      <PromptLibrary />
    </main>
  );
}

export default MainContent;