/** Message bubble component */
import React from 'react';
import ReactMarkdown from 'react-markdown';
import type { ChatMessage } from '../../types/chat';
import './MessageBubble.css';

interface MessageBubbleProps {
  message: ChatMessage;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const timestamp = new Date(message.timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className={`message-bubble message-bubble--${message.role}`}>
      <div className="message-bubble__content">
        {isUser ? (
          <p className="message-bubble__text">{message.content}</p>
        ) : (
          <div className="message-bubble__markdown">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}
      </div>
      <div className="message-bubble__footer">
        <span className="message-bubble__timestamp">{timestamp}</span>
        {!isUser && message.citations && message.citations.length > 0 && (
          <span className="message-bubble__citations">
            {message.citations.length} citation{message.citations.length !== 1 ? 's' : ''}
          </span>
        )}
      </div>
    </div>
  );
};

