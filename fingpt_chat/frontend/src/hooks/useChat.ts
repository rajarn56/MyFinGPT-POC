/** Chat state management hook */
import { useState, useCallback } from 'react';
import { apiClient } from '../services/api';
import { sessionService } from '../services/session';
import type { ChatState, ChatMessage } from '../types/chat';

export function useChat() {
  const [state, setState] = useState<ChatState>({
    sessionId: sessionService.getSessionId(),
    messages: [],
    isLoading: false,
    error: null,
  });
  
  // Note: Demo data is shown via useResults and useWebSocket hooks
  // This keeps chat messages separate from demo display data

  const sendMessage = useCallback(async (message: string) => {
    try {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      // Ensure we have a session
      let sessionId = state.sessionId;
      if (!sessionId) {
        const session = await apiClient.createSession();
        sessionId = session.session_id;
        sessionService.saveSession(session.session_id, session.expires_at);
        setState((prev) => ({ ...prev, sessionId }));
      }

      // Add user message to UI immediately
      const userMessage: ChatMessage = {
        id: `msg_${Date.now()}_user`,
        session_id: sessionId,
        role: 'user',
        content: message,
        timestamp: new Date().toISOString(),
      };

      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, userMessage],
      }));

      // Send message to API
      const response = await apiClient.sendMessage(sessionId, message);
      
      // WebSocket connection will be handled by useWebSocket hook automatically

      // Add assistant response
      const assistantMessage: ChatMessage = {
        id: response.message_id,
        session_id: response.session_id,
        role: 'assistant',
        content: response.content,
        timestamp: response.timestamp,
        transaction_id: response.transaction_id,
        citations: response.citations,
        visualizations: response.visualizations,
      };

      // Store agent activity in a way that ResultsPanel can access it
      // We'll attach it to the message for now
      (assistantMessage as any).agentActivity = response.agent_activity;

      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isLoading: false,
      }));
    } catch (error: any) {
      let errorMessage = 'Failed to send message';
      
      if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
        errorMessage = 'Cannot connect to server. Please make sure the mock server is running on http://localhost:8000';
      } else if (error.response) {
        errorMessage = error.response.data?.error || error.response.statusText || 'Server error';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
    }
  }, [state.sessionId]);

  const loadHistory = useCallback(async (sessionId: string) => {
    try {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));
      const messages = await apiClient.getHistory(sessionId);
      setState((prev) => ({
        ...prev,
        messages,
        isLoading: false,
      }));
    } catch (error: any) {
      let errorMessage = 'Failed to load history';
      
      if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
        errorMessage = 'Cannot connect to server. Please make sure the mock server is running on http://localhost:8000';
      } else if (error.response) {
        errorMessage = error.response.data?.error || error.response.statusText || 'Server error';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
    }
  }, []);

  return {
    state,
    sendMessage,
    loadHistory,
  };
}

