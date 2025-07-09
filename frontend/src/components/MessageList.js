import React from 'react';
import MessageItem from './MessageItem';
import './MessageList.css';

function MessageList() {
  // Assuming messages will be passed as props or managed via state
  const messages = []; // Placeholder for messages data

  return (
    <div className="message-list">
      {messages.map((message, index) => (
        <MessageItem key={index} message={message} />
      ))}
    </div>
  );
}

export default MessageList;