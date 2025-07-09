import React from 'react';
import UserMessage from './UserMessage';
import BotMessage from './BotMessage';
import './MessageItem.css';

function MessageItem({ message }) {
  return (
    <div className="message-item">
      {message.type === 'user' ? (
        <UserMessage content={message.content} />
      ) : (
        <BotMessage content={message.content} />
      )}
    </div>
  );
}

export default MessageItem;