import React from 'react';
import './TextInput.css';

function TextInput() {
  return (
    <input
      className="text-input"
      type="text"
      placeholder="Type your message..."
    />
  );
}

export default TextInput;