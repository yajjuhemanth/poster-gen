import React from 'react';
import PromptItem from './PromptItem';
import './PromptLibrary.css';

function PromptLibrary() {
  // Assuming prompts will be passed as props or managed via state
  const prompts = []; // Placeholder for prompts data

  return (
    <div className="prompt-library">
      {prompts.map((prompt, index) => (
        <PromptItem key={index} prompt={prompt} />
      ))}
    </div>
  );
}

export default PromptLibrary;