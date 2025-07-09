import React from 'react';
import TextInput from './TextInput';
import SendButton from './SendButton';
import './InputArea.css';

function InputArea() {
  return (
    <div className="input-area">
      <TextInput />
      <SendButton />
    </div>
  );
}

export default InputArea;