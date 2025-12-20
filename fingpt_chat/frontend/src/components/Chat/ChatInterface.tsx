/** Chat interface component */
import React, { useEffect } from 'react';
import { useChat } from '../../hooks/useChat';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { TypingIndicator } from './TypingIndicator';
import './ChatInterface.css';

export const ChatInterface: React.FC = () => {
  const { state, sendMessage, loadHistory } = useChat();

  useEffect(() => {
    // Load history when session exists
    if (state.sessionId) {
      loadHistory(state.sessionId);
    }
  }, [state.sessionId, loadHistory]);

  return (
    <div className="chat-interface">
      <div className="chat-interface__header">Chat</div>
      <div className="chat-interface__messages">
        <MessageList messages={state.messages} />
        {state.isLoading && <TypingIndicator />}
      </div>
      {state.error && (
        <div className="chat-interface__error">{state.error}</div>
      )}
      <ChatInput onSendMessage={sendMessage} disabled={state.isLoading} />
    </div>
  );
};
