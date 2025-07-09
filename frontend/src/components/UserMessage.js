import React from 'react';
import './UserMessage.css';

function UserMessage({ content }) {
  return (
    <div className="user-message">
      <p>{content}</p>
    </div>
  );
}

export default UserMessage;