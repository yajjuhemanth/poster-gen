import React from 'react';
import './BotMessage.css';

function BotMessage({ content }) {
  return (
    <div className="bot-message">
      <p>{content}</p>
    </div>
  );
}

export default BotMessage;