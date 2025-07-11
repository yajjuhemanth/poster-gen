import React from 'react';
import './PromptItem.css';

function PromptItem({ prompt }) {
  return (
    <div className="prompt-item">
      <p>{prompt.text}</p>
      <button className="use-button">Use</button>
    </div>
  );
}

export default PromptItem;