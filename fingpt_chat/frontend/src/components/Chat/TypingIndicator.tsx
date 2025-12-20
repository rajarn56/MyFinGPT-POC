/** Typing indicator component */
import React from 'react';
import './TypingIndicator.css';

export const TypingIndicator: React.FC = () => {
  return (
    <div className="typing-indicator">
      <div className="typing-indicator__dots">
        <span></span>
        <span></span>
        <span></span>
      </div>
      <span className="typing-indicator__text">Agent is thinking...</span>
    </div>
  );
};

