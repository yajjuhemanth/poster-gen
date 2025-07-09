import React from 'react';
import MessageList from './MessageList';
import InputArea from './InputArea';
import './ChatWindow.css';

function ChatWindow() {
  return (
    <div className="chat-window">
      <MessageList />
      <InputArea />
    </div>
  );
}

export default ChatWindow;